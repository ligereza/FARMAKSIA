"""Closed bridge from the existing GazeSample to the geometry-first contract."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from gaze_geometry import GazeObservation, GazeState, MonitorLayout, resolve_gaze


@dataclass(frozen=True)
class BridgeResult:
    state: GazeState | None
    status: str
    reason: str
    legacy_screen_mapping_allowed: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "state": None if self.state is None else self.state.as_dict(),
            "legacy_screen_mapping_allowed": self.legacy_screen_mapping_allowed,
        }


def _closed(reason: str) -> BridgeResult:
    return BridgeResult(None, "UNKNOWN", reason, False)


def bridge_sample(
    sample: Any,
    timestamp_capture: float,
    layout: MonitorLayout,
    *,
    left_eye_world: tuple[float, float, float] | None = None,
    right_eye_world: tuple[float, float, float] | None = None,
    gaze_direction_world: tuple[float, float, float] | None = None,
    uncertainty_deg: float = 3.0,
) -> BridgeResult:
    """Require world geometry; legacy image features never produce screen UV."""

    if sample is None:
        return _closed("sample_missing")
    quality = getattr(sample, "quality", None)
    if quality is None or not math.isfinite(float(quality)):
        return _closed("sample_quality_missing")
    if left_eye_world is None or right_eye_world is None or gaze_direction_world is None:
        return _closed("missing_world_geometry")
    if not math.isfinite(float(timestamp_capture)):
        return _closed("invalid_timestamp")
    observation = GazeObservation(
        timestamp_capture=float(timestamp_capture),
        left_eye_world=left_eye_world,
        right_eye_world=right_eye_world,
        gaze_direction_world=gaze_direction_world,
        confidence=max(0.0, min(1.0, float(quality))),
        uncertainty_deg=uncertainty_deg,
        layout_version=layout.version,
        fixation_state="unknown",
        head_pose_valid=True,
    )
    state = resolve_gaze(observation, layout)
    return BridgeResult(state, state.status, state.unknown_reason or "geometry_resolved", False)
