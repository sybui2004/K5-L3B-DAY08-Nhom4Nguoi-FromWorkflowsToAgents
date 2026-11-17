"""Pieces of one assistant chat message: call timeline, reply text, 7-metric strip.

The reply sentence is a fixed template filled from RunResult and the ledger.
It is presentation only, not model output: no shape decides anything here.
"""

from __future__ import annotations

from typing import Any

from ui.components import badge, compact_json, cost_vnd, esc, money, status_badge

# kind -> (icon, label, tone class)
CALL_KINDS = {
    "tool": ("🔧", "Tool call", "tool"),
    "model": ("🧠", "Model call", "model"),
    "host": ("🏦", "Host ghi tiền", "host"),
    "trace": ("📝", "Trace event", "trace"),
}
HOT_TRACE = {"model_override", "crash", "error"}


def ledger_amount(outcome: dict[str, Any]) -> int:
    return sum(int(row["amount_vnd"]) for row in outcome["store"]["own_ledger"])


def call_counts(calls: list[dict[str, Any]]) -> dict[str, int]:
    counts = {kind: 0 for kind in CALL_KINDS}
    for call in calls:
        counts[call["kind"]] = counts.get(call["kind"], 0) + 1
    return counts


def timeline_html(calls: list[dict[str, Any]], charged_tools: int = 0) -> str:
    """Ordered list of every recorded call. Payloads are already allowlisted and scrubbed.

    charged_tools = RunResult.tool_calls. A shape may charge the budget for a raw SQL
    read without calling a tool function (swarm reads the claim row this way); such
    charges cannot be placed in the timeline, so they are reported in a footer line.
    """
    if not calls:
        return '<p class="sc-muted">Không ghi được sự kiện nào.</p>'
    unplaced = charged_tools - sum(1 for call in calls if call["kind"] == "tool")
    footer = (f'<p class="sc-muted">+{unplaced} tool call được tính vào budget nhưng không qua hàm tool '
              f'(shape tự đọc DB bằng SQL rồi cộng budget).</p>') if unplaced > 0 else ""
    items = []
    for index, call in enumerate(calls, start=1):
        icon, label, tone = CALL_KINDS.get(call["kind"], ("•", call["kind"], "trace"))
        payload = dict(call.get("payload") or {})
        cost = payload.pop("cost", None)
        hot = " sc-call-hot" if call["kind"] == "trace" and call["name"] in HOT_TRACE else ""
        cost_html = f'<span class="sc-call-cost">{esc(cost_vnd(cost))}</span>' if cost is not None else ""
        items.append(
            f'<li class="sc-call sc-call-{tone}{hot}">'
            f'<span class="sc-call-no">{index}</span>'
            f'<span class="sc-call-kind">{icon} {esc(label)}</span>'
            f'<span class="sc-call-body"><strong>{esc(call["name"])}</strong>'
            f'<code>{esc(compact_json(payload, 320))}</code></span>{cost_html}</li>'
        )
    return f'<ol class="sc-calls">{"".join(items)}</ol>{footer}'


def reply_text(outcome: dict[str, Any], claim: dict[str, Any]) -> str:
    """Customer-facing sentence built from the run outcome (template, not a model)."""
    if outcome.get("not_implemented"):
        return "Shape này chưa được cài, chưa thể xử lý yêu cầu."
    if outcome.get("crashed"):
        return (f"Tiến trình dừng đột ngột tại `{outcome['crashed']}`. "
                "Mở trang Durability để retry trên cùng DB và kiểm tra ledger không bị ghi 2 lần.")
    if outcome.get("error"):
        return f"Shape ném exception: `{outcome['error']}`."
    result = outcome.get("result") or {}
    status, quote = result.get("status"), int(result.get("proposal_amount") or 0)
    order, reason, paid = claim.get("order_id") or "không rõ", result.get("error_reason"), ledger_amount(outcome)
    if status == "resolved":
        text = f"LogiX đã hoàn **{money(paid)}** cho đơn {order}."
        if paid < quote:
            text += f" Mức được hưởng theo policy là {money(quote)}; host đã trừ phần hoàn trước đó hoặc cắt theo mức approval."
        return text
    if status == "denied" and quote > 0:
        return f"Đơn {order} được tính {money(quote)} theo policy, nhưng host từ chối chi trả (`{reason}`)."
    if status == "denied":
        return f"Rất tiếc, đơn {order} không đủ điều kiện bồi thường theo policy hiện hành (`{reason}`)."
    if status == "needs_info":
        return "Bạn vui lòng cung cấp mã đơn hàng để LogiX kiểm tra yêu cầu."
    if status == "escalated":
        return f"Yêu cầu đã được chuyển cho nhân viên hỗ trợ xem xét (`{reason}`)."
    return f"Hệ thống không xử lý được yêu cầu (`{reason}`). Chưa có khoản tiền nào được chuyển."


def metrics_strip_html(outcome: dict[str, Any]) -> str:
    """The 7 shared report fields: Status, Quote, Ledger, Model call, Tool call, Số bước, Cost."""
    result = outcome.get("result") or {}
    cells = [
        ("Status", status_badge(result.get("status")) if result else badge("không có", "idle")),
        ("Quote", esc(money(result.get("proposal_amount")) if result else "-")),
        ("Ledger", esc(money(ledger_amount(outcome)))),
        ("Model call", esc(result.get("model_calls", 0))),
        ("Tool call", esc(result.get("tool_calls", 0))),
        ("Số bước", esc(outcome["trace"].get("steps", 0))),
        ("Cost", esc(cost_vnd(result.get("cost_estimate", 0.0)))),
    ]
    body = "".join(f'<div class="sc-metric"><span>{esc(k)}</span><strong>{v}</strong></div>' for k, v in cells)
    return f'<div class="sc-metrics">{body}</div>'


def expected_line_html(outcome: dict[str, Any], expected: dict[str, Any], verdict_html: str) -> str:
    want = f'{status_badge(expected.get("status"))} {esc(money(expected.get("proposal_amount")))}'
    refund = esc(money(expected.get("refund_vnd")))
    return (f'<div class="sc-expect">{verdict_html}<span>Kỳ vọng: {want} · ledger {refund}</span>'
            f'<span class="sc-muted">trace: <code>{esc(outcome["trace"].get("path"))}</code></span></div>')
