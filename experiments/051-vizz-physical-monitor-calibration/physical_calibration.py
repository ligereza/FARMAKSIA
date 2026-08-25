"""Physical monitor calibration contract for VIZZ.

This layer accepts measured/validated physical monitor data and converts it to
the 3-D planes consumed by experiment 046. It intentionally rejects pixel-only
layout data: Windows coordinates are logical desktop coordinates, not metres.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any

from gaze_geometry import MonitorLayout, MonitorPlane


Vec3 = tuple[float, float, float]
Rect = tuple[int, int, int, int]

ALLOWED_SCALE_SOURCES = {
    "manual_measurement",
    "edid_verified_manual",
    "known_marker",
    "declared_fixture",
}
ALLOWED_POSE_SOURCES = {
    "manual_measurement",
    "marker_pose",
    "declared_fixture",
}


class PhysicalCalibrationError(ValueError):
    """Raised when physical calibration data is absent or inconsistent."""


def _finite_vec3(value: Any, label: str) -> Vec3:
    try:
        result = tuple(float(item) for item in value)
    except (TypeError, ValueError):
        raise PhysicalCalibrationError(f"{label} must contain three finite numbers") from None
    if len(result) != 3 or not all(math.isfinite(item) for item in result):
        raise PhysicalCalibrationError(f"{label} must contain three finite numbers")
    return result[0], result[1], result[2]


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(value: Vec3) -> float:
    return math.sqrt(_dot(value, value))


def _unit(value: Vec3, label: str) -> Vec3:
    length = _norm(value)
    if not math.isfinite(length) or length <= 1e-9:
        raise PhysicalCalibrationError(f"{label} must be non-zero")
    return value[0] / length, value[1] / length, value[2] / length


def _logical_rect_to_width_height(logical_rect: Rect) -> tuple[int, int, int, int]:
    if len(logical_rect) != 4:
        raise PhysicalCalibrationError("logical_rect must be left, top, right, bottom")
    left, top, right, bottom = (int(value) for value in logical_rect)
    if right <= left or bottom <= top:
        raise PhysicalCalibrationError("logical_rect must have positive extent")
    return left, top, right - left, bottom - top


@dataclass(frozen=True)
class PhysicalMonitorSpec:
    """One physical rectangular display in a shared world frame.

    ``origin`` is the centre of the display plane. Axes are directions along
    the visible horizontal and vertical sides. All distances use metres.
    """

    monitor_id: str
    logical_rect: Rect
    width_m: float
    height_m: float
    origin: Vec3
    horizontal_axis: Vec3
    vertical_axis: Vec3
    scale_source: str
    pose_source: str
    measurement_id: str
    reprojection_error_px: float | None = None
    marker_count: int | None = None

    def __post_init__(self) -> None:
        if not self.monitor_id or not self.measurement_id:
            raise PhysicalCalibrationError("monitor_id and measurement_id are required")
        _logical_rect_to_width_height(self.logical_rect)
        for value, label in ((self.width_m, "width_m"), (self.height_m, "height_m")):
            if not math.isfinite(value) or value <= 0.0:
                raise PhysicalCalibrationError(f"{label} must be positive metres")
        origin = _finite_vec3(self.origin, "origin")
        horizontal = _unit(_finite_vec3(self.horizontal_axis, "horizontal_axis"), "horizontal_axis")
        vertical = _unit(_finite_vec3(self.vertical_axis, "vertical_axis"), "vertical_axis")
        if abs(_dot(horizontal, vertical)) > 1e-5:
            raise PhysicalCalibrationError("monitor axes must be orthogonal")
        if self.scale_source not in ALLOWED_SCALE_SOURCES:
            raise PhysicalCalibrationError(f"unsupported scale_source: {self.scale_source}")
        if self.pose_source not in ALLOWED_POSE_SOURCES:
            raise PhysicalCalibrationError(f"unsupported pose_source: {self.pose_source}")
        if self.reprojection_error_px is not None and (
            not math.isfinite(self.reprojection_error_px) or self.reprojection_error_px < 0.0
        ):
            raise PhysicalCalibrationError("reprojection_error_px must be non-negative when present")
        if self.marker_count is not None and self.marker_count < 0:
            raise PhysicalCalibrationError("marker_count must be non-negative when present")
        object.__setattr__(self, "origin", origin)
        object.__setattr__(self, "horizontal_axis", horizontal)
        object.__setattr__(self, "vertical_axis", vertical)

    @property
    def logical_rect_xywh(self) -> tuple[int, int, int, int]:
        return _logical_rect_to_width_height(self.logical_rect)

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["logical_rect"] = list(self.logical_rect)
        payload["logical_rect_xywh"] = list(self.logical_rect_xywh)
        payload["origin"] = list(self.origin)
        payload["horizontal_axis"] = list(self.horizontal_axis)
        payload["vertical_axis"] = list(self.vertical_axis)
        return payload


def build_physical_layout(
    specs: tuple[PhysicalMonitorSpec, ...],
    *,
    logical_layout_version: str,
) -> MonitorLayout:
    """Convert physical specs to the geometry-first 046 monitor layout."""

    if not logical_layout_version:
        raise PhysicalCalibrationError("logical_layout_version is required")
    if not specs:
        raise PhysicalCalibrationError("at least one physical monitor is required")
    monitor_ids = [spec.monitor_id for spec in specs]
    if len(monitor_ids) != len(set(monitor_ids)):
        raise PhysicalCalibrationError("monitor IDs must be unique")
    canonical = {
        "logical_layout_version": logical_layout_version,
        "monitors": [spec.as_dict() for spec in sorted(specs, key=lambda item: item.monitor_id)],
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    version = hashlib.sha256(encoded).hexdigest()[:16]
    planes = tuple(
        MonitorPlane(
            monitor_id=spec.monitor_id,
            origin=spec.origin,
            horizontal_axis=spec.horizontal_axis,
            vertical_axis=spec.vertical_axis,
            width_m=spec.width_m,
            height_m=spec.height_m,
            logical_rect=spec.logical_rect_xywh,
        )
        for spec in sorted(specs, key=lambda item: item.monitor_id)
    )
    return MonitorLayout(version=version, monitors=planes)


def calibration_targets(monitor_id: str) -> tuple[dict[str, Any], ...]:
    """Nine spatial targets; target coordinates are screen-normalized, not mouse truth."""

    if not monitor_id:
        raise PhysicalCalibrationError("monitor_id is required")
    values = (0.10, 0.50, 0.90)
    targets: list[dict[str, Any]] = []
    for row, v in enumerate(values):
        for column, u in enumerate(values):
            role = "center" if (u, v) == (0.50, 0.50) else "edge_or_corner"
            targets.append(
                {
                    "id": f"{monitor_id}-target-{row + 1}-{column + 1}",
                    "monitor_id": monitor_id,
                    "u": u,
                    "v": v,
                    "role": role,
                    "ground_truth_source": "presented_target",
                    "mouse_is_ground_truth": False,
                }
            )
    return tuple(targets)


def validate_against_logical_snapshot(
    specs: tuple[PhysicalMonitorSpec, ...], snapshot: dict[str, Any]
) -> None:
    """Ensure physical records still refer to the current Windows layout."""

    snapshot_monitors = {item["device_name"]: item for item in snapshot.get("monitors", [])}
    for spec in specs:
        observed = snapshot_monitors.get(spec.monitor_id)
        if observed is None:
            raise PhysicalCalibrationError(f"monitor not present in logical snapshot: {spec.monitor_id}")
        observed_rect = tuple(int(value) for value in observed["monitor_rect"])
        if observed_rect != spec.logical_rect:
            raise PhysicalCalibrationError(f"logical rectangle changed for {spec.monitor_id}")


def reject_pixel_only_layout(width_m: Any, height_m: Any, *, source: str) -> None:
    """Explicit kill test for attempts to derive metres from pixel layout."""

    if source in {"windows_pixels", "dpi_only", "logical_rect_only", "depth_mask_only"}:
        raise PhysicalCalibrationError("pixel-only or unscaled source cannot establish physical geometry")
    try:
        width = float(width_m)
        height = float(height_m)
    except (TypeError, ValueError):
        raise PhysicalCalibrationError("physical width and height are required") from None
    if not math.isfinite(width) or not math.isfinite(height) or width <= 0.0 or height <= 0.0:
        raise PhysicalCalibrationError("physical width and height are required")
