"""LogiX-VN Lab 8 showcase - live demo for the classroom projector.

Run from the repo root (K5-Day8-From-Workflows-to-Agents/) with the lab venv active:

    python -m pip install -r showcase/requirements-demo.txt
    streamlit run showcase/app.py --theme.base light

The app imports lab8 from src/ and reads src/reports, src/traces.
Every page opens with a waybill strip (what the page shows + the run facts).
Pages sit in the sidebar in talk order. The slides live in showcase/slides/index.html.
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="LogiX-VN Showcase",
    layout="wide",
    initial_sidebar_state="expanded",
)

from services import lab_runner  # noqa: E402,F401 - bootstraps repo path and cwd before lab8 imports
from views import benchmark_dashboard  # noqa: E402
from views import chat_console  # noqa: E402
from views import compare_shapes  # noqa: E402
from views import durability_lab  # noqa: E402
from views import security_gates  # noqa: E402
from ui.theme import inject_theme  # noqa: E402
from ui.components import esc, html_block  # noqa: E402
from catalog.team_roster import MEMBERS, TEAM_NAME  # noqa: E402

# label in the menu -> (module, strip title, strip subtitle)
PAGES = {
    "Xử lý một ticket": (
        chat_console,
        "Gửi một ticket, xem shape xử lý từng bước",
        "Chọn claim và shape ở thanh bên. Mỗi câu trả lời kèm tool call, model call, host và trace.",
    ),
    "So sánh 4 shape": (
        compare_shapes,
        "Cùng một claim, cùng seed, bốn kiến trúc",
        "Chỗ swarm tin số ngày trong ticket hiện ra dưới dạng model_override.",
    ),
    "Cổng bảo mật": (
        security_gates,
        "Secret và PII không được lọt khỏi host",
        "Handoff allowlist, quét trace tìm canary, chặn approval của claim khác.",
    ),
    "Crash và retry": (
        durability_lab,
        "Sập giữa chừng, chạy lại, vẫn chỉ một dòng tiền",
        "Ledger là nguồn sự thật. Checkpoint chỉ là ghi chú tiến độ.",
    ),
    "Bảng benchmark": (
        benchmark_dashboard,
        "Độ đúng và cái giá của từng shape",
        "14 claim công khai × 5 seed, mỗi trial một SQLite mới, cost mô phỏng.",
    ),
}

STRIP_FACTS = [("14", "claim công khai"), ("4", "shape"), ("5", "seed"), ("MockLLM", "không cần API key")]


def _sidebar_brand() -> None:
    crew = "".join(
        f'<div class="{"" if m["mssv"] else "sc-crew-todo"}"><span>{esc(m["name"])}</span>'
        f'<span>{esc(m["mssv"] or "chưa điền")}</span></div>'
        for m in MEMBERS
    )
    st.sidebar.markdown(
        f'<div class="sc-brand"><strong>LogiX-VN showcase</strong><span>Lab 8 · {esc(TEAM_NAME)}</span>'
        f'<div class="sc-crew">{crew}</div></div>',
        unsafe_allow_html=True,
    )


def _strip(title: str, subtitle: str) -> None:
    facts = "".join(f"<div><strong>{esc(v)}</strong><span>{esc(k)}</span></div>" for v, k in STRIP_FACTS)
    html_block(
        f'<div class="sc-strip"><div class="sc-strip-main"><h1>{esc(title)}</h1><p>{esc(subtitle)}</p></div>'
        f'<div class="sc-strip-facts">{facts}</div></div>'
    )


def main() -> None:
    inject_theme()
    _sidebar_brand()
    label = st.sidebar.radio("Trang", list(PAGES), key="nav_page", label_visibility="collapsed")
    st.sidebar.divider()
    module, title, subtitle = PAGES[label]
    _strip(title, subtitle)
    try:
        module.render()
    except Exception as exc:  # noqa: BLE001 - one broken page must not blank the demo
        st.error(f"Trang {label} gặp lỗi: {type(exc).__name__}: {exc}")


main()
