"""Small HTML building blocks shared by every page (badges, tables, timeline, placeholders).

Everything user-visible goes through html.escape. Custom HTML tables are used
instead of st.dataframe because canvas grids are too small to read on a projector.
"""

from __future__ import annotations

import html
import json
from typing import Any, Iterable

import streamlit as st

STATUS_TONE = {
    "resolved": "ok",
    "denied": "warn",
    "escalated": "info",
    "needs_info": "idle",
    "failed": "bad",
    "error": "bad",
}
# Trace event kinds worth pointing at during the talk.
HOT_KINDS = {"model_override": "bad", "crash": "warn", "error": "bad", "handoff": "info"}


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def html_block(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def money(value: Any) -> str:
    if value is None:
        return "-"
    return f"{int(value):,}".replace(",", ".") + " đ"


def cost_vnd(value: Any) -> str:
    """Simulated cost in VND, Vietnamese style: '.' groups thousands, ',' marks decimals.

    "30.00 đ" would read as 30 nghìn next to a quote shown as "35.000 đ", so render "30,00 đ".
    """
    if value is None:
        return "-"
    return f"{float(value):,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".") + " đ"


def badge(text: Any, tone: str = "idle") -> str:
    return f'<span class="sc-badge sc-{tone}">{esc(text)}</span>'


def status_badge(status: str | None) -> str:
    return badge(status or "không có", STATUS_TONE.get(status or "", "idle"))


def verdict_badge(outcome: dict[str, Any]) -> str:
    """One badge that summarizes how a run ended, in demo language."""
    if outcome.get("not_implemented"):
        return badge("Shape chưa cài", "idle")
    if outcome.get("crashed"):
        return badge(f"Crash tại {outcome['crashed']}", "warn")
    if outcome.get("error"):
        return badge("Lỗi khi chạy", "bad")
    verdict = outcome.get("verdict") or {}
    if verdict.get("passed") is True:
        return badge("PASS", "ok")
    if verdict.get("passed") is False:
        return badge(f"FAIL · {verdict.get('reason')}", "bad")
    return badge("Chưa chấm", "idle")


def section_title(title: str, hint: str | None = None) -> None:
    hint_html = f"<p>{esc(hint)}</p>" if hint else ""
    html_block(f'<div class="sc-section"><h3>{esc(title)}</h3>{hint_html}</div>')


def placeholder(title: str, body: str, command: str | None = None) -> None:
    """Visible empty state: says what is missing and how to produce it."""
    cmd = f"<code>{esc(command)}</code>" if command else ""
    html_block(f'<div class="sc-placeholder"><h4>{esc(title)}</h4><p>{esc(body)}</p>{cmd}</div>')


def html_table(
    rows: Iterable[dict[str, Any]],
    columns: list[tuple[str, str]],
    *,
    numeric: set[str] | None = None,
    raw: set[str] | None = None,
    extra_class: str = "",
) -> None:
    """Render rows as a readable table. columns = [(key, header)].

    Keys listed in `raw` are trusted HTML produced by this module (badges).
    """
    numeric = numeric or set()
    raw = raw or set()
    head = "".join(f"<th>{esc(header)}</th>" for _, header in columns)
    body = []
    for row in rows:
        cells = []
        for key, _ in columns:
            value = row.get(key)
            content = str(value) if key in raw else esc(value)
            css = ' class="sc-num"' if key in numeric else ""
            cells.append(f"<td{css}>{content}</td>")
        body.append(f"<tr>{''.join(cells)}</tr>")
    if not body:
        body.append(f'<tr><td colspan="{len(columns)}">Không có dòng nào</td></tr>')
    html_block(f'<table class="sc-table {extra_class}"><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>')


def compact_json(payload: Any, limit: int = 220) -> str:
    text = json.dumps(payload, ensure_ascii=False, default=str)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def trace_timeline(trace: dict[str, Any]) -> None:
    """Numbered list of trace events; risky kinds are tinted."""
    if not trace.get("found"):
        placeholder("Chưa có trace", "Lần chạy này chưa ghi file trace nào.")
        return
    items = []
    for index, event in enumerate(trace.get("events") or [], start=1):
        kind = event.get("kind", "?")
        tone = HOT_KINDS.get(kind, "idle")
        items.append(
            f'<li class="sc-step sc-step-{tone}"><span class="sc-step-no">{index}</span>'
            f'<span class="sc-step-kind">{esc(kind)}</span><code>{esc(compact_json(event.get("payload")))}</code></li>'
        )
    stale = badge("Trace cũ từ lần chạy trước", "warn") if trace.get("stale") else ""
    html_block(f'<p>File: <code>{esc(trace.get("path"))}</code> {stale}</p><ol class="sc-timeline">{"".join(items)}</ol>')


def trace_chain(trace: dict[str, Any]) -> str:
    """One-line chain of event kinds, used in side-by-side comparison cards."""
    kinds = [event.get("kind", "?") for event in trace.get("events") or []]
    if not kinds:
        return '<div class="sc-chain"><span>không có trace</span></div>'
    parts = [f'<span class="{"sc-hot" if kind in ("model_override", "crash", "error") else ""}">{esc(kind)}</span>' for kind in kinds]
    return f'<div class="sc-chain">{" → ".join(parts)}</div>'


def kv_card(title: str, pairs: list[tuple[str, str]], header_html: str = "") -> str:
    """Card with key/value lines. Values are trusted HTML (already escaped or badges)."""
    lines = "".join(f'<div class="sc-kv"><span>{esc(k)}</span><span>{v}</span></div>' for k, v in pairs)
    return f'<div class="sc-card"><h4>{esc(title)}</h4>{header_html}{lines}</div>'
