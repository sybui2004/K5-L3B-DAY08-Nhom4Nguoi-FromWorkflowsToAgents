"""Tab 2 - So sánh 4 shape: the same claim and seed on every shape, side by side.

The money moment is C-002 at seed 55: the swarm trusts the delay written in the
ticket (trace event model_override) while workflow reads the order row.
"""

from __future__ import annotations

import streamlit as st

from services import lab_runner as svc
from ui.outcome_panels import render_outcome_card
from catalog.presets import COMPARE_PRESETS, SEEDS, SHAPE_LABELS, SHAPES, scenario_label
from ui.components import badge, esc, html_block, html_table, money, section_title, status_badge, verdict_badge


def _preset_callback(claim_id: str, seed: int):
    def apply() -> None:
        st.session_state["compare_claim"] = claim_id
        st.session_state["compare_seed"] = seed
        st.session_state["compare_autorun"] = True

    return apply


def _run_all(claim_id: str, seed: int) -> None:
    with st.spinner(f"Chạy {claim_id} seed {seed} trên 4 shape, mỗi shape một DB mới..."):
        st.session_state["compare_outcomes"] = [svc.run_claim_once(shape, claim_id, seed) for shape in SHAPES]


def render() -> None:
    claims = svc.load_public_claims()
    by_id = {claim["claim_id"]: claim for claim in claims}

    section_title("Kịch bản dựng sẵn", "Bấm là chạy ngay, không cần chọn tay khi đang trình bày.")
    preset_cols = st.columns(len(COMPARE_PRESETS))
    for col, (label, claim_id, seed) in zip(preset_cols, COMPARE_PRESETS):
        col.button(label, on_click=_preset_callback(claim_id, seed), use_container_width=True, key=f"cmp_{claim_id}_{seed}")

    pick_claim, pick_seed, go = st.columns([3, 1, 1], vertical_alignment="bottom")
    claim_id = pick_claim.selectbox(
        "Claim", list(by_id), format_func=lambda cid: f"{cid} · {scenario_label(cid)}", key="compare_claim"
    )
    seed = pick_seed.selectbox("Seed", SEEDS, key="compare_seed")
    if go.button("Chạy 4 shape", type="primary", use_container_width=True, key="compare_go"):
        _run_all(claim_id, seed)
    elif st.session_state.pop("compare_autorun", False):
        _run_all(claim_id, seed)

    outcomes = st.session_state.get("compare_outcomes")
    if not outcomes:
        return

    first = outcomes[0]
    expected = by_id.get(first["claim_id"], {}).get("expected", {})
    ticket = by_id.get(first["claim_id"], {}).get("ticket", "")
    html_block(
        f'<div class="sc-banner"><strong>{esc(first["claim_id"])} · seed {esc(first["seed"])}</strong>'
        f'Kỳ vọng {status_badge(expected.get("status"))} {esc(money(expected.get("proposal_amount")))}</div>'
        f'<div class="sc-ticket">{esc(ticket)}</div>'
    )

    cols = st.columns(len(outcomes), gap="medium")
    for col, outcome in zip(cols, outcomes):
        with col:
            render_outcome_card(outcome)

    section_title("Tóm tắt", "Dòng có model_override là chỗ shape tin ticket thay vì order row.")
    rows = []
    for outcome in outcomes:
        result = outcome.get("result") or {}
        kinds = [event.get("kind") for event in outcome["trace"].get("events") or []]
        rows.append({
            "shape": SHAPE_LABELS.get(outcome["shape"], outcome["shape"]),
            "verdict": verdict_badge(outcome),
            "status": status_badge(result.get("status")),
            "quote": money(result.get("proposal_amount")),
            "model": result.get("model_calls", 0),
            "steps": outcome["trace"].get("steps", 0),
            "override": badge("tin ticket", "bad") if "model_override" in kinds else badge("không", "idle"),
        })
    html_table(
        rows,
        [("shape", "Shape"), ("verdict", "Chấm"), ("status", "Status"), ("quote", "Quote"),
         ("model", "Model call"), ("steps", "Bước"), ("override", "Override")],
        numeric={"quote", "model", "steps"},
        raw={"verdict", "status", "override"},
    )
