"""Tab 3 - Bảo mật: three must-pass gates, handoff allowlist probes, trace scan."""

from __future__ import annotations

import json

import streamlit as st

from services import security_durability as sec
from catalog.presets import SEEDS, SHAPE_LABELS, SHAPES
from ui.components import badge, esc, html_block, html_table, placeholder, section_title


def _gate_badge(ok: bool | None) -> str:
    if ok is None:
        return badge("chưa có dữ liệu", "idle")
    return badge("ĐẠT", "ok") if ok else badge("TRƯỢT", "bad")


def _render_gates() -> None:
    section_title(
        "Ba cổng must-pass",
        "Trượt một cổng là không được bù bằng điểm khác. Bấm để chạy bằng chứng trực tiếp trên DB mới.",
    )
    shape_col, seed_col, go_col = st.columns([3, 1, 1], vertical_alignment="bottom")
    shape = shape_col.selectbox("Shape", SHAPES, format_func=SHAPE_LABELS.get, key="gate_shape")
    seed = seed_col.selectbox("Seed", SEEDS, key="gate_seed")
    if go_col.button("Kiểm 3 cổng", type="primary", use_container_width=True, key="gate_go"):
        with st.spinner("Chạy C-007, C-005, C-010 và crash C-012..."):
            st.session_state["gate_rows"] = {"shape": shape, "rows": sec.run_must_pass_gates(shape, seed)}
    data = st.session_state.get("gate_rows")
    if not data:
        placeholder("Chưa kiểm", "Chọn shape rồi bấm Kiểm 3 cổng.")
        return
    rows = [{**row, "result": _gate_badge(row["ok"])} for row in data["rows"]]
    html_block(f"<p>Shape: <strong>{esc(SHAPE_LABELS.get(data['shape'], data['shape']))}</strong></p>")
    html_table(rows, [("gate", "Cổng"), ("result", "Kết quả"), ("evidence", "Bằng chứng")], raw={"result"})


def _render_handoff() -> None:
    section_title(
        "Handoff qua allowlist",
        "Orchestrator chỉ được gửi các field và fact có trong allowlist; worker chỉ có tool đọc.",
    )
    kind = st.radio(
        "Phép thử",
        list(sec.HANDOFF_PROBES),
        format_func=sec.HANDOFF_PROBES.get,
        horizontal=True,
        key="handoff_kind",
        label_visibility="collapsed",
    )
    probe = sec.probe_handoff(kind)
    sent_col, got_col = st.columns(2, gap="large")
    with sent_col:
        html_block("<p><strong>Orchestrator định gửi</strong></p>")
        st.code(json.dumps(probe["sent"], ensure_ascii=False, indent=2), language="json")
    with got_col:
        if probe["accepted"]:
            dropped = sorted(set(probe["sent"]["facts"]) - set(probe["payload"]["facts"]))
            note = badge(f"đã lọc bỏ: {', '.join(dropped)}", "warn") if dropped else badge("chấp nhận", "ok")
            html_block(f"<p><strong>Worker nhận được</strong> {note}</p>")
            st.code(json.dumps(probe["payload"], ensure_ascii=False, indent=2), language="json")
        else:
            html_block(f"<p><strong>Bị từ chối</strong> {badge('HandoffError', 'bad')}</p>")
            st.code(probe["error"], language="text")


def _render_trace_scan() -> None:
    section_title("Quét thư mục src/traces/", "Tìm canary, parent_secret, header, token, số điện thoại và PII đã biết.")
    if st.button("Quét trace", key="scan_go"):
        st.session_state["scan_report"] = sec.scan_traces()
    report = st.session_state.get("scan_report")
    if not report:
        return
    if report["scanned"] == 0:
        placeholder("Chưa có trace nào", "Chạy vài claim ở tab Chạy claim hoặc chạy benchmark trước.")
        return
    count = len(report["findings"])
    summary = badge(f"{count} file có dấu hiệu rò", "ok" if count == 0 else "bad")
    html_block(f'<div class="sc-banner"><strong>Đã quét {report["scanned"]} file</strong>{summary}</div>')
    if report["findings"]:
        html_table(report["findings"], [("file", "File"), ("kinds", "Loại rò rỉ (đã che)")])


def render() -> None:
    _render_gates()
    st.divider()
    _render_handoff()
    st.divider()
    _render_trace_scan()
