"""Waybill theme for the Streamlit showcase.

The subject is shipping-fee refunds, so the look borrows from a carrier's waybill:
cool grey-green paper, petrol ink, and one strip of hazard-yellow packing tape used
only to mark "where you are" (active nav item, page strip, highlighted rows).
Green/red/amber stay reserved for pass/fail/warning.

Type: Be Vietnam Pro (drawn for Vietnamese diacritics) for everything, IBM Plex Mono
only for claim ids, run ids and code. Both fall back to Segoe UI / Consolas offline.
Sizes stay large because the app is shown on a classroom projector.
"""

from __future__ import annotations

import streamlit as st

THEME_CSS = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap");
:root {
  --sc-paper: #E9EEEC; --sc-surface: #F8FAF9; --sc-ink: #0F2A2C; --sc-muted: #4F6466;
  --sc-line: #C9D4D2; --sc-petrol: #0E4D52; --sc-petrol-deep: #08302F; --sc-petrol-soft: #DCE8E7;
  --sc-tape: #F4C20D; --sc-tape-soft: #FDF3C4;
  --sc-ok: #17734A; --sc-ok-soft: #DDF0E5; --sc-bad: #B42318; --sc-bad-soft: #FBE4E1;
  --sc-warn: #9A5B00; --sc-warn-soft: #FBEBCF; --sc-info: #0E4D52; --sc-info-soft: #DCE8E7;
  --sc-idle: #4F6466; --sc-idle-soft: #E1E7E6;
  --sc-font: "Be Vietnam Pro", "Segoe UI Variable Text", "Segoe UI", system-ui, sans-serif;
  --sc-mono: "IBM Plex Mono", "Cascadia Mono", Consolas, monospace;
}
html, body, .stApp, [class*="st-"] { font-family: var(--sc-font); }
/* The rule above also hits Streamlit's ligature icons (expander arrow, sidebar toggle):
   without their icon font they render as raw text like "keyboard_arrow_down". */
[data-testid="stIconMaterial"], span[class*="material-symbols"], [data-testid="stExpanderToggleIcon"] {
  font-family: "Material Symbols Rounded" !important; }
[data-testid="stExpander"] summary { align-items: center; }
.stApp { background: var(--sc-paper); color: var(--sc-ink); }
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1440px; padding-top: 3.2rem; padding-bottom: 4rem; }
.stApp p, .stApp li, .stApp label { font-size: 1.12rem; }
code, pre { font-family: var(--sc-mono) !important; }
:focus-visible { outline: 3px solid var(--sc-tape) !important; outline-offset: 2px; }

button[data-baseweb="tab"] p { font-size: 1.2rem; font-weight: 600; }
button[data-baseweb="tab"][aria-selected="true"] p { color: var(--sc-petrol); }
[data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 800; letter-spacing: -0.02em; color: var(--sc-petrol); }
[data-testid="stMetricLabel"] p { font-size: 1rem; color: var(--sc-muted); }
.stButton > button { font-size: 1.05rem; font-weight: 600; border-radius: 4px; padding: 0.55rem 1.1rem;
  border: 1.5px solid var(--sc-petrol); color: var(--sc-petrol); background: var(--sc-surface); }
.stButton > button:hover { background: var(--sc-petrol-soft); border-color: var(--sc-petrol); color: var(--sc-petrol-deep); }
.stButton > button[kind="primary"] { background: var(--sc-tape); color: var(--sc-ink); border: 1.5px solid var(--sc-ink); }
.stButton > button[kind="primary"]:hover { background: #FFD43B; color: var(--sc-ink); }
.stButton > button[kind="primary"] p, [data-testid="stSidebar"] .stButton > button[kind="primary"] p { color: var(--sc-ink); font-weight: 800; }
td.sc-id, .sc-table td.sc-id { white-space: nowrap; font-family: var(--sc-mono); }

/* Page strip: a waybill header. Left block = what page this is, right = shipment facts. */
.sc-strip { display: grid; grid-template-columns: 1fr auto; align-items: stretch; margin-bottom: 1.4rem;
  background: var(--sc-surface); border: 2px solid var(--sc-ink); border-radius: 4px; }
.sc-strip-main { padding: 1rem 1.4rem; border-left: 12px solid var(--sc-tape); }
.sc-strip-main h1 { font-size: clamp(1.8rem, 2.6vw, 2.6rem); line-height: 1.1; letter-spacing: -0.03em;
  font-weight: 800; margin: 0; color: var(--sc-ink); padding: 0; }
.sc-strip-main p { font-size: 1.1rem; color: var(--sc-muted); margin: 0.35rem 0 0; }
.sc-strip-facts { display: grid; grid-auto-flow: column; border-left: 2px solid var(--sc-ink); }
.sc-strip-facts div { padding: 0.8rem 1.1rem; border-left: 1px dashed var(--sc-line); min-width: 6.5rem; }
.sc-strip-facts div:first-child { border-left: 0; }
.sc-strip-facts strong { display: block; font-size: 1.7rem; font-weight: 800; color: var(--sc-petrol); line-height: 1.1; }
.sc-strip-facts span { font-size: 0.92rem; color: var(--sc-muted); }
@media (max-width: 900px) { .sc-strip { grid-template-columns: 1fr; }
  .sc-strip-facts { border-left: 0; border-top: 2px solid var(--sc-ink); } }

.sc-section { margin: 1.8rem 0 0.7rem; padding-bottom: 0.4rem; border-bottom: 2px solid var(--sc-ink); }
.sc-section h3 { font-size: 1.5rem; font-weight: 800; letter-spacing: -0.02em; margin: 0; color: var(--sc-ink); padding: 0; }
.sc-section p { font-size: 1.05rem; color: var(--sc-muted); margin: 0.2rem 0 0; }

.sc-card { background: var(--sc-surface); border: 1.5px solid var(--sc-line); border-top: 4px solid var(--sc-petrol);
  border-radius: 4px; padding: 1.1rem 1.3rem; margin-bottom: 0.9rem; }
.sc-card h4 { font-size: 1.3rem; font-weight: 700; margin: 0 0 0.5rem; letter-spacing: -0.01em; padding: 0; }
.sc-card .sc-kv { display: flex; justify-content: space-between; gap: 1rem; font-size: 1.08rem;
  padding: 0.3rem 0; border-bottom: 1px dashed var(--sc-line); }
.sc-card .sc-kv:last-child { border-bottom: 0; }
.sc-card .sc-kv span:first-child { color: var(--sc-muted); }
.sc-card .sc-kv span:last-child { font-weight: 600; text-align: right; }
.sc-ticket { font-size: 1.28rem; line-height: 1.5; background: var(--sc-surface); border: 1.5px dashed var(--sc-ink);
  border-radius: 4px; padding: 0.8rem 1.1rem; margin: 0.6rem 0; }

/* Badges look like small printed labels, not pills */
.sc-badge { display: inline-block; padding: 0.15rem 0.6rem; border-radius: 3px; font-weight: 700;
  font-size: 0.98rem; border: 1.5px solid transparent; }
.sc-ok { color: var(--sc-ok); background: var(--sc-ok-soft); border-color: var(--sc-ok); }
.sc-bad { color: var(--sc-bad); background: var(--sc-bad-soft); border-color: var(--sc-bad); }
.sc-warn { color: var(--sc-warn); background: var(--sc-warn-soft); border-color: var(--sc-warn); }
.sc-info { color: var(--sc-info); background: var(--sc-info-soft); border-color: var(--sc-info); }
.sc-idle { color: var(--sc-idle); background: var(--sc-idle-soft); border-color: var(--sc-line); }

.sc-banner { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; padding: 0.9rem 1.2rem;
  border-radius: 4px; background: var(--sc-petrol); color: #FFFFFF; margin: 0.8rem 0; }
.sc-banner strong { font-size: 1.45rem; letter-spacing: -0.01em; }
.sc-banner .sc-badge { background: var(--sc-surface); }

.sc-table { width: 100%; border-collapse: collapse; background: var(--sc-surface); font-size: 1.08rem;
  border-top: 2px solid var(--sc-ink); border-bottom: 2px solid var(--sc-ink); }
.sc-table th { text-align: left; font-weight: 700; color: var(--sc-ink); padding: 0.6rem 0.9rem;
  border-bottom: 1.5px solid var(--sc-ink); background: var(--sc-paper); }
.sc-table td { padding: 0.55rem 0.9rem; border-top: 1px solid var(--sc-line); vertical-align: top; }
.sc-table tbody tr:hover td { background: var(--sc-tape-soft); }
.sc-table td:first-child { white-space: nowrap; }
.sc-table td.sc-num { text-align: right; font-variant-numeric: tabular-nums; }

.sc-timeline { list-style: none; padding: 0; margin: 0.4rem 0; }
.sc-step { display: grid; grid-template-columns: 2.4rem 11rem 1fr; gap: 0.8rem; align-items: start;
  padding: 0.55rem 0.8rem; border-left: 5px solid var(--sc-line); background: var(--sc-surface); margin-bottom: 0.3rem; }
.sc-step-no { font-weight: 700; color: var(--sc-muted); font-family: var(--sc-mono); }
.sc-step-kind { font-weight: 700; font-size: 1.05rem; }
.sc-step code { white-space: pre-wrap; word-break: break-word; font-size: 0.92rem; background: transparent; }
.sc-step-bad { border-left-color: var(--sc-bad); background: var(--sc-bad-soft); }
.sc-step-warn { border-left-color: var(--sc-warn); background: var(--sc-warn-soft); }
.sc-step-info { border-left-color: var(--sc-petrol); }

.sc-chain { font-family: var(--sc-mono); font-size: 0.95rem; line-height: 2; }
.sc-chain span { padding: 0.1rem 0.45rem; border-radius: 3px; background: var(--sc-idle-soft); }
.sc-chain span.sc-hot { background: var(--sc-bad-soft); color: var(--sc-bad); font-weight: 600; }

.sc-placeholder { border: 2px dashed var(--sc-petrol); border-radius: 4px; padding: 1.3rem 1.5rem; background: var(--sc-surface); }
.sc-placeholder h4 { font-size: 1.25rem; margin: 0 0 0.3rem; padding: 0; }
.sc-placeholder p { color: var(--sc-muted); margin: 0 0 0.5rem; }
.sc-placeholder code { font-size: 0.92rem; }

/* Sidebar: dark petrol panel, the active page is marked with tape */
[data-testid="stSidebar"] { background: var(--sc-petrol-deep); border-right: 0; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p, [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] > p { color: #E6EFEE; }
[data-testid="stSidebar"] hr { border-color: rgba(255, 255, 255, 0.18); }
[data-testid="stSidebar"] [role="radiogroup"] label { padding: 0.45rem 0.6rem; margin: 0 0 0.15rem; border-radius: 3px;
  border-left: 5px solid transparent; }
[data-testid="stSidebar"] [role="radiogroup"] label p { color: #CFE0DE; font-size: 1.1rem; font-weight: 600; }
[data-testid="stSidebar"] [role="radiogroup"] label[data-selected="true"] { background: rgba(255, 255, 255, 0.08); border-left-color: var(--sc-tape); }
[data-testid="stSidebar"] [role="radiogroup"] label[data-selected="true"] p { color: #FFFFFF; }
[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:not([data-testid="stMarkdownContainer"]) { display: none; }
[data-testid="stSidebar"] .stButton > button { background: transparent; color: #E6EFEE; border-color: rgba(255, 255, 255, 0.45); }
[data-testid="stSidebar"] .stButton > button:hover { background: rgba(255, 255, 255, 0.1); color: #FFFFFF; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] { background: var(--sc-tape); color: var(--sc-ink); border-color: var(--sc-tape); }

.sc-brand { color: #FFFFFF; padding: 0.2rem 0 0.9rem; margin-bottom: 0.6rem; border-bottom: 1px solid rgba(255, 255, 255, 0.18); }
.sc-brand strong { display: block; font-size: 1.45rem; font-weight: 800; letter-spacing: -0.02em; }
.sc-brand span { font-size: 0.95rem; color: #A9C3C0; }
.sc-crew { margin-top: 0.6rem; }
.sc-crew div { display: flex; justify-content: space-between; gap: 0.6rem; font-size: 0.92rem; color: #CFE0DE; padding: 0.15rem 0; }
.sc-crew div span:last-child { font-family: var(--sc-mono); color: #A9C3C0; }
.sc-crew div.sc-crew-todo span { color: #7F9C99; font-style: italic; }

.sc-side-claim { background: var(--sc-surface); border-left: 6px solid var(--sc-tape); border-radius: 3px;
  padding: 0.6rem 0.8rem; margin: 0.4rem 0 0.8rem; color: var(--sc-ink); }
.sc-side-claim div { display: flex; justify-content: space-between; gap: 0.6rem; padding: 0.2rem 0; font-size: 1rem; }
.sc-side-claim span { color: var(--sc-muted); }
.sc-chat-head { margin-bottom: 1rem; }
.sc-muted { color: var(--sc-muted); }
[data-testid="stChatMessage"] { background: var(--sc-surface); border: 1.5px solid var(--sc-line); border-radius: 4px;
  padding: 0.9rem 1.1rem; margin-bottom: 0.7rem; }

.sc-calls { list-style: none; padding: 0; margin: 0.2rem 0; }
.sc-call { display: grid; grid-template-columns: 2rem 10.5rem 1fr auto; gap: 0.7rem; align-items: start;
  padding: 0.45rem 0.7rem; margin-bottom: 0.25rem; border-left: 5px solid var(--sc-line); background: var(--sc-paper); font-size: 1rem; }
.sc-call-no { font-weight: 700; color: var(--sc-muted); font-family: var(--sc-mono); }
.sc-call-kind { font-weight: 600; white-space: nowrap; }
.sc-call-body strong { margin-right: 0.5rem; }
.sc-call-body code { white-space: pre-wrap; word-break: break-word; font-size: 0.88rem; background: transparent; }
.sc-call-cost { font-family: var(--sc-mono); font-size: 0.88rem; color: var(--sc-muted); white-space: nowrap; }
.sc-call-tool { border-left-color: var(--sc-petrol); }
.sc-call-model { border-left-color: #6B4FA0; background: #EEEAF5; }
.sc-call-host { border-left-color: var(--sc-ok); background: var(--sc-ok-soft); }
.sc-call-trace { border-left-color: var(--sc-line); }
.sc-call-hot { border-left-color: var(--sc-bad); background: var(--sc-bad-soft); }

.sc-metrics { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); margin: 0.8rem 0 0.5rem;
  border: 1.5px solid var(--sc-ink); border-radius: 3px; background: var(--sc-surface); }
.sc-metric { padding: 0.5rem 0.7rem; border-left: 1px dashed var(--sc-line); }
.sc-metric:first-child { border-left: 0; }
.sc-metric span { display: block; font-size: 0.88rem; color: var(--sc-muted); }
.sc-metric strong { font-size: 1.15rem; font-variant-numeric: tabular-nums; }
.sc-expect { display: flex; flex-wrap: wrap; align-items: center; gap: 0.8rem; font-size: 1rem; margin-bottom: 0.4rem; }
@media (max-width: 900px) { .sc-metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .sc-call { grid-template-columns: 1.6rem 1fr; } }

.sc-heat td.sc-cell { width: 2.2rem; height: 2.2rem; padding: 0; text-align: center; font-size: 0.9rem; }
.sc-cell-pass { background: var(--sc-ok-soft); color: var(--sc-ok); }
.sc-cell-fail { background: var(--sc-bad); color: #FFFFFF; font-weight: 700; }
.sc-cell-none { background: var(--sc-idle-soft); color: var(--sc-idle); }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
</style>
"""


def inject_theme() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)
