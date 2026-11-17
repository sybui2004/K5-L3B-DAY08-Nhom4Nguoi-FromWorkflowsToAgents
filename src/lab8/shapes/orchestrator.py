"""Shape C — orchestrator plus read-only investigators.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Roles:
- Orchestrator (this function): reads the claim view, plans (one MockLLM call),
  builds a `handoff.v1` with `lab8.handoff.make_handoff`, then quotes and is
  the only caller of `durability.issue_refund`.
- Investigator (`lab8.runtime.run_readonly_investigators`): sees only the
  sanitized handoff and the read tools named in it. It has no write registry.

Handoff: `facts` is empty on purpose — the investigator re-reads the order
row itself through principal-scoped tools, so nothing from the parent context
(parent_secret, raw headers, full claim row, ticket text) crosses the boundary.
An LLM summary is not a sanitizer; the allowlist in `make_handoff` is.

Money: the quote is `compute_compensation` on the order row the investigator
read from the DB. The FULL quote goes to `issue_refund`; the host subtracts
earlier refunds on the same order (T13, T14).

Trace: the sanitized handoff and a summary of investigator results. Never the
parent context or the ticket.

This file is self-contained on purpose: the grader copies only the three shape
files from the group repo, so it must import only official lab8 modules.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE = "orchestrator"
INVESTIGATOR_TOOLS = ["lookup_order", "lookup_policy", "lookup_refund_history", "compute_compensation"]


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
        complete(budget, seed=seed, purpose="draft", prompt=f"status={status} amount={proposal}")
        trace.add("decision", {"status": status, "proposal_amount": int(proposal), "reason": reason})
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

    # Orchestrator reads the claim view (allowlisted columns) to route the claim.
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    trace.add("claim", {"claim_id": claim_id, "found": claim["found"], "has_order_id": bool(claim.get("order_id"))})
    if not claim["found"]:
        return done("failed", 0, "unknown_claim")
    if not claim["order_id"]:
        return done("needs_info", 0, "missing_order_id")

    complete(budget, seed=seed, purpose="plan", prompt=f"claim={claim_id} task=check_applicable_policy")
    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="check_applicable_policy",
        facts={},
        allowed_tools=list(INVESTIGATOR_TOOLS),
    )
    trace.add("handoff", safe_dump(handoff))

    investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim["principal_id"])
    tools = investigated["tools"]
    order_view = tools.get("lookup_order") or {}
    trace.add("investigator", _investigator_event(tools))
    if not order_view.get("visible"):
        return done("escalated", 0, order_view.get("reason"))

    quote = tools.get("compute_compensation")
    if not quote:
        return done("failed", 0, "missing_quote")
    proposal = int(quote["amount_vnd"])
    trace.add("quote", safe_dump(quote))
    if proposal <= 0:
        return done("denied", 0, quote.get("reason"))

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add("host", {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]})

    if outcome["ok"]:
        return done("resolved", proposal, None)
    return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])


def _investigator_event(tools: dict[str, Any]) -> dict[str, Any]:
    order_view = tools.get("lookup_order") or {}
    event: dict[str, Any] = {"order_visible": order_view.get("visible"), "order_reason": order_view.get("reason")}
    if order_view.get("visible"):
        event["order"] = safe_dump(order_view["order"])
    history = tools.get("lookup_refund_history") or {}
    if history.get("visible"):
        event["refund_history"] = {"refund_count": history["refund_count"], "refunded_vnd": history["refunded_vnd"]}
    event["policy_count"] = len((tools.get("lookup_policy") or {}).get("policies") or [])
    return event
