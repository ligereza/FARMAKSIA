"""Geometry-first VIZZ state contract.

This module deliberately stops before rendering or opening a camera. It turns
an already-estimated binocular gaze ray into monitor hypotheses, a screen
coordinate and a conservative visual policy. Unknown states are explicit.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


Vec3 = tuple[float, float, float]
Vec2 = tuple[float, float]


def _finite_vector(value: Any, length: int) -> tuple[float, ...] | None:
    if value is None:
        return None
    try:
        values = tuple(float(item) for item in value)
    except (TypeError, ValueError):
        return None
    if len(values) != length or not all(math.isfinite(item) for item in values):
        return None
    return values


def _vec3(value: Any) -> Vec3 | None:
    result = _finite_vector(value, 3)
    return None if result is None else (result[0], result[1], result[2])


def _add(a: Vec3, b: Vec3) -> Vec3:
    return a[0] + b[0], a[1] + b[1], a[2] + b[2]


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


def _scale(value: Vec3, factor: float) -> Vec3:
    return value[0] * factor, value[1] * factor, value[2] * factor


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _norm(value: Vec3) -> float:
    return math.sqrt(_dot(value, value))


def _normalize(value: Vec3) -> Vec3 | None:
    length = _norm(value)
    if not math.isfinite(length) or length <= 1e-9:
        return None
    return _scale(value, 1.0 / length)


def angular_extent_deg(size_m: float, distance_m: float) -> float:
    """Angular extent of a physical display dimension at a positive distance."""

    if not math.isfinite(size_m) or not math.isfinite(distance_m) or size_m <= 0.0 or distance_m <= 0.0:
        raise ValueError("angular extent requires positive finite size and distance")
    return math.degrees(2.0 * math.atan(size_m / (2.0 * distance_m)))


@dataclass(frozen=True)
class MonitorPlane:
    """A physical monitor rectangle centered at ``origin`` in world metres."""

    monitor_id: str
    origin: Vec3
    horizontal_axis: Vec3
    vertical_axis: Vec3
    width_m: float
    height_m: float
    logical_rect: tuple[int, int, int, int]
    dpi_scale: float = 1.0
    enabled: bool = True

    def __post_init__(self) -> None:
        origin = _vec3(self.origin)
        horizontal = _normalize(self.horizontal_axis)
        vertical = _normalize(self.vertical_axis)
        if origin is None or horizontal is None or vertical is None:
            raise ValueError("monitor vectors must be finite and non-zero")
        if abs(_dot(horizontal, vertical)) > 1e-6:
            raise ValueError("monitor axes must be orthogonal")
        if self.width_m <= 0.0 or self.height_m <= 0.0:
            raise ValueError("monitor dimensions must be positive")
        if self.dpi_scale <= 0.0 or not math.isfinite(self.dpi_scale):
            raise ValueError("monitor dpi_scale must be finite and positive")
        if len(self.logical_rect) != 4 or self.logical_rect[2] <= 0 or self.logical_rect[3] <= 0:
            raise ValueError("monitor logical_rect must have positive size")

    @property
    def normal(self) -> Vec3:
        normal = _normalize(_cross(self.horizontal_axis, self.vertical_axis))
        if normal is None:  # pragma: no cover - guarded by __post_init__
            raise ValueError("monitor axes do not define a plane")
        return normal

    def intersect(self, ray_origin: Vec3, ray_direction: Vec3) -> dict[str, Any] | None:
        """Intersect a ray and return normalized screen coordinates if inside."""

        direction = _normalize(ray_direction)
        if direction is None:
            return None
        denominator = _dot(self.normal, direction)
        if abs(denominator) <= 1e-9:
            return None
        distance = _dot(self.normal, _sub(self.origin, ray_origin)) / denominator
        if not math.isfinite(distance) or distance <= 0.0:
            return None
        point = _add(ray_origin, _scale(direction, distance))
        relative = _sub(point, self.origin)
        horizontal_offset = _dot(relative, _normalize(self.horizontal_axis) or self.horizontal_axis)
        vertical_offset = _dot(relative, _normalize(self.vertical_axis) or self.vertical_axis)
        u = 0.5 + horizontal_offset / self.width_m
        v = 0.5 + vertical_offset / self.height_m
        if not (-1e-9 <= u <= 1.0 + 1e-9 and -1e-9 <= v <= 1.0 + 1e-9):
            return None
        return {
            "monitor_id": self.monitor_id,
            "distance_m": distance,
            "point_world": point,
            "uv": (u, v),
        }


@dataclass(frozen=True)
class MonitorLayout:
    version: str
    monitors: tuple[MonitorPlane, ...]

    def __post_init__(self) -> None:
        ids = [monitor.monitor_id for monitor in self.monitors]
        if not self.version or len(ids) != len(set(ids)) or not self.monitors:
            raise ValueError("monitor layout needs a version and unique monitors")


@dataclass(frozen=True)
class GazeObservation:
    """The minimum camera/model output required by the geometry layer."""

    timestamp_capture: float
    left_eye_world: Vec3 | None
    right_eye_world: Vec3 | None
    gaze_direction_world: Vec3 | None
    confidence: float
    uncertainty_deg: float
    layout_version: str
    fixation_state: str = "unknown"
    head_pose_valid: bool = True


@dataclass(frozen=True)
class InteractionContext:
    """Context only; neither mouse nor keyboard is gaze ground truth."""

    keyboard_active: bool = False
    keyboard_event_count: int = 0
    mouse_screen: tuple[int, int] | None = None
    active_window: str | None = None


@dataclass(frozen=True)
class DisplayState:
    layout_version: str
    refresh_hz: float = 60.0
    content_mutation_enabled: bool = False


@dataclass(frozen=True)
class GazeState:
    status: str
    monitor_id: str | None
    uv: Vec2 | None
    point_world: Vec3 | None
    gaze_origin_world: Vec3 | None
    gaze_direction_world: Vec3 | None
    distance_m: float | None
    confidence: float
    uncertainty_deg: float
    safe_radius_deg: float
    fixation_state: str
    candidate_monitor_ids: tuple[str, ...]
    unknown_reason: str | None

    @property
    def valid(self) -> bool:
        return self.status == "VALID" and self.unknown_reason is None

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "monitor_id": self.monitor_id,
            "uv": None if self.uv is None else list(self.uv),
            "point_world": None if self.point_world is None else list(self.point_world),
            "gaze_origin_world": None if self.gaze_origin_world is None else list(self.gaze_origin_world),
            "gaze_direction_world": None if self.gaze_direction_world is None else list(self.gaze_direction_world),
            "distance_m": self.distance_m,
            "confidence": self.confidence,
            "uncertainty_deg": self.uncertainty_deg,
            "safe_radius_deg": self.safe_radius_deg,
            "fixation_state": self.fixation_state,
            "candidate_monitor_ids": list(self.candidate_monitor_ids),
            "unknown_reason": self.unknown_reason,
        }


@dataclass(frozen=True)
class VisualPolicy:
    mode: str
    reason: str
    monitor_id: str | None
    focus_uv: Vec2 | None
    inner_radius_deg: float | None
    transition_radius_deg: float | None
    preserve_peripheral_signals: bool
    task: str
    keyboard_active: bool
    mouse_is_ground_truth: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "reason": self.reason,
            "monitor_id": self.monitor_id,
            "focus_uv": None if self.focus_uv is None else list(self.focus_uv),
            "inner_radius_deg": self.inner_radius_deg,
            "transition_radius_deg": self.transition_radius_deg,
            "preserve_peripheral_signals": self.preserve_peripheral_signals,
            "task": self.task,
            "keyboard_active": self.keyboard_active,
            "mouse_is_ground_truth": self.mouse_is_ground_truth,
        }


def safe_region_radius_deg(
    base_radius_deg: float,
    gaze_speed_deg_s: float,
    latency_ms: float,
    uncertainty_deg: float,
    uncertainty_multiplier: float = 2.0,
) -> float:
    """Conservative radius; parameters are engineering hypotheses, not physiology."""

    values = (base_radius_deg, gaze_speed_deg_s, latency_ms, uncertainty_deg, uncertainty_multiplier)
    if not all(math.isfinite(value) for value in values) or any(value < 0.0 for value in values):
        raise ValueError("safe-region inputs must be finite and non-negative")
    return base_radius_deg + gaze_speed_deg_s * latency_ms / 1000.0 + uncertainty_multiplier * uncertainty_deg


def _unknown(observation: GazeObservation, reason: str, candidates: tuple[str, ...] = ()) -> GazeState:
    return GazeState(
        status="UNKNOWN",
        monitor_id=None,
        uv=None,
        point_world=None,
        gaze_origin_world=None,
        gaze_direction_world=None,
        distance_m=None,
        confidence=observation.confidence,
        uncertainty_deg=observation.uncertainty_deg,
        safe_radius_deg=0.0,
        fixation_state=observation.fixation_state,
        candidate_monitor_ids=candidates,
        unknown_reason=reason,
    )


def resolve_gaze(
    observation: GazeObservation,
    layout: MonitorLayout,
    *,
    minimum_confidence: float = 0.60,
    maximum_uncertainty_deg: float = 8.0,
    gaze_speed_deg_s: float = 0.0,
    latency_ms: float = 0.0,
    base_radius_deg: float = 2.0,
) -> GazeState:
    """Resolve one observation against all monitor planes, or return UNKNOWN."""

    if observation.layout_version != layout.version:
        return _unknown(observation, "display_layout_changed")
    if not math.isfinite(observation.timestamp_capture):
        return _unknown(observation, "invalid_timestamp")
    if observation.left_eye_world is None or observation.right_eye_world is None:
        return _unknown(observation, "missing_eye")
    left = _vec3(observation.left_eye_world)
    right = _vec3(observation.right_eye_world)
    direction = _vec3(observation.gaze_direction_world)
    if left is None or right is None or direction is None:
        return _unknown(observation, "invalid_eye_or_gaze_vector")
    if not observation.head_pose_valid:
        return _unknown(observation, "invalid_head_pose")
    if not math.isfinite(observation.confidence) or observation.confidence < minimum_confidence:
        return _unknown(observation, "low_confidence")
    if not math.isfinite(observation.uncertainty_deg) or observation.uncertainty_deg < 0.0:
        return _unknown(observation, "invalid_uncertainty")
    if observation.uncertainty_deg > maximum_uncertainty_deg:
        return _unknown(observation, "uncertainty_out_of_domain")
    unit_direction = _normalize(direction)
    if unit_direction is None:
        return _unknown(observation, "zero_gaze_vector")

    origin = _scale(_add(left, right), 0.5)
    hits = [
        hit
        for monitor in layout.monitors
        if monitor.enabled
        for hit in [monitor.intersect(origin, unit_direction)]
        if hit is not None
    ]
    candidates = tuple(hit["monitor_id"] for hit in hits)
    if not hits:
        return _unknown(observation, "no_monitor_intersection")
    if len(hits) > 1:
        return _unknown(observation, "ambiguous_monitor", candidates)
    hit = hits[0]
    return GazeState(
        status="VALID",
        monitor_id=hit["monitor_id"],
        uv=hit["uv"],
        point_world=hit["point_world"],
        gaze_origin_world=origin,
        gaze_direction_world=unit_direction,
        distance_m=hit["distance_m"],
        confidence=observation.confidence,
        uncertainty_deg=observation.uncertainty_deg,
        safe_radius_deg=safe_region_radius_deg(
            base_radius_deg,
            gaze_speed_deg_s,
            latency_ms,
            observation.uncertainty_deg,
        ),
        fixation_state=observation.fixation_state,
        candidate_monitor_ids=candidates,
        unknown_reason=None,
    )


def visual_policy(
    state: GazeState,
    context: InteractionContext,
    display: DisplayState,
    *,
    task: str = "unknown",
) -> VisualPolicy:
    """Return a policy descriptor; this function never changes screen content."""

    if display.content_mutation_enabled:
        return VisualPolicy(
            "STATIC_FALLBACK",
            "content_mutation_disabled_in_geometry_probe",
            None,
            None,
            None,
            None,
            True,
            task,
            context.keyboard_active,
        )
    if not state.valid:
        return VisualPolicy(
            "STATIC_FALLBACK",
            state.unknown_reason or "invalid_gaze_state",
            None,
            None,
            None,
            None,
            True,
            task,
            context.keyboard_active,
        )
    transition = max(state.safe_radius_deg * 2.0, state.safe_radius_deg + 1.0)
    return VisualPolicy(
        "ADAPTIVE_REGION_DESCRIPTOR",
        "geometry_only_no_renderer",
        state.monitor_id,
        state.uv,
        state.safe_radius_deg,
        transition,
        True,
        task,
        context.keyboard_active,
    )
