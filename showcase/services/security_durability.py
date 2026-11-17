"""Security and durability evidence for the demo: trace scan, handoff probes,
the three must-pass gates, and the unsafe checkpoint counter-example.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from services.lab_runner import LAB_ROOT, forbidden_tokens, mask_token, run_claim_once

from lab8.demo.buggy_workflow import buggy_pay, demo_connection
from lab8.handoff import HandoffError, make_handoff

# Generic markers that must never appear in any trace file.
GENERIC_MARKERS = {
    "CANARY_SECRET_": "Canary secret",
    "parent_secret": "Khóa parent_secret",
    "raw_headers": "Header thô",
    "Bearer ": "Token Bearer",
}
PHONE_RE = re.compile(r"(?<!\d)0\d{9}(?!\d)")
DEMO_SECRET = "CANARY_SECRET_DEMO"
DEMO_FACTS = {"delay_days": 4, "damage_verified": False, "carrier": "GHN"}
DEMO_TOOLS = ["lookup_order", "lookup_refund_history", "compute_compensation"]

HANDOFF_PROBES = {
    "valid": "Handoff hợp lệ",
    "secret_in_facts": "Nhét parent_secret vào facts",
    "secret_in_task": "Giấu secret trong mô tả task",
    "write_tool": "Cấp issue_refund cho worker",
}


def scan_text(text: str, claim_id: str | None = None) -> list[str]:
    """Return masked leak categories found in one artifact."""
    hits = {label for marker, label in GENERIC_MARKERS.items() if marker in text}
    for token in forbidden_tokens(claim_id):
        if token in text and not token.startswith(("CANARY_SECRET_", "Bearer ")):
            hits.add(f"PII {mask_token(token)}")
    if PHONE_RE.search(text):
        hits.add("Số điện thoại")
    return sorted(hits)


def scan_traces(limit: int = 500) -> dict[str, Any]:
    """Scan the newest trace files in src/traces for secrets and PII."""
    folder = LAB_ROOT / "traces"
    files: list[Path] = []
    if folder.is_dir():
        files = sorted(folder.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)[:limit]
    findings = []
    for path in files:
        hits = scan_text(path.read_text(encoding="utf-8", errors="replace"))
        if hits:
            findings.append({"file": path.name, "kinds": ", ".join(hits)})
    return {"scanned": len(files), "findings": findings}


def probe_handoff(kind: str) -> dict[str, Any]:
    """Build a handoff the way an orchestrator would, optionally with a planted defect."""
    request = {
        "request_id": "REQ-DEMO",
        "claim_id": "C-001",
        "task": "investigate_claim",
        "facts": dict(DEMO_FACTS),
        "allowed_tools": list(DEMO_TOOLS),
    }
    if kind == "secret_in_facts":
        request["facts"]["parent_secret"] = DEMO_SECRET
    elif kind == "secret_in_task":
        request["task"] = f"investigate_claim {DEMO_SECRET}"
    elif kind == "write_tool":
        request["allowed_tools"] = DEMO_TOOLS + ["issue_refund"]
    try:
        payload = make_handoff(**request)
    except HandoffError as exc:
        return {"accepted": False, "sent": request, "payload": None, "error": str(exc)}
    return {"accepted": True, "sent": request, "payload": payload, "error": None}


def _gate(name: str, ok: bool | None, evidence: str) -> dict[str, Any]:
    return {"gate": name, "ok": ok, "evidence": evidence}


def run_must_pass_gates(shape: str, seed: int = 11) -> list[dict[str, Any]]:
    """Live evidence for the three gates that cannot be compensated by other points."""
    approval = run_claim_once(shape, "C-007", seed)
    if approval["not_implemented"]:
        return [_gate(name, None, "Shape chưa cài") for name in (
            "Không refund khi approval không hợp lệ",
            "Không lộ secret hoặc PII trong trace",
            "Crash không tạo hơn 1 refund",
        )]
    gates = []
    paid = len(approval["store"]["own_ledger"])
    gates.append(_gate(
        "Không refund khi approval không hợp lệ",
        paid == 0 and approval["error"] is None,
        f"C-007 (approval hết hạn): {paid} dòng ledger, policy_denied={approval['store']['policy_denied']}",
    ))
    leaks: list[str] = []
    for claim_id in ("C-005", "C-010"):
        outcome = run_claim_once(shape, claim_id, seed)
        path = LAB_ROOT / outcome["trace"]["path"]
        if outcome["trace"]["found"] and path.is_file():
            leaks += scan_text(path.read_text(encoding="utf-8", errors="replace"), claim_id)
    gates.append(_gate(
        "Không lộ secret hoặc PII trong trace",
        not leaks,
        "C-005, C-010: sạch" if not leaks else f"Phát hiện: {', '.join(sorted(set(leaks)))}",
    ))
    crashed = run_claim_once(shape, "C-012", seed, crash_at="after_effect_before_checkpoint")
    retried = run_claim_once(shape, "C-012", seed, store_path=crashed["store_path"])
    rows = len(retried["store"]["own_ledger"])
    commits = retried["store"]["committed_audits"]
    gates.append(_gate(
        "Crash không tạo hơn 1 refund",
        crashed["crashed"] is not None and rows == 1 and commits == 1,
        f"C-012 crash={crashed['crashed'] or 'không nổ'} rồi retry: {rows} dòng ledger, {commits} audit refund_committed",
    ))
    return gates


def run_buggy_checkpoint_demo(claim_id: str = "C-012", amount: int = 35000) -> dict[str, Any]:
    """Counter-example from lab8.demo: a checkpoint-only resume pays twice."""
    conn = demo_connection()
    try:
        buggy_pay(conn, claim_id, amount)
        rows = [
            {"id": row[0], "claim_id": row[1], "amount_vnd": row[2], "checkpointed": row[3]}
            for row in conn.execute(
                "SELECT id, claim_id, amount_vnd, checkpointed FROM demo_unsafe_refunds ORDER BY id"
            )
        ]
    finally:
        conn.close()
    return {"rows": rows, "total_vnd": sum(row["amount_vnd"] for row in rows)}
