"""Main page - chatbot view of one claim run.

Sidebar holds the run config (claim, shape, seed, crash). "Gửi ticket" posts the
claim's ticket as the customer message; each shape answers as an assistant message
with the full live call log (tool / model / host / trace), the 7 report metrics,
and the verdict against the claim's expected label. "Gửi cho cả 4 shape" answers the
same ticket four times so shapes can be compared inside one conversation.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from services import lab_runner as svc
from ui.chat_renderers import (
    call_counts,
    expected_line_html,
    metrics_strip_html,
    reply_text,
    timeline_html,
)
from ui.outcome_panels import render_store_panel
from catalog.presets import CRASH_LABELS, CRASH_POINTS, SEEDS, SHAPE_LABELS, SHAPES, scenario_label
from ui.components import esc, html_block, money, status_badge, verdict_badge

HISTORY_KEY = "chat_history"


def _run_turn(claim: dict[str, Any], shapes: list[str], seed: int, crash_at: str | None) -> None:
    outcomes = []
    with st.spinner(f"Đang chạy {len(shapes)} shape trên DB mới..."):
        for shape in shapes:
            outcomes.append(svc.run_claim_once(shape, claim["claim_id"], seed, crash_at=crash_at))
    st.session_state[HISTORY_KEY].append({"claim": claim, "seed": seed, "crash_at": crash_at, "outcomes": outcomes})


def _sidebar(claims: list[dict[str, Any]]) -> None:
    by_id = {claim["claim_id"]: claim for claim in claims}
    st.sidebar.markdown("### Cấu hình lần chạy")
    claim_id = st.sidebar.selectbox(
        "Claim", list(by_id), format_func=lambda cid: f"{cid} · {scenario_label(cid)}", key="chat_claim"
    )
    shape = st.sidebar.selectbox("Shape", SHAPES, format_func=SHAPE_LABELS.get, key="chat_shape")
    seed = st.sidebar.selectbox("Seed", SEEDS, key="chat_seed")
    crash_at = st.sidebar.selectbox("Crash", CRASH_POINTS, format_func=CRASH_LABELS.get, key="chat_crash")

    claim = by_id[claim_id]
    expected = claim["expected"]
    st.sidebar.markdown(
        f'<div class="sc-side-claim"><div><span>Principal</span><b>{esc(claim["principal_id"])}</b></div>'
        f'<div><span>Đơn</span><b>{esc(claim["order_id"] or "không có")}</b></div>'
        f'<div><span>Kỳ vọng</span><b>{status_badge(expected.get("status"))} {esc(money(expected.get("proposal_amount")))}</b></div></div>',
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Gửi ticket", type="primary", use_container_width=True, key="chat_send"):
        _run_turn(claim, [shape], seed, crash_at)
    if st.sidebar.button("Gửi cho cả 4 shape", use_container_width=True, key="chat_send_all"):
        _run_turn(claim, list(SHAPES), seed, crash_at)
    if st.sidebar.button("Xóa hội thoại", use_container_width=True, key="chat_clear"):
        st.session_state[HISTORY_KEY] = []
    st.sidebar.caption("Mỗi lần gửi chạy trên một DB SQLite mới. MockLLM, cost mô phỏng.")


def _render_user(turn: dict[str, Any]) -> None:
    claim = turn["claim"]
    with st.chat_message("user", avatar=":material/person:"):
        crash = f" · crash `{turn['crash_at']}`" if turn["crash_at"] else ""
        st.caption(f"{claim['claim_id']} · {claim['principal_id']} · đơn {claim['order_id'] or 'không có'} · seed {turn['seed']}{crash}")
        st.markdown(claim["ticket"])


def _render_assistant(outcome: dict[str, Any], claim: dict[str, Any], expanded: bool) -> None:
    with st.chat_message("assistant", avatar=":material/local_shipping:"):
        st.caption(f"{SHAPE_LABELS.get(outcome['shape'], outcome['shape'])} · seed {outcome['seed']}")
        calls = outcome.get("calls") or []
        counts = call_counts(calls)
        title = (f"Quá trình xử lý · {len(calls)} sự kiện · {counts['tool']} tool · "
                 f"{counts['model']} model · {counts['host']} host · {counts['trace']} trace")
        with st.expander(title, expanded=expanded):
            html_block(timeline_html(calls, (outcome.get("result") or {}).get("tool_calls", 0)))
        st.markdown(reply_text(outcome, claim))
        html_block(metrics_strip_html(outcome))
        html_block(expected_line_html(outcome, claim["expected"], verdict_badge(outcome)))
        with st.expander("Ledger và audit (SQLite)"):
            render_store_panel(outcome)


def render() -> None:
    claims = svc.load_public_claims()
    st.session_state.setdefault(HISTORY_KEY, [])
    _sidebar(claims)

    history = st.session_state[HISTORY_KEY]
    if not history:
        with st.chat_message("assistant", avatar=":material/local_shipping:"):
            st.markdown("Chưa có ticket nào. Chọn claim và shape ở thanh bên rồi bấm **Gửi ticket**.")
        return
    last = len(history) - 1
    for index, turn in enumerate(history):
        _render_user(turn)
        for outcome in turn["outcomes"]:
            _render_assistant(outcome, turn["claim"], expanded=(index == last and len(turn["outcomes"]) == 1))
