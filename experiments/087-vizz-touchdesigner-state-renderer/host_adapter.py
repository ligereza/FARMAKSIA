"""Translate already-observed VIZZ signals into the 087 state payload.

This adapter does not obtain the signals. The existing GPU tracker, UIA/input
observer or a future screen mapper must provide them explicitly. In particular,
eye-centre coordinates are not silently promoted to gaze focus.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence


SCHEMA = "farmaxia:vizz-state:0.1"


def _finite(value: Any) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("non-finite signal")
    return result


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _head_from_tracker_pose(pose: Sequence[float], reference_face_width: float | None = None) -> dict[str, float]:
    """Map the current tracker pose tuple to a bounded relative pose.

    The current tuple is `(face_cx, face_cy, face_w, face_h, eye_roll_pi,
    eye_distance)`, all normalized to the camera frame. It does not contain
    metric depth, yaw or pitch; the missing components remain neutral rather
    than being invented.
    """

    if len(pose) != 6:
        raise ValueError("tracker pose must contain six normalized values")
    face_cx, face_cy, face_w, _face_h, eye_roll_pi, _eye_distance = (_finite(value) for value in pose)
    if not 0.0 < face_w <= 1.0:
        raise ValueError("face width must be in (0, 1]")
    if reference_face_width is None:
        relative_z = 0.0
    else:
        reference = _finite(reference_face_width)
        if not 0.0 < reference <= 1.0:
            raise ValueError("reference face width must be in (0, 1]")
        relative_z = _clamp(reference / face_w - 1.0, -1.0, 1.0)
    return {
        "x": _clamp((face_cx - 0.5) * 2.0, -1.0, 1.0),
        "y": _clamp((0.5 - face_cy) * 2.0, -1.0, 1.0),
        "z": relative_z,
        "rx": _clamp(eye_roll_pi * 180.0, -180.0, 180.0),
        "ry": 0.0,
        "rz": 0.0,
    }


def _neutral_focus() -> dict[str, float]:
    return {"x": 0.5, "y": 0.5, "w": 0.0, "h": 0.0, "interest": 0.0}


def _focus(value: Mapping[str, Any] | None) -> dict[str, float]:
    """Accept focus only from an explicit screen mapper output."""

    if value is None:
        return _neutral_focus()
    output = {key: _finite(value[key]) for key in ("x", "y", "w", "h", "interest")}
    if any(not 0.0 <= output[key] <= 1.0 for key in output):
        raise ValueError("focus values must be in [0, 1]")
    if output["x"] + output["w"] > 1.0 or output["y"] + output["h"] > 1.0:
        raise ValueError("focus rectangle is outside the source")
    return output


def build_payload(
    *,
    seq: int,
    timestamp_monotonic_ms: float,
    source: str,
    confidence: float,
    head: Mapping[str, Any],
    focus: Mapping[str, Any] | None,
    keyboard_activity: float,
    pointer_x: float,
    pointer_y: float,
    pointer_active: bool,
    window: Mapping[str, Any],
    permissions: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the narrow payload consumed by `state_router.normalize_state`."""

    if isinstance(seq, bool) or not isinstance(seq, int) or seq < 0:
        raise ValueError("seq must be a non-negative integer")
    if not isinstance(pointer_active, bool):
        raise ValueError("pointer_active must be boolean")
    bounded_confidence = _clamp(_finite(confidence), 0.0, 1.0)
    return {
        "schema": SCHEMA,
        "seq": seq,
        "timestamp_monotonic_ms": _finite(timestamp_monotonic_ms),
        "source": source,
        "confidence": bounded_confidence,
        "head": {key: _finite(head[key]) for key in ("x", "y", "z", "rx", "ry", "rz")},
        "focus": _focus(focus),
        "input": {
            "keyboard_activity": _clamp(_finite(keyboard_activity), 0.0, 1.0),
            "pointer_x": _clamp(_finite(pointer_x), 0.0, 1.0),
            "pointer_y": _clamp(_finite(pointer_y), 0.0, 1.0),
            "pointer_active": pointer_active,
        },
        "window": dict(window),
        "permissions": dict(permissions),
    }


def from_tracker_observation(
    *,
    seq: int,
    timestamp_monotonic_ms: float,
    pose: Sequence[float],
    quality: float,
    reference_face_width: float | None = None,
    focus: Mapping[str, Any] | None = None,
    keyboard_activity: float = 0.0,
    pointer_x: float = 0.5,
    pointer_y: float = 0.5,
    pointer_active: bool = False,
    window: Mapping[str, Any],
    permissions: Mapping[str, Any],
) -> dict[str, Any]:
    """Adapt a tracker observation without claiming that it is gaze focus."""

    return build_payload(
        seq=seq,
        timestamp_monotonic_ms=timestamp_monotonic_ms,
        source="face_track",
        confidence=quality,
        head=_head_from_tracker_pose(pose, reference_face_width),
        focus=focus,
        keyboard_activity=keyboard_activity,
        pointer_x=pointer_x,
        pointer_y=pointer_y,
        pointer_active=pointer_active,
        window=window,
        permissions=permissions,
    )


def from_geometry_state(
    *,
    seq: int,
    timestamp_monotonic_ms: float,
    geometry_state: Mapping[str, Any],
    head: Mapping[str, Any],
    keyboard_activity: float = 0.0,
    pointer_x: float = 0.5,
    pointer_y: float = 0.5,
    pointer_active: bool = False,
    window: Mapping[str, Any],
    permissions: Mapping[str, Any],
) -> dict[str, Any]:
    """Adapt the 046 geometry result and preserve UNKNOWN monitor states.

    A valid `uv` is the only accepted source for focus. Monitor identity and
    layout remain metadata in `window`; the adapter never chooses a monitor
    when 046 reported ambiguity or no intersection.
    """

    valid = geometry_state.get("status") == "VALID"
    uv = geometry_state.get("uv")
    if valid and isinstance(uv, (list, tuple)) and len(uv) == 2:
        focus = {"x": _finite(uv[0]), "y": _finite(uv[1]), "w": 0.0, "h": 0.0, "interest": 1.0}
        quality = _clamp(_finite(geometry_state.get("confidence", 0.0)), 0.0, 1.0)
    else:
        focus = None
        quality = 0.0
    return build_payload(
        seq=seq,
        timestamp_monotonic_ms=timestamp_monotonic_ms,
        source="combined",
        confidence=quality,
        head=head,
        focus=focus,
        keyboard_activity=keyboard_activity,
        pointer_x=pointer_x,
        pointer_y=pointer_y,
        pointer_active=pointer_active,
        window=window,
        permissions=permissions,
    )
