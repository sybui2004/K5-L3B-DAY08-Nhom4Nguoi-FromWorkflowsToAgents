"""Bonus B3: swarm_verified catches the swarm's ticket-trust weakness before the write."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from bonus.swarm_verified import run_claim as swarm_verified
from lab8.config_loader import repo_path
from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.durability import InjectedCrash
from lab8.metrics import trial_pass
from lab8.shapes.swarm_reference import run_claim as swarm
from tests.conftest import BY_ID, CLAIMS, WORLD

BONUS_CLAIMS = load_jsonl(repo_path("bonus", "cases.jsonl"))
BONUS_WORLD = load_json(repo_path("bonus", "world.json"))
BONUS_BY_ID = {row["claim_id"]: row for row in BONUS_CLAIMS}
SEEDS = [11, 22, 33, 44, 55]


def _events(result):
    return json.loads(Path(result.trace_path).read_text(encoding="utf-8"))["events"]


def _grade(fn, claim_id, seed, store, world, claims, expected):
    init_store(store, world, claims).close()
    started = time.time()
    result = fn(claim_id, seed=seed, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), expected, conn, started_at=started)
    finally:
        conn.close()
    return result, passed, reason


def test_verifier_fixes_swarm_t02_seed_55(tmp_path):
    expected = BY_ID["C-002"]["expected"]
    _, swarm_passed, _ = _grade(swarm, "C-002", 55, tmp_path / "s.sqlite", WORLD, CLAIMS, expected)
    result, passed, reason = _grade(swarm_verified, "C-002", 55, tmp_path / "v.sqlite", WORLD, CLAIMS, expected)
    assert not swarm_passed, "baseline swarm should show its weakness here"
    assert passed, reason
    overrides = [e["payload"] for e in _events(result) if e["kind"] == "verifier_override"]
    assert len(overrides) == 1
    assert overrides[0]["mismatches"]["delay_days"] == {"used": 5, "structured": 2}


@pytest.mark.parametrize("claim", BONUS_CLAIMS, ids=lambda row: row["claim_id"])
@pytest.mark.parametrize("seed", SEEDS)
def test_swarm_verified_passes_hand_labelled_adversarial_cases(tmp_path, claim, seed):
    _, passed, reason = _grade(
        swarm_verified, claim["claim_id"], seed, tmp_path / "b.sqlite", BONUS_WORLD, BONUS_CLAIMS, claim["expected"]
    )
    assert passed, reason


@pytest.mark.parametrize("seed", [11, 22, 33, 44])
def test_verifier_silent_when_facts_agree(tmp_path, seed):
    # Off seed 55 the swarm never rewrites facts, so the verifier must not intervene.
    for claim_id in ("C-001", "C-002", "C-014"):
        store = tmp_path / f"{claim_id}.sqlite"
        init_store(store, WORLD, CLAIMS).close()
        result = swarm_verified(claim_id, seed=seed, store_path=str(store))
        assert not [e for e in _events(result) if e["kind"] == "verifier_override"]


def test_swarm_verified_crash_then_resume_keeps_one_refund(tmp_path):
    store = tmp_path / "crash.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    with pytest.raises(InjectedCrash):
        swarm_verified("C-012", seed=11, store_path=str(store), crash_at="after_effect_before_checkpoint")
    started = time.time()
    result = swarm_verified("C-012", seed=11, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID["C-012"]["expected"], conn, started_at=started)
        count = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'").fetchone()["n"]
    finally:
        conn.close()
    assert passed, reason
    assert count == 1


def test_adversarial_labels_are_consistent_with_ledger_fields():
    # Hand labels: resolved <=> exactly one refund and one committed audit; denied with quote 0 => nothing written.
    for claim in BONUS_CLAIMS:
        exp = claim["expected"]
        if exp["status"] == "resolved":
            assert exp["refund_count"] == 1 and exp["audit_refund_committed"] == 1
            assert exp["refund_vnd"] == exp["proposal_amount"]
        else:
            assert exp["refund_count"] == 0 and exp["refund_vnd"] == 0 and exp["proposal_amount"] == 0
