"""Tab 4 - Durability: crash, retry on the same DB, and the checkpoint-only counter-example.

Story: the ledger (keyed by claim_id + idempotency key) is the source of truth,
so a retry after a crash replays instead of paying again. A resume that trusts
only a checkpoint flag pays twice.
"""

from __future__ import annotations

import streamlit as st

from services import lab_runner as svc
from services import security_durability as sec
from catalog.presets import CRASH_LABELS, CRASH_POINTS, DURABILITY_PRESET, SEEDS, SHAPE_LABELS, SHAPES
from ui.components import badge, esc, html_block, html_table, money, placeholder, section_title, verdict_badge

CRASH_ONLY = [point for point in CRASH_POINTS if point]


def _ledger_summary(outcome: dict) -> str:
    store = outcome["store"]
    own = store["own_ledger"]
    rows_badge = badge(f"{len(own)} dòng ledger", "ok" if len(own) <= 1 else "bad")
    audit_badge = badge(f"{store['committed_audits']} audit refund_committed", "ok" if store["committed_audits"] <= 1 else "bad")
    total = money(sum(int(row["amount_vnd"]) for row in own))
    return f"{verdict_badge(outcome)} {rows_badge} {audit_badge} <strong>{esc(total)}</strong>"


def _render_live_crash() -> None:
    section_title("Crash rồi retry trên cùng DB", "Bước 1 làm shape nổ giữa chừng. Bước 2 chạy lại đúng claim đó trên cùng file SQLite.")
    c1, c2, c3, c4 = st.columns([2, 2, 1, 3])
    shape = c1.selectbox("Shape", SHAPES, index=SHAPES.index(DURABILITY_PRESET["shape"]),
                         format_func=SHAPE_LABELS.get, key="dur_shape")
    claim_id = c2.text_input("Claim", value=DURABILITY_PRESET["claim"], key="dur_claim")
    seed = c3.selectbox("Seed", SEEDS, key="dur_seed")
    crash_at = c4.selectbox("Điểm crash", CRASH_ONLY, index=CRASH_ONLY.index(DURABILITY_PRESET["crash_at"]),
                            format_func=CRASH_LABELS.get, key="dur_crash")

    step1, step2 = st.columns(2, gap="large")
    with step1:
        if st.button("1. Chạy có crash", type="primary", use_container_width=True, key="dur_step1"):
            first = svc.run_claim_once(shape, claim_id, seed, crash_at=crash_at)
            st.session_state["dur_first"] = first
            st.session_state.pop("dur_retry", None)
        first = st.session_state.get("dur_first")
        if first:
            html_block(f'<div class="sc-card"><h4>Sau crash</h4><p>{_ledger_summary(first)}</p></div>')
    with step2:
        first = st.session_state.get("dur_first")
        disabled = first is None
        if st.button("2. Retry cùng DB", use_container_width=True, disabled=disabled, key="dur_step2"):
            st.session_state["dur_retry"] = svc.run_claim_once(
                first["shape"], first["claim_id"], first["seed"], store_path=first["store_path"]
            )
        retry = st.session_state.get("dur_retry")
        if retry:
            html_block(f'<div class="sc-card"><h4>Sau retry</h4><p>{_ledger_summary(retry)}</p></div>')
            html_table(
                [{**row, "amount": money(row["amount_vnd"])} for row in retry["store"]["own_ledger"]],
                [("claim_id", "Claim"), ("order_id", "Đơn"), ("amount", "Số tiền"), ("status", "Trạng thái")],
                numeric={"amount"},
            )
        elif disabled:
            placeholder("Chờ bước 1", "Retry chỉ có ý nghĩa khi đã có một lần chạy bị crash.")


def _render_counter_example() -> None:
    section_title("Phản ví dụ: chỉ tin checkpoint", "lab8.demo.buggy_workflow - bảng demo không khóa theo claim nên retry trả tiền lần 2.")
    if st.button("Chạy phản ví dụ", key="dur_buggy"):
        st.session_state["dur_buggy_result"] = sec.run_buggy_checkpoint_demo()
    buggy = st.session_state.get("dur_buggy_result")
    if not buggy:
        return
    count = len(buggy["rows"])
    html_block(
        f'<div class="sc-banner"><strong>{count} dòng · {esc(money(buggy["total_vnd"]))}</strong>'
        f'{badge("trả tiền 2 lần", "bad") if count > 1 else badge("1 dòng", "ok")}</div>'
    )
    html_table(
        [{**row, "amount": money(row["amount_vnd"])} for row in buggy["rows"]],
        [("id", "#"), ("claim_id", "Claim"), ("amount", "Số tiền"), ("checkpointed", "Checkpoint")],
        numeric={"amount"},
    )


def _render_crash_suite() -> None:
    section_title("Crash suite", "Kết quả của lab8.crash_test, đọc từ src/reports/crash.json.")
    report = svc.load_report("crash.json")
    if not report:
        placeholder("Chưa có src/reports/crash.json", "Chạy crash suite trong src/ rồi tải lại trang.",
                    "python -m lab8.crash_test --count 20 --out reports/crash.json")
        return
    passed, count = report.get("passed", 0), report.get("count", 0)
    html_block(
        f'<div class="sc-banner"><strong>crash_safety = {esc(report.get("crash_safety", f"{passed}/{count}"))}</strong>'
        f'{badge("an toàn", "ok") if passed == count else badge("có kịch bản trượt", "bad")}</div>'
    )
    rows = [{**row, "result": badge("pass", "ok") if row.get("passed") else badge("fail", "bad")}
            for row in report.get("scenarios", [])]
    html_table(rows, [("id", "ID"), ("point", "Điểm crash"), ("result", "Kết quả"), ("reason", "Lý do")], raw={"result"})


def render() -> None:
    _render_live_crash()
    st.divider()
    left, right = st.columns(2, gap="large")
    with left:
        _render_counter_example()
    with right:
        _render_crash_suite()
