"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace


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


def _run(
    conn: sqlite3.Connection,
    claim_id: str,
    *,
    seed: int,
    crash_at: str | None,
) -> RunResult:
    budget = Budget()
    run_id = make_run_id("single", claim_id, seed)
    trace = Trace(run_id)

    budget.add_tool(tool_cost())
    claim_view = get_claim_view(conn, claim_id)
    if not claim_view.get("found"):
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="unknown_claim",
        )

    trace.add(
        "claim_view",
        {"claim_id": claim_view.get("claim_id"), "order_id": claim_view.get("order_id")},
    )

    if not claim_view.get("order_id"):
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        trace.add("decision", {"status": "needs_info"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="needs_info",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="missing_order_id",
        )

    order_info: dict[str, Any] = {}

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        last_tool = seen.get("last_tool")
        if last_tool is None:
            complete(budget, seed=seed, purpose="decide", prompt=f"lookup_order {claim_view['order_id']}")
            return {
                "tool": "lookup_order",
                "args": {
                    "order_id": claim_view["order_id"],
                    "principal_id": claim_view["principal_id"],
                },
            }
        if last_tool == "lookup_order":
            order_view = seen.get("last_result") or {}
            if not order_view.get("visible"):
                return {"final": {"status": "escalated", "reason": order_view.get("reason")}}
            order_info["order"] = order_view["order"]
            complete(budget, seed=seed, purpose="decide", prompt=f"compute_compensation {claim_view['order_id']}")
            return {
                "tool": "compute_compensation",
                "args": {"order": order_view["order"]},
            }
        if last_tool == "compute_compensation":
            quote_payload = seen.get("last_result") or {}
            complete(budget, seed=seed, purpose="decide", prompt=f"quote={quote_payload.get('amount_vnd')}")
            return {"final": {"status": "quoted", "quote": quote_payload}}
        return {"final": {"status": "failed", "reason": "unexpected_step"}}

    outcome = run_react(
        conn,
        budget,
        observation={"claim": claim_view},
        decide=decide,
        max_steps=8,
    )
    trace.add("react", {"stopped": outcome["stopped"]})

    if outcome["stopped"] == "step_cap":
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="step_cap",
        )

    final = outcome["final"]
    if final.get("status") == "escalated":
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        trace.add("decision", {"status": "escalated"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="escalated",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final.get("reason"),
        )

    if final.get("status") != "quoted":
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final.get("reason", "unknown_error"),
        )

    quote_payload = final["quote"]
    proposal = int(quote_payload.get("amount_vnd", 0))
    trace.add("quote", quote_payload)

    if proposal <= 0:
        complete(budget, seed=seed, purpose="draft", prompt="proposal=0")
        trace.add("decision", {"status": "denied"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=quote_payload.get("reason"),
        )

    try:
        refund_outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
    if not refund_outcome["ok"]:
        status = "failed" if refund_outcome.get("conflict") else "denied"
        trace.add(
            "refund_decision",
            {"ok": False, "status": status, "reason": refund_outcome.get("reason")},
        )
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=refund_outcome.get("reason"),
        )

    trace.add("refund_decision", {"ok": True, "status": "resolved"})
    return finish(
        conn,
        shape="single",
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=None,
    )
