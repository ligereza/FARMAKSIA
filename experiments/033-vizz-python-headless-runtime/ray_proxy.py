"""Relative binocular ray output for the CUDA tracker.

This module deliberately exposes a *proxy* camera frame.  The current webcam
pipeline has two eye-specific gaze angles and two image-space eye centres, but
it does not yet have calibrated intrinsics, metric eye depth, or a solved 3-D
head pose.  The output is therefore suitable for relative geometry and
quality-gating only.  It must not be reported as a metric world ray.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


Vec3 = tuple[float, float, float]


def _finite(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _unit(vector: Vec3) -> Vec3 | None:
    length = math.sqrt(sum(component * component for component in vector))
    if not math.isfinite(length) or length <= 1e-9:
        return None
    return tuple(component / length for component in vector)  # type: ignore[return-value]


def _direction_from_angles(yaw_deg: float, pitch_deg: float) -> Vec3 | None:
    """Use the tracker's convention: x right, y down, z forward."""

    yaw = _finite(yaw_deg)
    pitch = _finite(pitch_deg)
    if yaw is None or pitch is None:
        return None
    yaw_rad = math.radians(yaw)
    pitch_rad = math.radians(pitch)
    direction = (
        math.sin(yaw_rad) * math.cos(pitch_rad),
        math.sin(pitch_rad),
        math.cos(yaw_rad) * math.cos(pitch_rad),
    )
    return _unit(direction)


def _origin_from_pixel(center_px: tuple[float, float], width: int, height: int) -> Vec3 | None:
    x = _finite(center_px[0])
    y = _finite(center_px[1])
    if x is None or y is None or width <= 0 or height <= 0:
        return None
    scale = float(max(width, height))
    return ((x - width * 0.5) / scale, (y - height * 0.5) / scale, 0.0)


@dataclass(frozen=True)
class BinocularRayProxy:
    """Two eye rays in a normalized, camera-aligned proxy frame."""

    coordinate_frame: str
    left_origin: Vec3
    left_direction: Vec3
    right_origin: Vec3
    right_direction: Vec3
    interocular_baseline_proxy: float
    status: str = "VALID_RELATIVE_PROXY"
    unknown_reason: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "coordinate_frame": self.coordinate_frame,
            "left_origin": list(self.left_origin),
            "left_direction": list(self.left_direction),
            "right_origin": list(self.right_origin),
            "right_direction": list(self.right_direction),
            "interocular_baseline_proxy": self.interocular_baseline_proxy,
            "status": self.status,
            "unknown_reason": self.unknown_reason,
        }


def build_binocular_ray_proxy(
    *,
    left_center_px: tuple[float, float],
    right_center_px: tuple[float, float],
    left_yaw_deg: float,
    left_pitch_deg: float,
    right_yaw_deg: float,
    right_pitch_deg: float,
    width: int,
    height: int,
    disagreement_deg: float,
    max_disagreement_deg: float = 45.0,
) -> tuple[BinocularRayProxy | None, str | None]:
    """Build two explicit rays, failing closed when the signal is unusable.

    The image-plane origins are normalized by frame size.  This preserves
    relative parallax but intentionally does not claim metric eye separation.
    """

    disagreement = _finite(disagreement_deg)
    if disagreement is None or disagreement < 0.0:
        return None, "invalid_binocular_disagreement"
    if disagreement > max_disagreement_deg:
        return None, "binocular_disagreement_too_large"
    left_origin = _origin_from_pixel(left_center_px, width, height)
    right_origin = _origin_from_pixel(right_center_px, width, height)
    left_direction = _direction_from_angles(left_yaw_deg, left_pitch_deg)
    right_direction = _direction_from_angles(right_yaw_deg, right_pitch_deg)
    if left_origin is None or right_origin is None:
        return None, "invalid_eye_centres"
    if left_direction is None or right_direction is None:
        return None, "invalid_eye_directions"
    baseline = math.sqrt(
        sum((left_origin[index] - right_origin[index]) ** 2 for index in range(3))
    )
    if not math.isfinite(baseline) or baseline <= 1e-9:
        return None, "interocular_baseline_too_small"
    return (
        BinocularRayProxy(
            coordinate_frame="camera_proxy_normalized_v1",
            left_origin=left_origin,
            left_direction=left_direction,
            right_origin=right_origin,
            right_direction=right_direction,
            interocular_baseline_proxy=baseline,
        ),
        None,
    )

