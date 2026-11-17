"""Orchestrator: handoff stays inside the allowlist, investigators get read tools only."""

from __future__ import annotations

import json

import pytest

from lab8.handoff import ALLOWED_FIELDS, READONLY_TOOLS
from lab8.shapes import orchestrator
from tests.conftest import BY_ID


def _handoffs(result):
    with open(result.trace_path, encoding="utf-8") as fh:
        body = json.load(fh)
    return [e["payload"] for e in body["events"] if e["kind"] == "handoff"]


@pytest.mark.parametrize("claim_id", ["C-001", "C-013", "C-014"])
def test_orchestrator_handoff_is_allowlisted_and_read_only(public_db, claim_id):
    result = orchestrator.run_claim(claim_id, seed=11, store_path=str(public_db))
    handoffs = _handoffs(result)
    assert len(handoffs) == 1
    handoff = handoffs[0]
    assert set(handoff) <= ALLOWED_FIELDS
    assert handoff["contract_version"] == "handoff.v1"
    assert set(handoff["allowed_tools"]) <= READONLY_TOOLS
    assert handoff["facts"] == {}
    blob = json.dumps(handoff, ensure_ascii=False)
    assert BY_ID[claim_id]["parent_secret"] not in blob
    assert BY_ID[claim_id]["ticket"] not in blob


def test_orchestrator_passes_full_quote_on_partial_refund(public_db):
    # T14: order already refunded 30000 for shipping; damage entitlement 150000 -> ledger 120000.
    result = orchestrator.run_claim("C-014", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    assert result.proposal_amount == 150000
    assert [e["amount_vnd"] for e in result.refund_effects] == [120000]
