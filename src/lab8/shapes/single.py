"""Shape B — one ReAct agent.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

`lab8.runtime.run_react` drives the loop (max 8 steps). Each `decide` call is
one MockLLM call (counted in the Budget) and picks the next READ tool. The
agent never calls `issue_refund`: `dispatch` rejects write tools anyway.

Boundary:
- The agent chooses which read tool to call and when to stop.
- Code owns the money: the proposal is the `compute_compensation` result
  computed from the order row returned by `lookup_order`, never a number the
  agent writes into its final answer and never a number from the ticket.
- After the loop, the shape (not the agent) calls `durability.issue_refund`
  with the FULL quote and `crash_at`. The host checks approval, the per-order
  cap and idempotency.

`run_react` only passes the last tool result back to `decide`, so `decide`
keeps its own memory of what it has seen.

This file is self-contained on purpose: the grader copies only the three shape
files from the group repo, so it must import only official lab8 modules.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.trace import Trace

SHAPE = "single"
MAX_STEPS = 8


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

    agent = _Agent(claim_id, seed=seed, budget=budget, trace=trace)
    loop = run_react(conn, budget, observation={"claim": {"claim_id": claim_id}}, decide=agent.decide, max_steps=MAX_STEPS)
    trace.add("react_stop", {"stopped": loop["stopped"], "steps": agent.steps})

    if loop["stopped"] != "final":
        return done("failed", 0, "step_cap")

    final = loop["final"]
    status = final.get("status")
    if status in ("failed", "needs_info", "escalated"):
        return done(status, 0, final.get("reason"))
    if status != "propose" or agent.quote is None:
        return done("failed", 0, "invalid_final")

    # Code owns the amount: take it from the tool result, ignore anything else in `final`.
    proposal = int(agent.quote["amount_vnd"])
    if proposal <= 0:
        return done("denied", 0, agent.quote.get("reason"))

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


class _Agent:
    """The ReAct policy. One MockLLM call per decision; only read tools."""

    def __init__(self, claim_id: str, *, seed: int, budget: Budget, trace: Trace) -> None:
        self.claim_id = claim_id
        self.seed = seed
        self.budget = budget
        self.trace = trace
        self.steps = 0
        self.claim: dict[str, Any] | None = None
        self.order: dict[str, Any] | None = None
        self.quote: dict[str, Any] | None = None

    def decide(self, seen: dict[str, Any]) -> dict[str, Any]:
        self.steps += 1
        last_tool = seen.get("last_tool")
        # Prompt carries only the step and tool name: ticket text is data, not instructions.
        complete(self.budget, seed=self.seed, purpose="react", prompt=f"step={self.steps} last_tool={last_tool}")
        if last_tool is not None:
            self._remember(last_tool, seen.get("last_result") or {})

        if self.claim is None:
            return self._call("get_claim_view", {"claim_id": self.claim_id})
        if not self.claim.get("found"):
            return self._final({"status": "failed", "reason": "unknown_claim"})
        if not self.claim.get("order_id"):
            return self._final({"status": "needs_info", "reason": "missing_order_id"})
        if self.order is None:
            return self._call(
                "lookup_order",
                {"order_id": self.claim["order_id"], "principal_id": self.claim["principal_id"]},
            )
        if not self.order.get("visible"):
            return self._final({"status": "escalated", "reason": self.order.get("reason")})
        if self.quote is None:
            return self._call("compute_compensation", {"order": self.order["order"]})
        return self._final({"status": "propose"})

    def _remember(self, tool: str, result: dict[str, Any]) -> None:
        if tool == "get_claim_view":
            self.claim = result
            self.trace.add("tool", {"name": tool, "found": result.get("found"), "has_order_id": bool(result.get("order_id"))})
        elif tool == "lookup_order":
            self.order = result
            event: dict[str, Any] = {"name": tool, "visible": result.get("visible"), "reason": result.get("reason")}
            if result.get("visible"):
                event["order"] = safe_dump(result["order"])
            self.trace.add("tool", event)
        elif tool == "compute_compensation":
            self.quote = result
            self.trace.add("tool", {"name": tool, **safe_dump(result)})

    def _call(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        self.trace.add("react_action", {"step": self.steps, "tool": name})
        return {"tool": name, "args": args}

    def _final(self, final: dict[str, Any]) -> dict[str, Any]:
        self.trace.add("react_action", {"step": self.steps, "final": final.get("status")})
        return {"final": final}
