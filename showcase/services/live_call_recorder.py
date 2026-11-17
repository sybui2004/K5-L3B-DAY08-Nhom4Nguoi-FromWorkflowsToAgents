"""Record every tool call, MockLLM call, host write and trace event of one run, in order.

Demo-only instrumentation. It wraps lab8 functions inside the module namespaces the
shapes import them into (`from lab8.tools import lookup_order` binds a local name, so
patching lab8.tools alone would miss it). lab8 source files are untouched, so the
grader, benchmark and CLI behave exactly the same.

Rules:
- Wrappers are pass-through unless `record_calls()` is active in the current context
  (contextvars, so concurrent Streamlit sessions never mix their events).
- In lab8.tools only compute_compensation is patched (swarm imports it locally on its
  override path). No tool calls it internally, so this never double-counts; tools that
  call other tools (compute_compensation -> lookup_policy) stay invisible, matching the
  budget counters.
- Payloads keep allowlisted fields only and are scrubbed of the claim's forbidden
  tokens (canaries, phones, addresses) before the UI sees them.
"""

from __future__ import annotations

import contextvars
import functools
import importlib
import inspect
import json
import sqlite3
from contextlib import contextmanager
from typing import Any, Callable, Iterator

TOOL_NAMES = (
    "get_claim_view",
    "lookup_order",
    "lookup_refund_history",
    "lookup_policy",
    "get_clause",
    "compute_compensation",
)
# Consumer modules only. bonus.swarm_verified is optional and skipped when absent.
TARGET_MODULES = (
    "lab8.runtime",
    "lab8.shapes.workflow",
    "lab8.shapes.single",
    "lab8.shapes.orchestrator",
    "lab8.shapes.swarm_reference",
    "bonus.swarm_verified",
)
SAFE_ORDER_FIELDS = ("order_id", "status", "delay_days", "shipping_fee_vnd", "paid_vnd", "damage_verified")
SCALARS = (str, int, float, bool, type(None))
PROMPT_PREVIEW = 160

_active: contextvars.ContextVar[list[dict[str, Any]] | None] = contextvars.ContextVar("lx_calls", default=None)
_installed = False


def _emit(kind: str, name: str, payload: dict[str, Any]) -> None:
    events = _active.get()
    if events is not None:
        events.append({"kind": kind, "name": name, "payload": payload})


def _flat(value: Any) -> Any:
    """Keep scalars and one level of scalar dict/list; drop anything bigger."""
    if isinstance(value, SCALARS):
        return value
    if isinstance(value, dict):
        return {k: v for k, v in value.items() if isinstance(v, SCALARS)}
    if isinstance(value, (list, tuple)):
        return [v for v in value if isinstance(v, SCALARS)]
    return type(value).__name__


def _tool_args(fn: Callable[..., Any], args: tuple, kwargs: dict[str, Any]) -> dict[str, Any]:
    try:
        bound = inspect.signature(fn).bind(*args, **kwargs).arguments
    except TypeError:
        bound = {f"arg{i}": v for i, v in enumerate(args)} | kwargs
    shown: dict[str, Any] = {}
    for key, value in bound.items():
        if isinstance(value, sqlite3.Connection):
            continue
        if isinstance(value, dict):  # an order row passed to compute_compensation
            shown[key] = {"order_id": value.get("order_id")}
        else:
            shown[key] = _flat(value)
    return shown


def _tool_result(name: str, result: Any) -> Any:
    if not isinstance(result, dict):
        return _flat(result)
    if name == "get_claim_view":  # ticket is shown as the chat message already
        return {k: result.get(k) for k in ("found", "claim_id", "principal_id", "order_id") if k in result}
    if name == "lookup_order":
        order = result.get("order") or {}
        out = {k: result.get(k) for k in ("visible", "reason") if k in result}
        if order:
            out["order"] = {k: order.get(k) for k in SAFE_ORDER_FIELDS}
        return out
    if name == "compute_compensation":
        return {k: result.get(k) for k in ("amount_vnd", "reason", "clause_ids")}
    if name == "lookup_policy":
        return {"as_of": result.get("as_of"), "policies": [p.get("policy_id") for p in result.get("policies") or []]}
    return _flat(result)


def _wrap_tool(fn: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = fn(*args, **kwargs)
        if _active.get() is not None:
            from lab8.tools import tool_cost

            _emit("tool", fn.__name__, {
                "args": _tool_args(fn, args, kwargs),
                "result": _tool_result(fn.__name__, result),
                "cost": tool_cost(),
            })
        return result

    return wrapper


def _wrap_complete(fn: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        budget = args[0] if args else kwargs.get("budget")
        before = (budget.input_tokens, budget.output_tokens, budget.cost_estimate) if budget else (0, 0, 0.0)
        text = fn(*args, **kwargs)
        if budget is not None and _active.get() is not None:
            prompt = str(kwargs.get("prompt", ""))
            _emit("model", str(kwargs.get("purpose", "?")), {
                "seed": kwargs.get("seed"),
                "prompt": prompt if len(prompt) <= PROMPT_PREVIEW else prompt[: PROMPT_PREVIEW - 3] + "...",
                "output": text,
                "input_tokens": budget.input_tokens - before[0],
                "output_tokens": budget.output_tokens - before[1],
                "cost": round(budget.cost_estimate - before[2], 4),
            })
        return text

    return wrapper


def _wrap_refund(fn: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        amount = args[2] if len(args) > 2 else kwargs.get("amount_vnd", kwargs.get("amount"))
        crash_at = kwargs.get("crash_at")
        try:
            out = fn(*args, **kwargs)
        except Exception as exc:  # InjectedCrash: record it, then let the shape see it
            _emit("host", "issue_refund", {"amount_proposed": amount, "crash_at": crash_at, "raised": type(exc).__name__})
            raise
        effect = out.get("effect") if isinstance(out, dict) else None
        _emit("host", "issue_refund", {
            "amount_proposed": amount,
            "ok": out.get("ok"),
            "reason": out.get("reason"),
            "conflict": out.get("conflict"),
            "ledger_amount": dict(effect).get("amount_vnd") if effect else None,
        })
        return out

    return wrapper


def _patch(module: Any, name: str, factory: Callable[[Callable[..., Any]], Callable[..., Any]]) -> None:
    fn = getattr(module, name, None)
    if fn is None or getattr(fn, "_lx_wrapped", False):
        return
    wrapped = factory(fn)
    wrapped._lx_wrapped = True  # type: ignore[attr-defined]
    setattr(module, name, wrapped)


def install() -> None:
    """Idempotent. Call after lab8 is importable (services.lab_runner does the path bootstrap)."""
    global _installed
    if _installed:
        return
    for module_name in TARGET_MODULES:
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue
        for name in TOOL_NAMES:
            _patch(module, name, _wrap_tool)
        _patch(module, "complete", _wrap_complete)
        _patch(module, "issue_refund", _wrap_refund)
    _patch(importlib.import_module("lab8.tools"), "compute_compensation", _wrap_tool)

    from lab8.trace import Trace

    if not getattr(Trace.add, "_lx_wrapped", False):
        original_add = Trace.add

        def add(self: Any, kind: str, payload: dict[str, Any]) -> None:
            original_add(self, kind, payload)
            _emit("trace", kind, payload)

        add._lx_wrapped = True  # type: ignore[attr-defined]
        Trace.add = add  # type: ignore[method-assign]
    _installed = True


def _scrub(event: dict[str, Any], forbidden: list[str]) -> dict[str, Any]:
    text = json.dumps(event, ensure_ascii=False, default=str)
    for token in forbidden:
        text = text.replace(json.dumps(token, ensure_ascii=False)[1:-1], f"{token[:6]}***")
    return json.loads(text)


@contextmanager
def record_calls(forbidden: list[str]) -> Iterator[list[dict[str, Any]]]:
    """Collect events for the code run inside the block. The list is scrubbed on exit."""
    install()
    events: list[dict[str, Any]] = []
    token = _active.set(events)
    try:
        yield events
    finally:
        _active.reset(token)
        events[:] = [_scrub(event, forbidden) for event in events]
