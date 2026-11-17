"""Shape A — deterministic workflow.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Fixed Python steps. Money stays in code (`lab8.tools.compute_compensation`).
The ticket text is user data: it is never parsed for numbers, never obeyed,
and never written to the trace. MockLLM only drafts the reply text.

Steps:
1. Read the claim through `get_claim_view` (allowlisted columns, no secret).
2. Unknown claim -> `failed`. Missing order_id -> `needs_info`.
3. `lookup_order` (principal-scoped). Not visible -> `escalated`.
4. Quote from the order row with `compute_compensation`.
5. Quote 0 -> `denied`, no host call.
6. Quote > 0 -> `durability.issue_refund(conn, claim_id, full_quote, crash_at=...)`.
   The host checks approval, the per-order cap and idempotency.
   ok -> `resolved`; conflict -> `failed`; otherwise -> `denied` (host wrote
   `policy_denied`). `proposal_amount` is always the full quote.

This file is self-contained on purpose: the grader copies only the three shape
files from the group repo, so it must import only official lab8 modules.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace

SHAPE = "workflow"


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

    # 1. Claim view: only claim_id, principal_id, order_id, ticket. Ticket stays out of the trace.
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    trace.add("claim", {"claim_id": claim_id, "found": claim["found"], "has_order_id": bool(claim.get("order_id"))})
    if not claim["found"]:
        return done("failed", 0, "unknown_claim")

    # 2. No order id on the claim row -> ask. Never pull an order id out of the ticket text.
    if not claim["order_id"]:
        return done("needs_info", 0, "missing_order_id")

    # 3. Principal-scoped order lookup. Returns allowlisted fields only (no phone, address, item, note).
    budget.add_tool(tool_cost())
    order_view = lookup_order(conn, claim["order_id"], claim["principal_id"])
    trace.add("order", _order_event(order_view))
    if not order_view["visible"]:
        return done("escalated", 0, order_view["reason"])

    # 4. Quote from the structured order row, current policies only.
    budget.add_tool(tool_cost())
    quote = compute_compensation(conn, order_view["order"])
    proposal = int(quote["amount_vnd"])
    trace.add("quote", safe_dump(quote))

    # 5. Nothing owed -> deny without touching the host.
    if proposal <= 0:
        return done("denied", 0, quote.get("reason"))

    # 6. Host gate. Full quote; host subtracts earlier refunds of the same order.
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


def _order_event(order_view: dict[str, Any]) -> dict[str, Any]:
    event: dict[str, Any] = {"visible": order_view["visible"], "reason": order_view["reason"]}
    if order_view["visible"]:
        event["order"] = safe_dump(order_view["order"])
    return event
