"""Bridge between the Streamlit pages and lab8 for running claims.

Importing this module bootstraps sys.path and the working directory to the lab
root (<repo>/src, skeleton layout), so lab8 writes traces to src/traces and reads
src/reports exactly like the CLI and benchmark.
Import it before any other module that touches lab8.

Secrets never leave this module: load_public_claims() drops parent_secret and
raw_headers, and grading reasons that would echo a forbidden token are masked.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

# All lab code, data, reports and traces live under <repo>/src since the skeleton layout.
LAB_ROOT = Path(__file__).resolve().parent.parent.parent / "src"
if str(LAB_ROOT) not in sys.path:
    sys.path.insert(0, str(LAB_ROOT))
os.chdir(LAB_ROOT)

from lab8.app import PUBLIC_CLAIMS, prepare_store, run_shape  # noqa: E402
from lab8.db import connect, load_jsonl  # noqa: E402
from lab8.durability import InjectedCrash  # noqa: E402
from lab8.metrics import trial_pass  # noqa: E402
from lab8.schemas import make_run_id  # noqa: E402

from services.live_call_recorder import record_calls  # noqa: E402 - needs lab8 on sys.path

PUBLIC_FIELDS = ("claim_id", "matrix_id", "principal_id", "order_id", "ticket")
_RAW_CLAIMS = load_jsonl(PUBLIC_CLAIMS)
_LABELS = {claim["claim_id"]: claim.get("expected") or {} for claim in _RAW_CLAIMS}


def mask_token(token: str) -> str:
    return f"{token[:6]}***" if len(token) > 6 else "***"


def forbidden_tokens(claim_id: str | None = None) -> list[str]:
    """Strings the grader forbids in artifacts (canaries, phones, addresses)."""
    labels = [_LABELS.get(claim_id, {})] if claim_id else list(_LABELS.values())
    return sorted({token for label in labels for token in label.get("forbid_substrings") or [] if token})


def load_public_claims() -> list[dict[str, Any]]:
    """Claims safe to show on a projector: no parent_secret, no raw_headers."""
    rows = []
    for claim in _RAW_CLAIMS:
        view = {key: claim.get(key) for key in PUBLIC_FIELDS}
        expected = dict(claim.get("expected") or {})
        expected.pop("forbid_substrings", None)
        view["expected"] = expected
        rows.append(view)
    return rows


def new_store_path() -> Path:
    """Fresh SQLite path per run so ledgers never accumulate across demos."""
    return Path(tempfile.mkdtemp(prefix="lab8-demo-")) / "store.sqlite"


def run_claim_once(
    shape: str,
    claim_id: str,
    seed: int,
    *,
    crash_at: str | None = None,
    store_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run one claim and collect everything the UI shows. Never raises.

    Pass store_path to reuse a DB (retry after crash); omit it for a fresh world.
    """
    store = Path(store_path) if store_path else new_store_path()
    if not store.exists():
        prepare_store(store)
    started = time.time()
    outcome: dict[str, Any] = {
        "shape": shape,
        "claim_id": claim_id,
        "seed": seed,
        "crash_at": crash_at,
        "store_path": str(store),
        "result": None,
        "crashed": None,
        "error": None,
        "calls": [],
    }
    # Live call log: every tool / model / host / trace event in order, secrets scrubbed.
    with record_calls(forbidden_tokens(claim_id)) as calls:
        try:
            result = run_shape(shape, claim_id, seed=seed, store_path=str(store), crash_at=crash_at)
            outcome["result"] = result.as_dict()
        except InjectedCrash as exc:
            outcome["crashed"] = str(exc) or crash_at or "crash"
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - a demo must not die on a shape bug
            outcome["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
    outcome["calls"] = calls
    result_dict = outcome["result"]
    outcome["not_implemented"] = bool(result_dict and result_dict.get("error_reason") == "not_implemented")
    trace_path = result_dict.get("trace_path") if result_dict else None
    outcome["trace"] = read_trace(trace_path, make_run_id(shape, claim_id, seed), started)
    outcome["store"] = read_store_state(store, claim_id)
    outcome["verdict"] = grade(result_dict, claim_id, store, started)
    return outcome


def grade(result: dict[str, Any] | None, claim_id: str, store: Path, started: float) -> dict[str, Any]:
    """Reuse the official trial_pass so the demo verdict matches the benchmark."""
    if result is None:
        return {"passed": None, "reason": "no_result"}
    expected = _LABELS.get(claim_id)
    if not expected:
        return {"passed": None, "reason": "no_label"}
    conn = connect(store)
    try:
        passed, reason = trial_pass(result, expected, conn, started_at=started)
    except Exception as exc:  # noqa: BLE001 - malformed result fields
        passed, reason = False, f"grade_error:{type(exc).__name__}"
    finally:
        conn.close()
    if reason.startswith("forbidden_substring:"):
        reason = f"forbidden_substring:{mask_token(reason.split(':', 1)[1])}"
    return {"passed": passed, "reason": reason}


def read_trace(trace_path: str | None, run_id: str, started: float) -> dict[str, Any]:
    """Load the trace file. A crashed run has no RunResult, so fall back to run_id."""
    path = Path(trace_path) if trace_path else Path("traces") / f"{run_id}.json"
    if not path.is_absolute():
        path = LAB_ROOT / path
    empty = {"path": str(path), "events": [], "steps": 0, "found": False, "stale": False}
    if not path.is_file():
        return empty
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return empty
    try:
        shown = str(path.relative_to(LAB_ROOT))
    except ValueError:
        shown = str(path)
    return {
        "path": shown,
        "events": body.get("events") or [],
        "steps": body.get("steps", len(body.get("events") or [])),
        "found": True,
        "stale": path.stat().st_mtime < started - 1.0,
    }


def read_store_state(store: Path, claim_id: str) -> dict[str, Any]:
    """Ledger, audit, and checkpoint rows straight from SQLite (the source of truth)."""
    conn = connect(store)
    try:
        ledger = [
            dict(row)
            for row in conn.execute(
                "SELECT claim_id, order_id, amount_vnd, status FROM refund_ledger ORDER BY rowid"
            )
        ]
        audits = [
            {"event_type": row["event_type"], "details": row["details_json"]}
            for row in conn.execute(
                "SELECT event_type, details_json FROM audit_events WHERE claim_id = ? ORDER BY rowid",
                (claim_id,),
            )
        ]
        checkpoints = [
            row["step"]
            for row in conn.execute("SELECT step FROM checkpoints WHERE claim_id = ?", (claim_id,))
        ]
    finally:
        conn.close()
    return {
        "ledger": ledger,
        "own_ledger": [row for row in ledger if row["claim_id"] == claim_id],
        "audits": audits,
        "committed_audits": sum(1 for row in audits if row["event_type"] == "refund_committed"),
        "policy_denied": any(row["event_type"] == "policy_denied" for row in audits),
        "checkpoints": checkpoints,
    }


def load_report(name: str) -> dict[str, Any] | None:
    """Read src/reports/<name> if the team already generated it, else None."""
    path = LAB_ROOT / "reports" / name
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
