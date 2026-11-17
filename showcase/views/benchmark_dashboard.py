"""Tab 5 - Benchmark: read src/reports/*.json written by lab8.benchmark. Never edits them.

Commands below are run inside src/.

Shows the by_shape summary and a claim x (shape, seed) heatmap so a red cell can be
traced back to the live failure shown earlier (C-002 seed 55 on swarm).
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from services import lab_runner as svc
from catalog.presets import SHAPE_LABELS
from ui.components import badge, cost_vnd, esc, html_block, html_table, placeholder, section_title

REPORTS = {
    "benchmark.json": ("Benchmark công khai", "python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm "
                       "--cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json"),
    "hidden_selfcheck.json": ("Hidden self-check", "python -m lab8.benchmark --shapes workflow,single,orchestrator "
                              "--cases student_drop/hidden_claims.jsonl --world student_drop/hidden_world_state.json "
                              "--out reports/hidden_selfcheck.json"),
    "bonus_benchmark_public.json": ("Bonus B3: swarm + verifier, bộ public", "python -m lab8.benchmark --shapes workflow,swarm,swarm_verified "
                             "--extra-shape swarm_verified=bonus.swarm_verified:run_claim "
                             "--seeds 11,22,33,44,55 --out reports/bonus_benchmark_public.json"),
    "bonus_benchmark_adversarial.json": ("Bonus B3: bộ đối kháng 8 claim", "python -m lab8.benchmark --shapes workflow,swarm,swarm_verified "
                               "--extra-shape swarm_verified=bonus.swarm_verified:run_claim "
                               "--cases bonus/cases.jsonl --world bonus/world.json "
                               "--seeds 11,22,33,44,55 --out reports/bonus_benchmark_adversarial.json"),
}


def _fmt(value: Any, kind: str = "num") -> str:
    if value is None:
        return "-"
    if kind == "pct":
        return f"{float(value) * 100:.1f}%"
    if kind == "money":
        return cost_vnd(value)
    if kind == "var":
        return f"{float(value):.4f}".replace(".", ",")
    return f"{float(value):.2f}" if isinstance(value, float) else str(value)


def _summary_table(by_shape: dict[str, Any]) -> None:
    rows = []
    for shape, stats in by_shape.items():
        rows.append({
            "shape": SHAPE_LABELS.get(shape, shape),
            "pass": _fmt(stats.get("pass_rate"), "pct"),
            "pass5": _fmt(stats.get("pass_5"), "pct"),
            "var": _fmt(stats.get("seed_variance"), "var"),
            "cost": _fmt(stats.get("cost_per_success_vnd"), "money"),
            "steps": _fmt(stats.get("mean_steps")),
            "p95": _fmt(stats.get("p95_steps")),
            "model": _fmt(stats.get("mean_model_calls")),
            "errors": stats.get("error_trials", "-"),
            "leaks": stats.get("leak_suspect_trials", "-"),
        })
    html_table(
        rows,
        [("shape", "Shape"), ("pass", "Pass rate"), ("pass5", "pass^5"), ("var", "Var seed"),
         ("cost", "Cost/success"), ("steps", "Steps TB"), ("p95", "p95 steps"), ("model", "Model call TB"),
         ("errors", "Error"), ("leaks", "Leak")],
        numeric={"pass", "pass5", "var", "cost", "steps", "p95", "model", "errors", "leaks"},
    )


def _heatmap(trials: list[dict[str, Any]]) -> None:
    """Rows = claims, columns = shape/seed. Green pass, red fail, grey unlabeled."""
    shapes = list(dict.fromkeys(t["shape"] for t in trials))
    seeds = sorted({t["seed"] for t in trials})
    claims = list(dict.fromkeys(t["claim_id"] for t in trials))
    cell = {(t["claim_id"], t["shape"], t["seed"]): t for t in trials}
    head_top = "".join(f'<th colspan="{len(seeds)}">{esc(shape)}</th>' for shape in shapes)
    head_seed = "".join(f"<th>{seed}</th>" for _ in shapes for seed in seeds)
    body = []
    for claim_id in claims:
        tds = []
        for shape in shapes:
            for seed in seeds:
                trial = cell.get((claim_id, shape, seed), {})
                passed = trial.get("passed")
                css = "sc-cell-pass" if passed is True else ("sc-cell-fail" if passed is False else "sc-cell-none")
                mark = "" if passed is True else ("x" if passed is False else "?")
                tip = esc(f"{shape} seed {seed}: {trial.get('status', '-')} · {trial.get('reason', '-')}")
                tds.append(f'<td class="sc-cell {css}" title="{tip}">{mark}</td>')
        body.append(f"<tr><td class=\"sc-id\"><strong>{esc(claim_id)}</strong></td>{''.join(tds)}</tr>")
    html_block(
        f'<table class="sc-table sc-heat"><thead><tr><th rowspan="2">Claim</th>{head_top}</tr>'
        f'<tr>{head_seed}</tr></thead><tbody>{"".join(body)}</tbody></table>'
    )


def _render_report(name: str) -> None:
    title, command = REPORTS[name]
    section_title(title, f"Nguồn: src/reports/{name}")
    report = svc.load_report(name)
    if not report:
        placeholder(f"Chưa có src/reports/{name}",
                    "Chạy lệnh dưới đây trong src/ rồi tải lại trang. Không sửa tay file JSON.", command)
        return
    variables = report.get("controlled_variables") or {}
    html_block(
        f'<p>{badge(variables.get("model_backend", "?"), "info")} '
        f'{badge("seeds " + ", ".join(map(str, variables.get("seeds", []))), "idle")} '
        f'{badge(variables.get("isolation", "?"), "idle")} {badge("cost mô phỏng", "warn")}</p>'
    )
    _summary_table(report.get("by_shape") or {})
    trials = report.get("trials") or []
    if trials:
        with st.expander("Heatmap từng trial (claim x shape x seed)", expanded=(name == "benchmark.json")):
            _heatmap(trials)


def render() -> None:
    for name in REPORTS:
        _render_report(name)
        st.divider()
