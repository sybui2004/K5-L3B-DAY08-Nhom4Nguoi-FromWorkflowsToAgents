"""All three group shapes: trace contract v1 on every path, no secret / ticket text leaks."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from lab8.db import init_store
from lab8.shapes import SHAPES
from tests.conftest import CLAIMS, WORLD

GROUP_SHAPES = ["workflow", "single", "orchestrator"]


@pytest.mark.parametrize("shape", GROUP_SHAPES)
@pytest.mark.parametrize("claim", CLAIMS, ids=lambda row: row["claim_id"])
def test_trace_contract_and_no_leak(tmp_path, shape, claim):
    store = tmp_path / f"{shape}-{claim['claim_id']}.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    started = time.time()
    result = SHAPES[shape](claim["claim_id"], seed=11, store_path=str(store))

    path = Path(result.trace_path)
    assert path.exists() and path.stat().st_mtime >= started - 1
    body = json.loads(path.read_text(encoding="utf-8"))
    assert body["run_id"] == result.run_id
    assert isinstance(body["events"], list) and body["events"]

    blob = path.read_text(encoding="utf-8") + json.dumps(result.as_dict(), ensure_ascii=False)
    for token in claim["expected"]["forbid_substrings"]:
        assert token not in blob
    assert "CANARY_SECRET_" not in blob
    assert claim["ticket"] not in blob


@pytest.mark.parametrize("shape", GROUP_SHAPES)
def test_unknown_claim_still_writes_trace(public_db, shape):
    result = SHAPES[shape]("C-404", seed=11, store_path=str(public_db))
    assert result.status == "failed"
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert body["run_id"] == result.run_id
