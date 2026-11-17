"""Bonus B3 — swarm + code verifier before the write.

Signature (same as every shape):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

The swarm flow is kept as in `lab8/shapes/swarm_reference.py`, including its
REFERENCE_WEAKNESS (on seed % 5 == 0 it trusts the delay written in the ticket).
`swarm_reference.py` is not modified; its flow is mirrored here so one step can
be inserted between "quote" and "issue_refund":

    verifier: re-read the order through the principal-scoped `lookup_order`
    (an independent read, not the investigator's copy), compare every fact the
    quote used (delay_days, status, damage_verified, shipping_fee_vnd,
    paid_vnd) with the structured row. On any mismatch: trace one
    `verifier_override` event, re-quote from the structured row with
    `compute_compensation`. At most one correction round; if the facts still
    disagree after it, fail closed (`failed`, no write).

The verifier is code, not a model call. Money still comes from
`compute_compensation`; the host still checks approval, cap, and idempotency.

Run next to the four shapes (from `src/`):

    python -m lab8.benchmark --shapes workflow,swarm,swarm_verified \
        --extra-shape swarm_verified=bonus.swarm_verified:run_claim \
        --seeds 11,22,33,44,55 --out reports/bonus_benchmark_public.json
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete, parse_delay_days
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, lookup_order, tool_cost
from lab8.trace import Trace

SHAPE = "swarm_verified"
VERIFIED_FIELDS = ("delay_days", "status", "damage_verified", "shipping_fee_vnd", "paid_vnd")
MAX_CORRECTIONS = 1


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    def done(status: str, proposal: int, reason: str | None) -> RunResult:
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    # ---- swarm flow (mirrors swarm_reference) ----
    budget.add_tool(tool_cost())
    claim_row = conn.execute(
        "SELECT claim_id, principal_id, order_id, ticket FROM claims WHERE claim_id = ?",
        (claim_id,),
    ).fetchone()
    if claim_row is None:
        trace.add("error", {"reason": "unknown_claim"})
        return done("failed", 0, "unknown_claim")

    ticket = claim_row["ticket"]
    complete(budget, seed=seed, purpose="peer", prompt=ticket)
    parsed_delay = parse_delay_days(ticket)
    complete(budget, seed=seed, purpose="parse", prompt=ticket)

    if not claim_row["order_id"]:
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        trace.add("decision", {"status": "needs_info"})
        return done("needs_info", 0, "missing_order_id")

    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="check_applicable_policy",
        facts={},
        allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"],
    )
    trace.add("handoff", safe_dump(handoff))
    investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim_row["principal_id"])
    order_view = investigated["tools"].get("lookup_order", {})
    trace.add("investigator", {"lookup_order": order_view, "policy_count": len((investigated["tools"].get("lookup_policy") or {}).get("policies") or [])})
    if not order_view.get("visible"):
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return done("escalated", 0, order_view.get("reason"))

    order = dict(order_view["order"])
    # Swarm weakness kept on purpose: the verifier must catch it, not a patched swarm.
    if parsed_delay is not None and parsed_delay != int(order["delay_days"]) and seed % 5 == 0:
        order["delay_days"] = parsed_delay
        trace.add("model_override", {"delay_days": parsed_delay})

    quote_payload = investigated["tools"]["compute_compensation"]
    if order["delay_days"] != order_view["order"]["delay_days"]:
        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, order)
    trace.add("quote", safe_dump(quote_payload))

    # ---- verifier (code) ----
    verified = _verify(conn, budget, trace, claim_row["principal_id"], claim_row["order_id"], order, quote_payload)
    if verified is None:
        return done("failed", 0, "verifier_unresolved")
    quote_payload = verified

    proposal = int(quote_payload["amount_vnd"])
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
    if proposal <= 0:
        return done("denied", 0, quote_payload.get("reason"))

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
    return done("resolved", proposal, None)


def _verify(
    conn: sqlite3.Connection,
    budget: Budget,
    trace: Trace,
    principal_id: str,
    order_id: str,
    used_order: dict[str, Any],
    quote_payload: dict[str, Any],
) -> dict[str, Any] | None:
    """Return a quote whose inputs match the structured order, or None to fail closed."""
    budget.add_tool(tool_cost())
    structured_view = lookup_order(conn, order_id, principal_id)
    if not structured_view.get("visible"):
        trace.add("verifier", {"ok": False, "reason": structured_view.get("reason")})
        return None
    structured = structured_view["order"]

    for round_no in range(MAX_CORRECTIONS + 1):
        mismatches = _diff(used_order, structured)
        if not mismatches:
            trace.add("verifier", {"ok": True, "round": round_no})
            return quote_payload
        if round_no == MAX_CORRECTIONS:
            break
        trace.add("verifier_override", {"round": round_no + 1, "mismatches": mismatches})
        used_order = dict(structured)
        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, used_order)
        trace.add("quote", safe_dump(quote_payload))
    trace.add("verifier", {"ok": False, "reason": "unresolved_after_correction"})
    return None


def _diff(used: dict[str, Any], structured: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for field in VERIFIED_FIELDS:
        if used.get(field) != structured.get(field):
            out[field] = {"used": used.get(field), "structured": structured.get(field)}
    return out
