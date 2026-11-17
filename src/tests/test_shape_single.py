"""Single ReAct agent: bounded loop, read tools only, money from the tool result."""

from __future__ import annotations

import json

from lab8.handoff import READONLY_TOOLS
from lab8.shapes import single
from lab8.shapes.single import MAX_STEPS


def _events(result):
    with open(result.trace_path, encoding="utf-8") as fh:
        return json.load(fh)["events"]


def test_single_stays_within_step_cap_and_uses_read_tools_only(public_db):
    result = single.run_claim("C-001", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    actions = [e["payload"] for e in _events(result) if e["kind"] == "react_action"]
    assert 0 < len(actions) <= MAX_STEPS
    tools = {a["tool"] for a in actions if "tool" in a}
    assert tools <= READONLY_TOOLS
    assert "issue_refund" not in tools


def test_single_counts_one_model_call_per_decision(public_db):
    result = single.run_claim("C-001", seed=11, store_path=str(public_db))
    actions = [e for e in _events(result) if e["kind"] == "react_action"]
    # one MockLLM call per decide() plus one draft call
    assert result.model_calls == len(actions) + 1
    assert result.cost_estimate > 0


def test_single_needs_info_stops_early_without_order_lookup(public_db):
    # Find a public claim without an order id (T04-style needs_info).
    from tests.conftest import CLAIMS

    claim_id = next(row["claim_id"] for row in CLAIMS if not row["order_id"])
    result = single.run_claim(claim_id, seed=11, store_path=str(public_db))
    assert result.status == "needs_info"
    tools = {e["payload"].get("tool") for e in _events(result) if e["kind"] == "react_action"}
    assert "lookup_order" not in tools
