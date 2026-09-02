"""Bounded render-rate decisions for the future transparent LUCIDA surface."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping


DEFAULT_MAX_HZ = 30
MIN_MAX_HZ = 1
MAX_MAX_HZ = 60
PLAN_FIELDS = {
    "contractType",
    "schemaVersion",
    "surface",
    "mode",
    "sessionId",
    "phase",
    "viewDigest",
    "transparent",
    "clickThrough",
    "blocking",
    "intensity",
    "elements",
    "safety",
}
SAFETY_FIELDS = {
    "proposalOnly",
    "automaticActions",
    "externalSideEffects",
    "rawPayloadIncluded",
}
FORBIDDEN_KEYS = {"payload", "command", "shell", "action", "coordinates"}


class LucidaRenderBudgetError(ValueError):
    """Raised when a render-rate decision cannot be evaluated safely."""


def assess_render_update(
    previous_plan: Mapping[str, Any] | None,
    current_plan: Mapping[str, Any],
    *,
    elapsed_ms: int | float | None,
    max_hz: int = DEFAULT_MAX_HZ,
) -> dict[str, Any]:
    """Return a pure emit, drop or coalesce decision for one render plan.

    The caller owns scheduling and rendering. This function never sleeps,
    opens a window or retains the plan. A changed plan arriving before the
    minimum interval is held as the newest candidate for the next tick.
    """

    _validate_plan(current_plan, "current_plan")
    interval_ms = _minimum_interval_ms(max_hz)
    current_digest = _plan_digest(current_plan)
    previous_digest = None

    if previous_plan is None:
        decision = "emit"
        reason = "initial-plan"
    else:
        _validate_plan(previous_plan, "previous_plan")
        previous_digest = _plan_digest(previous_plan)
        if current_digest == previous_digest:
            decision = "drop_unchanged"
            reason = "plan-digest-unchanged"
        else:
            elapsed = _elapsed(elapsed_ms)
            if elapsed < interval_ms:
                decision = "hold_coalesced"
                reason = "minimum-render-interval-not-reached"
            else:
                decision = "emit"
                reason = "changed-plan-within-budget"

    return {
        "contractType": "LucidaRenderBudgetDecision",
        "schemaVersion": 1,
        "decision": decision,
        "reason": reason,
        "planDigest": current_digest,
        "previousPlanDigest": previous_digest,
        "elapsedMs": elapsed_ms,
        "minimumIntervalMs": interval_ms,
        "maxHz": max_hz,
        "retainsPlan": False,
        "opensWindow": False,
        "executesHostAction": False,
    }


def _minimum_interval_ms(max_hz: int) -> int:
    if isinstance(max_hz, bool) or not isinstance(max_hz, int):
        raise LucidaRenderBudgetError("max_hz must be an integer")
    if not MIN_MAX_HZ <= max_hz <= MAX_MAX_HZ:
        raise LucidaRenderBudgetError("max_hz is outside the supported budget")
    return math.ceil(1000 / max_hz)


def _elapsed(value: int | float | None) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise LucidaRenderBudgetError("elapsed_ms is required for a changed plan")
    if not math.isfinite(value) or value < 0:
        raise LucidaRenderBudgetError("elapsed_ms must be finite and non-negative")
    return value


def _validate_plan(plan: Mapping[str, Any], field_name: str) -> None:
    if not isinstance(plan, Mapping):
        raise LucidaRenderBudgetError(f"{field_name} must be a mapping")
    if set(plan) != PLAN_FIELDS:
        raise LucidaRenderBudgetError(f"{field_name} contains unsupported or missing fields")
    if plan["contractType"] != "LucidaRenderPlan" or plan["schemaVersion"] != 1:
        raise LucidaRenderBudgetError(f"{field_name} contract is invalid")
    if plan["surface"] != "LUCIDA" or plan["mode"] != "read_only":
        raise LucidaRenderBudgetError(f"{field_name} surface is invalid")
    if not isinstance(plan["viewDigest"], str) or not plan["viewDigest"].strip():
        raise LucidaRenderBudgetError(f"{field_name}.viewDigest is invalid")
    if plan["transparent"] is not True or plan["clickThrough"] is not True:
        raise LucidaRenderBudgetError(f"{field_name} must remain transparent and click-through")
    if plan["blocking"] is not False:
        raise LucidaRenderBudgetError(f"{field_name} cannot be blocking")
    elements = plan["elements"]
    if not isinstance(elements, list) or len(elements) > 8:
        raise LucidaRenderBudgetError(f"{field_name}.elements exceed the render bound")
    safety = plan["safety"]
    if not isinstance(safety, Mapping) or set(safety) != SAFETY_FIELDS:
        raise LucidaRenderBudgetError(f"{field_name}.safety is invalid")
    if (
        safety["proposalOnly"] is not True
        or safety["automaticActions"] is not False
        or safety["externalSideEffects"] is not False
        or safety["rawPayloadIncluded"] is not False
    ):
        raise LucidaRenderBudgetError(f"{field_name}.safety violates the render boundary")
    _reject_forbidden_keys(plan)


def _plan_digest(plan: Mapping[str, Any]) -> str:
    try:
        serialized = json.dumps(
            plan,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise LucidaRenderBudgetError("render plan must be JSON serializable") from exc
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _reject_forbidden_keys(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                raise LucidaRenderBudgetError(f"unsafe field in render plan: {key}")
            _reject_forbidden_keys(child)
    elif isinstance(value, list):
        for child in value:
            _reject_forbidden_keys(child)


__all__ = [
    "DEFAULT_MAX_HZ",
    "LucidaRenderBudgetError",
    "assess_render_update",
]
