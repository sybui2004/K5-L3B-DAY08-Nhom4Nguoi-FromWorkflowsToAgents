"""Render one run outcome: full detail (Runner tab) or a compact card (Compare tab)."""

from __future__ import annotations

from typing import Any

import streamlit as st

from catalog.presets import SHAPE_LABELS
from ui.components import (
    badge,
    cost_vnd,
    esc,
    html_block,
    html_table,
    kv_card,
    money,
    placeholder,
    section_title,
    status_badge,
    trace_chain,
    trace_timeline,
    verdict_badge,
)


def _expected_vs_actual(outcome: dict[str, Any], expected: dict[str, Any]) -> list[dict[str, Any]]:
    result = outcome.get("result") or {}
    store = outcome["store"]
    own = store["own_ledger"]
    actual = {
        "status": result.get("status"),
        "proposal_amount": result.get("proposal_amount"),
        "refund_vnd": sum(int(row["amount_vnd"]) for row in own),
        "refund_count": len(own),
        "audit_refund_committed": store["committed_audits"],
        "policy_denied": store["policy_denied"],
    }
    labels = {
        "status": "Status",
        "proposal_amount": "Quote đề xuất",
        "refund_vnd": "Tiền đã ghi ledger",
        "refund_count": "Số dòng ledger của claim",
        "audit_refund_committed": "Audit refund_committed",
        "policy_denied": "Audit policy_denied",
    }
    money_keys = {"proposal_amount", "refund_vnd"}
    rows = []
    for key, label in labels.items():
        want, got = expected.get(key), actual[key]
        same = (bool(want) == bool(got)) if key == "policy_denied" else (want == got)
        fmt = money if key in money_keys else (lambda v: "-" if v is None else str(v))
        rows.append({
            "field": label,
            "expected": fmt(want),
            "actual": fmt(got),
            "match": badge("khớp", "ok") if same else badge("lệch", "bad"),
        })
    return rows


def render_outcome_detail(outcome: dict[str, Any], expected: dict[str, Any]) -> None:
    """Full panel: verdict banner, expected vs actual, budget, trace, ledger, audit."""
    result = outcome.get("result") or {}
    html_block(
        f'<div class="sc-banner"><strong>{esc(outcome["claim_id"])} · {esc(SHAPE_LABELS.get(outcome["shape"], outcome["shape"]))}'
        f' · seed {esc(outcome["seed"])}</strong>{verdict_badge(outcome)}{status_badge(result.get("status"))}</div>'
    )
    if outcome.get("not_implemented"):
        placeholder(
            "Shape này chưa được cài",
            "run_claim đang trả not_implemented. Khi phase tương ứng xong, bấm chạy lại để thấy kết quả thật.",
        )
    if outcome.get("error"):
        placeholder("Shape ném exception", outcome["error"])

    cols = st.columns(5)
    cols[0].metric("Quote", money(result.get("proposal_amount")))
    cols[1].metric("Model call", result.get("model_calls", 0))
    cols[2].metric("Tool call", result.get("tool_calls", 0))
    cols[3].metric("Số bước trace", outcome["trace"].get("steps", 0))
    cols[4].metric("Cost mô phỏng", cost_vnd(result.get("cost_estimate", 0.0)))

    section_title("Kỳ vọng và thực tế", "Kỳ vọng lấy từ nhãn của claim; thực tế đọc từ RunResult và ledger.")
    html_table(
        _expected_vs_actual(outcome, expected),
        [("field", "Trường"), ("expected", "Kỳ vọng"), ("actual", "Thực tế"), ("match", "")],
        raw={"match"},
    )

    left, right = st.columns([3, 2], gap="large")
    with left:
        section_title("Trace", "Thứ tự sự kiện shape đã ghi. Không có ticket, claim row hay order row thô.")
        trace_timeline(outcome["trace"])
    with right:
        render_store_panel(outcome)


def render_store_panel(outcome: dict[str, Any]) -> None:
    """Ledger + audit + checkpoints of one run, read straight from SQLite."""
    store = outcome["store"]
    section_title("Ledger", "Nguồn sự thật về tiền. Dòng của claim khác là tiền đã hoàn từ trước.")
    rows = [
        {**row, "amount": money(row["amount_vnd"]),
         "origin": "lần chạy này" if row["claim_id"] == outcome["claim_id"] else "đã có từ trước"}
        for row in store["ledger"]
    ]
    html_table(rows, [("claim_id", "Claim"), ("order_id", "Đơn"), ("amount", "Số tiền"), ("origin", "Nguồn")],
               numeric={"amount"})
    section_title("Audit của claim")
    html_table(store["audits"], [("event_type", "Sự kiện"), ("details", "Chi tiết")])
    if store["checkpoints"]:
        html_block(f'<p>Checkpoint: <code>{esc(", ".join(store["checkpoints"]))}</code></p>')


def render_outcome_card(outcome: dict[str, Any]) -> None:
    """Compact card for side-by-side comparison of shapes on the same claim."""
    result = outcome.get("result") or {}
    pairs = [
        ("Status", status_badge(result.get("status"))),
        ("Quote", esc(money(result.get("proposal_amount")))),
        ("Ledger", esc(money(sum(int(r["amount_vnd"]) for r in outcome["store"]["own_ledger"])))),
        ("Model call", esc(result.get("model_calls", 0))),
        ("Tool call", esc(result.get("tool_calls", 0))),
        ("Số bước", esc(outcome["trace"].get("steps", 0))),
        ("Cost", esc(cost_vnd(result.get("cost_estimate", 0.0)))),
    ]
    header = f"<p>{verdict_badge(outcome)}</p>"
    html_block(kv_card(SHAPE_LABELS.get(outcome["shape"], outcome["shape"]), pairs, header) + trace_chain(outcome["trace"]))
