"""Tab 1 - Chạy claim: pick one public claim, one shape, one seed, and watch a full run."""

from __future__ import annotations

import streamlit as st

from services import lab_runner as svc
from ui.outcome_panels import render_outcome_detail
from catalog.presets import (
    CRASH_LABELS,
    CRASH_POINTS,
    GROUP_LABELS,
    RUNNER_PRESET,
    SEEDS,
    SHAPE_LABELS,
    SHAPES,
    scenario_group,
    scenario_label,
)
from ui.components import esc, html_block, html_table, kv_card, money, section_title, status_badge


def _apply_preset() -> None:
    """Button callback: runs before widgets are rebuilt, so widget keys can be set."""
    st.session_state["runner_group"] = "all"
    st.session_state["runner_claim"] = RUNNER_PRESET["claim"]
    st.session_state["runner_shape"] = RUNNER_PRESET["shape"]
    st.session_state["runner_seed"] = RUNNER_PRESET["seed"]
    st.session_state["runner_crash"] = None


def render() -> None:
    claims = svc.load_public_claims()
    by_id = {claim["claim_id"]: claim for claim in claims}

    left, right = st.columns([3, 2], gap="large")
    with left:
        section_title("Danh sách claim", "14 claim công khai. Không hiển thị parent_secret hay header.")
        group = st.radio(
            "Nhóm kịch bản",
            list(GROUP_LABELS),
            format_func=GROUP_LABELS.get,
            horizontal=True,
            key="runner_group",
            label_visibility="collapsed",
        )
        visible = [c for c in claims if group == "all" or scenario_group(c["claim_id"]) == group]
        html_table(
            [
                {
                    "claim": c["claim_id"],
                    "case": c["matrix_id"],
                    "scenario": scenario_label(c["claim_id"]),
                    "expected": f'{status_badge(c["expected"].get("status"))} {esc(money(c["expected"].get("proposal_amount")))}',
                }
                for c in visible
            ],
            [("claim", "Claim"), ("case", "Case"), ("scenario", "Kịch bản"), ("expected", "Kỳ vọng")],
            raw={"expected"},
        )

    with right:
        section_title("Cấu hình lần chạy")
        st.button("Kịch bản mở đầu: C-001 · workflow · seed 11", on_click=_apply_preset, use_container_width=True)
        options = [c["claim_id"] for c in visible] or list(by_id)
        if st.session_state.get("runner_claim") not in options:
            st.session_state["runner_claim"] = options[0]  # group filter changed under the selection
        claim_id = st.selectbox(
            "Claim", options, format_func=lambda cid: f"{cid} · {scenario_label(cid)}", key="runner_claim"
        )
        shape = st.selectbox("Shape", SHAPES, format_func=SHAPE_LABELS.get, key="runner_shape")
        seed = st.selectbox("Seed", SEEDS, key="runner_seed")
        crash_at = st.selectbox("Crash", CRASH_POINTS, format_func=CRASH_LABELS.get, key="runner_crash")
        if st.button("Chạy claim", type="primary", use_container_width=True, key="runner_go"):
            with st.spinner("Đang chạy trên DB mới..."):
                st.session_state["runner_outcome"] = svc.run_claim_once(shape, claim_id, seed, crash_at=crash_at)

        claim = by_id.get(claim_id)
        if claim:
            pairs = [
                ("Principal", esc(claim["principal_id"])),
                ("Đơn", esc(claim["order_id"] or "không có")),
                ("Kỳ vọng", f'{status_badge(claim["expected"].get("status"))} {esc(money(claim["expected"].get("proposal_amount")))}'),
            ]
            ticket = f'<div class="sc-ticket">{esc(claim["ticket"])}</div>'
            html_block(kv_card(f'{claim_id} · {scenario_label(claim_id)}', pairs, ticket))

    outcome = st.session_state.get("runner_outcome")
    if outcome:
        st.divider()
        render_outcome_detail(outcome, by_id.get(outcome["claim_id"], {}).get("expected", {}))
