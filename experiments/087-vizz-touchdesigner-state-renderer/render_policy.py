"""Bounded visual policy for the 087 normalized state.

The output is a presentation plan, not a gaze claim. Every value is bounded;
UNKNOWN, an unselected source or a missing overlay permission returns a neutral
plan. The heuristic weights are engineering defaults and require perceptual
validation later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class RenderPolicy:
    max_parallax: float = 0.05
    max_depth_scale_delta: float = 0.02
    max_context_dim: float = 0.18
    pointer_activity_weight: float = 0.35


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def neutral_plan(reason: str = "STATE_UNKNOWN") -> dict[str, float | str]:
    return {
        "status": "NEUTRAL",
        "reason": reason,
        "adaptation_enabled": 0.0,
        "parallax_x": 0.0,
        "parallax_y": 0.0,
        "depth_scale": 1.0,
        "focus_weight": 0.0,
        "context_dim": 0.0,
        "activity_signal": 0.0,
        "critical_sharpness": 1.0,
    }


def compute_plan(state: Mapping[str, Any], policy: RenderPolicy | None = None) -> dict[str, float | str]:
    """Turn normalized state into a bounded, explainable visual plan."""

    policy = policy or RenderPolicy()
    if state.get("status") != "VALID":
        return neutral_plan(str(state.get("reason") or "STATE_UNKNOWN"))
    permissions = state.get("permissions", {})
    window = state.get("window", {})
    if not permissions.get("overlay", False):
        return neutral_plan("OVERLAY_PERMISSION_MISSING")
    if not window.get("selected", False):
        return neutral_plan("SOURCE_NOT_SELECTED")

    confidence = _clamp(float(state.get("confidence", 0.0)), 0.0, 1.0)
    confidence_gain = _clamp((confidence - 0.25) / 0.75, 0.0, 1.0)
    head = state.get("head", {})
    focus = state.get("focus", {})
    input_state = state.get("input", {})
    focus_weight = _clamp(float(focus.get("interest", 0.0)) * confidence_gain, 0.0, 1.0)
    activity_signal = _clamp(
        max(
            float(input_state.get("keyboard_activity", 0.0)),
            float(input_state.get("pointer_active", 0.0)) * policy.pointer_activity_weight,
        ),
        0.0,
        1.0,
    )
    return {
        "status": "ACTIVE",
        "reason": "",
        "adaptation_enabled": 1.0,
        "parallax_x": _clamp(float(head.get("x", 0.0)) * policy.max_parallax * confidence_gain, -policy.max_parallax, policy.max_parallax),
        "parallax_y": _clamp(float(head.get("y", 0.0)) * policy.max_parallax * confidence_gain, -policy.max_parallax, policy.max_parallax),
        "depth_scale": 1.0 + _clamp(float(head.get("z", 0.0)) * policy.max_depth_scale_delta * confidence_gain, -policy.max_depth_scale_delta, policy.max_depth_scale_delta),
        "focus_weight": focus_weight,
        "context_dim": focus_weight * _clamp(policy.max_context_dim, 0.0, 1.0),
        "activity_signal": activity_signal,
        "critical_sharpness": 1.0,
    }
