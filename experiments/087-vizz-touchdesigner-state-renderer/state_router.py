"""Pure VIZZ state contract.

This module deliberately has no camera, window, socket, TouchDesigner or input
dependency. It converts a candidate payload into a small renderer state or an
explicit UNKNOWN state. Raw keys are never forwarded to the renderer.
"""

from __future__ import annotations

import math
import time
from typing import Any, Mapping


SCHEMA = "farmaxia:vizz-state:0.1"
MIN_CONFIDENCE = 0.25
DEFAULT_MAX_AGE_MS = 500.0
FUTURE_TOLERANCE_MS = 1000.0
SOURCES = {"manual", "face_track", "uia", "input", "combined"}


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def _bounded(value: Any, low: float, high: float) -> float | None:
    result = _number(value)
    if result is None or result < low or result > high:
        return None
    return result


def _integer(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _boolean(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def _string(value: Any, max_length: int = 128) -> str | None:
    if not isinstance(value, str) or not value or len(value) > max_length:
        return None
    return value


def _require_mapping(value: Any) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None


def _head(value: Any) -> dict[str, float] | None:
    group = _require_mapping(value)
    if group is None:
        return None
    ranges = {
        "x": (-1.0, 1.0),
        "y": (-1.0, 1.0),
        "z": (-1.0, 1.0),
        "rx": (-180.0, 180.0),
        "ry": (-180.0, 180.0),
        "rz": (-180.0, 180.0),
    }
    output: dict[str, float] = {}
    for key, (low, high) in ranges.items():
        parsed = _bounded(group.get(key), low, high)
        if parsed is None:
            return None
        output[key] = parsed
    return output


def _focus(value: Any) -> dict[str, float] | None:
    group = _require_mapping(value)
    if group is None:
        return None
    output: dict[str, float] = {}
    for key in ("x", "y", "w", "h", "interest"):
        parsed = _bounded(group.get(key), 0.0, 1.0)
        if parsed is None:
            return None
        output[key] = parsed
    if output["x"] + output["w"] > 1.0 or output["y"] + output["h"] > 1.0:
        return None
    return output


def _input(value: Any) -> dict[str, float | bool] | None:
    group = _require_mapping(value)
    if group is None:
        return None
    output: dict[str, float | bool] = {}
    for key in ("keyboard_activity", "pointer_x", "pointer_y"):
        parsed = _bounded(group.get(key), 0.0, 1.0)
        if parsed is None:
            return None
        output[key] = parsed
    pointer_active = _boolean(group.get("pointer_active"))
    if pointer_active is None:
        return None
    output["pointer_active"] = pointer_active
    return output


def _window(value: Any) -> dict[str, Any] | None:
    group = _require_mapping(value)
    if group is None:
        return None
    selected = _boolean(group.get("selected"))
    monitor_id = _string(group.get("monitor_id"))
    rect = _require_mapping(group.get("source_rect"))
    if selected is None or monitor_id is None or rect is None:
        return None
    left = rect.get("left")
    top = rect.get("top")
    width = _integer(rect.get("width"))
    height = _integer(rect.get("height"))
    if not isinstance(left, int) or isinstance(left, bool):
        return None
    if not isinstance(top, int) or isinstance(top, bool):
        return None
    if width is None or height is None or width == 0 or height == 0:
        return None
    return {
        "selected": selected,
        "monitor_id": monitor_id,
        "source_rect": {"left": left, "top": top, "width": width, "height": height},
    }


def _permissions(value: Any) -> dict[str, bool] | None:
    group = _require_mapping(value)
    if group is None:
        return None
    output: dict[str, bool] = {}
    for key in ("camera", "capture", "overlay", "input_remap"):
        parsed = _boolean(group.get(key))
        if parsed is None:
            return None
        output[key] = parsed
    return output


def _unknown(reason: str, *, seq: int = 0, timestamp: float = 0.0) -> dict[str, Any]:
    """Return a safe state that cannot move the renderer."""

    return {
        "schema": SCHEMA,
        "status": "UNKNOWN",
        "reason": reason,
        "seq": seq,
        "timestamp_monotonic_ms": timestamp,
        "source": "unknown",
        "confidence": 0.0,
        "head": {"x": 0.0, "y": 0.0, "z": 0.0, "rx": 0.0, "ry": 0.0, "rz": 0.0},
        "focus": {"x": 0.5, "y": 0.5, "w": 0.0, "h": 0.0, "interest": 0.0},
        "input": {
            "keyboard_activity": 0.0,
            "pointer_x": 0.5,
            "pointer_y": 0.5,
            "pointer_active": False,
        },
        "window": {
            "selected": False,
            "monitor_id": "unknown",
            "source_rect": {"left": 0, "top": 0, "width": 1, "height": 1},
        },
        "permissions": {"camera": False, "capture": False, "overlay": False, "input_remap": False},
    }


def normalize_state(
    payload: Mapping[str, Any] | Any,
    *,
    now_monotonic_ms: float | None = None,
    max_age_ms: float = DEFAULT_MAX_AGE_MS,
) -> dict[str, Any]:
    """Validate and minimize a candidate state for the renderer.

    The function intentionally returns UNKNOWN instead of guessing. `payload`
    may contain extra keys, but they are not copied into the result.
    """

    if not isinstance(payload, Mapping):
        return _unknown("PAYLOAD_NOT_OBJECT")
    seq = _integer(payload.get("seq"))
    timestamp = _bounded(payload.get("timestamp_monotonic_ms"), 0.0, float("inf"))
    if seq is None or timestamp is None:
        return _unknown("MISSING_CLOCK_OR_SEQUENCE", seq=seq or 0, timestamp=timestamp or 0.0)
    if payload.get("schema") != SCHEMA:
        return _unknown("SCHEMA_MISMATCH", seq=seq, timestamp=timestamp)
    source = payload.get("source")
    if source not in SOURCES:
        return _unknown("SOURCE_UNKNOWN", seq=seq, timestamp=timestamp)
    confidence = _bounded(payload.get("confidence"), 0.0, 1.0)
    if confidence is None:
        return _unknown("CONFIDENCE_INVALID", seq=seq, timestamp=timestamp)
    now = time.monotonic() * 1000.0 if now_monotonic_ms is None else _number(now_monotonic_ms)
    if now is None or timestamp > now + FUTURE_TOLERANCE_MS:
        return _unknown("CLOCK_MISMATCH", seq=seq, timestamp=timestamp)
    if timestamp < now - max(0.0, float(max_age_ms)):
        return _unknown("STATE_STALE", seq=seq, timestamp=timestamp)
    if confidence < MIN_CONFIDENCE:
        return _unknown("CONFIDENCE_TOO_LOW", seq=seq, timestamp=timestamp)

    head = _head(payload.get("head"))
    focus = _focus(payload.get("focus"))
    input_state = _input(payload.get("input"))
    window = _window(payload.get("window"))
    permissions = _permissions(payload.get("permissions"))
    if any(value is None for value in (head, focus, input_state, window, permissions)):
        return _unknown("STATE_GROUP_INVALID", seq=seq, timestamp=timestamp)

    return {
        "schema": SCHEMA,
        "status": "VALID",
        "reason": "",
        "seq": seq,
        "timestamp_monotonic_ms": timestamp,
        "source": source,
        "confidence": confidence,
        "head": head,
        "focus": focus,
        "input": input_state,
        "window": window,
        "permissions": permissions,
    }


def to_channels(state: Mapping[str, Any]) -> dict[str, float]:
    """Flatten only normalized values into renderer channels."""

    status = state.get("status")
    head = state.get("head", {})
    focus = state.get("focus", {})
    input_state = state.get("input", {})
    permissions = state.get("permissions", {})
    return {
        "state_valid": 1.0 if status == "VALID" else 0.0,
        "state_unknown": 0.0 if status == "VALID" else 1.0,
        "state_confidence": float(state.get("confidence", 0.0)),
        "head_x": float(head.get("x", 0.0)),
        "head_y": float(head.get("y", 0.0)),
        "head_z": float(head.get("z", 0.0)),
        "head_rx": float(head.get("rx", 0.0)),
        "head_ry": float(head.get("ry", 0.0)),
        "head_rz": float(head.get("rz", 0.0)),
        "focus_x": float(focus.get("x", 0.5)),
        "focus_y": float(focus.get("y", 0.5)),
        "focus_w": float(focus.get("w", 0.0)),
        "focus_h": float(focus.get("h", 0.0)),
        "focus_interest": float(focus.get("interest", 0.0)),
        "keyboard_activity": float(input_state.get("keyboard_activity", 0.0)),
        "pointer_x": float(input_state.get("pointer_x", 0.5)),
        "pointer_y": float(input_state.get("pointer_y", 0.5)),
        "pointer_active": 1.0 if input_state.get("pointer_active", False) else 0.0,
        "permission_camera": 1.0 if permissions.get("camera", False) else 0.0,
        "permission_capture": 1.0 if permissions.get("capture", False) else 0.0,
        "permission_overlay": 1.0 if permissions.get("overlay", False) else 0.0,
        "permission_input_remap": 1.0 if permissions.get("input_remap", False) else 0.0,
    }
