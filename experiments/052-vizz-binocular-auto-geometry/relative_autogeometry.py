"""Binocular auto-geometry contract for VIZZ.

The method reconstructs a fixation point from two eye rays, fits a monitor
plane to presented targets and optionally uses a known EDID size to recover a
metric scale. Without that scale it remains valid only in relative eye-frame
units. This module is synthetic and does not open a camera.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


Vec3 = tuple[float, float, float]


def _add(a: Vec3, b: Vec3) -> Vec3:
    return a[0] + b[0], a[1] + b[1], a[2] + b[2]


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


def _scale(a: Vec3, factor: float) -> Vec3:
    return a[0] * factor, a[1] * factor, a[2] * factor


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _norm(a: Vec3) -> float:
    return math.sqrt(_dot(a, a))


def _unit(a: Vec3) -> Vec3 | None:
    length = _norm(a)
    if not math.isfinite(length) or length <= 1e-9:
        return None
    return _scale(a, 1.0 / length)


def _finite_vec3(value: Any) -> Vec3 | None:
    try:
        values = tuple(float(item) for item in value)
    except (TypeError, ValueError):
        return None
    if len(values) != 3 or not all(math.isfinite(item) for item in values):
        return None
    return values[0], values[1], values[2]


@dataclass(frozen=True)
class BinocularRaySample:
    sample_id: str
    monitor_id: str
    target_u: float
    target_v: float
    left_origin: Vec3
    left_direction: Vec3
    right_origin: Vec3
    right_direction: Vec3
    head_translation: Vec3 = (0.0, 0.0, 0.0)


@dataclass(frozen=True)
class FixationReconstruction:
    point: Vec3
    ray_separation: float
    left_depth: float
    right_depth: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "point": list(self.point),
            "ray_separation": self.ray_separation,
            "left_depth": self.left_depth,
            "right_depth": self.right_depth,
        }


@dataclass(frozen=True)
class PlaneFit:
    status: str
    monitor_id: str
    sample_count: int
    origin: Vec3 | None
    horizontal_axis: Vec3 | None
    vertical_axis: Vec3 | None
    normal: Vec3 | None
    relative_width: float | None
    relative_height: float | None
    width_m: float | None
    height_m: float | None
    scale_factor_m_per_relative_unit: float | None
    scale_status: str
    mean_ray_separation: float | None
    max_plane_residual: float | None
    unknown_reason: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "monitor_id": self.monitor_id,
            "sample_count": self.sample_count,
            "origin": None if self.origin is None else list(self.origin),
            "horizontal_axis": None if self.horizontal_axis is None else list(self.horizontal_axis),
            "vertical_axis": None if self.vertical_axis is None else list(self.vertical_axis),
            "normal": None if self.normal is None else list(self.normal),
            "relative_width": self.relative_width,
            "relative_height": self.relative_height,
            "width_m": self.width_m,
            "height_m": self.height_m,
            "scale_factor_m_per_relative_unit": self.scale_factor_m_per_relative_unit,
            "scale_status": self.scale_status,
            "mean_ray_separation": self.mean_ray_separation,
            "max_plane_residual": self.max_plane_residual,
            "unknown_reason": self.unknown_reason,
        }


def reconstruct_fixation(sample: BinocularRaySample) -> FixationReconstruction | None:
    """Return the closest midpoint of two forward rays, or UNKNOWN."""

    p = _finite_vec3(sample.left_origin)
    q = _finite_vec3(sample.right_origin)
    d = _unit(_finite_vec3(sample.left_direction) or (0.0, 0.0, 0.0))
    e = _unit(_finite_vec3(sample.right_direction) or (0.0, 0.0, 0.0))
    if p is None or q is None or d is None or e is None:
        return None
    w = _sub(p, q)
    a = _dot(d, d)
    b = _dot(d, e)
    c = _dot(e, e)
    f = _dot(d, w)
    g = _dot(e, w)
    denominator = a * c - b * b
    if abs(denominator) <= 1e-8:
        return None
    left_depth = (b * g - c * f) / denominator
    right_depth = (a * g - b * f) / denominator
    if not math.isfinite(left_depth) or not math.isfinite(right_depth) or left_depth <= 0.0 or right_depth <= 0.0:
        return None
    left_point = _add(p, _scale(d, left_depth))
    right_point = _add(q, _scale(e, right_depth))
    separation = _norm(_sub(left_point, right_point))
    return FixationReconstruction(
        point=_scale(_add(left_point, right_point), 0.5),
        ray_separation=separation,
        left_depth=left_depth,
        right_depth=right_depth,
    )


def _solve_3x3(matrix: list[list[float]], vector: list[float]) -> list[float] | None:
    augmented = [row[:] + [vector[index]] for index, row in enumerate(matrix)]
    for pivot in range(3):
        best = max(range(pivot, 3), key=lambda index: abs(augmented[index][pivot]))
        if abs(augmented[best][pivot]) <= 1e-10:
            return None
        augmented[pivot], augmented[best] = augmented[best], augmented[pivot]
        divisor = augmented[pivot][pivot]
        augmented[pivot] = [value / divisor for value in augmented[pivot]]
        for row in range(3):
            if row == pivot:
                continue
            factor = augmented[row][pivot]
            augmented[row] = [
                augmented[row][column] - factor * augmented[pivot][column]
                for column in range(4)
            ]
    return [augmented[index][3] for index in range(3)]


def _fit_affine(points: list[tuple[float, float, Vec3]]) -> tuple[Vec3, Vec3, Vec3] | None:
    if len(points) < 3:
        return None
    normal_matrix = [[0.0, 0.0, 0.0] for _ in range(3)]
    for u, v, _point in points:
        features = (1.0, u - 0.5, v - 0.5)
        for row in range(3):
            for column in range(3):
                normal_matrix[row][column] += features[row] * features[column]
    coefficients: list[list[float]] = []
    for coordinate in range(3):
        rhs = [0.0, 0.0, 0.0]
        for u, v, point in points:
            features = (1.0, u - 0.5, v - 0.5)
            for row in range(3):
                rhs[row] += features[row] * point[coordinate]
        solved = _solve_3x3([row[:] for row in normal_matrix], rhs)
        if solved is None:
            return None
        coefficients.append(solved)
    return (
        (coefficients[0][0], coefficients[1][0], coefficients[2][0]),
        (coefficients[0][1], coefficients[1][1], coefficients[2][1]),
        (coefficients[0][2], coefficients[1][2], coefficients[2][2]),
    )


def _prediction(origin: Vec3, horizontal: Vec3, vertical: Vec3, u: float, v: float) -> Vec3:
    return _add(origin, _add(_scale(horizontal, u - 0.5), _scale(vertical, v - 0.5)))


def _unknown(monitor_id: str, sample_count: int, reason: str) -> PlaneFit:
    return PlaneFit(
        status="UNKNOWN",
        monitor_id=monitor_id,
        sample_count=sample_count,
        origin=None,
        horizontal_axis=None,
        vertical_axis=None,
        normal=None,
        relative_width=None,
        relative_height=None,
        width_m=None,
        height_m=None,
        scale_factor_m_per_relative_unit=None,
        scale_status="UNKNOWN",
        mean_ray_separation=None,
        max_plane_residual=None,
        unknown_reason=reason,
    )


def fit_monitor_plane(
    samples: tuple[BinocularRaySample, ...],
    monitor_id: str,
    *,
    edid_width_m: float | None = None,
    edid_height_m: float | None = None,
) -> PlaneFit:
    """Fit a plane to binocular fixations, optionally solving scale from EDID."""

    selected = tuple(sample for sample in samples if sample.monitor_id == monitor_id)
    reconstructions: list[tuple[BinocularRaySample, FixationReconstruction]] = []
    for sample in selected:
        fixation = reconstruct_fixation(sample)
        if fixation is not None:
            reconstructions.append((sample, fixation))
    if len(reconstructions) < 6:
        return _unknown(monitor_id, len(reconstructions), "insufficient_valid_binocular_samples")
    points = [(sample.target_u, sample.target_v, fixation.point) for sample, fixation in reconstructions]
    fitted = _fit_affine(points)
    if fitted is None:
        return _unknown(monitor_id, len(reconstructions), "target_geometry_not_identifiable")
    origin, horizontal, vertical = fitted
    horizontal_length = _norm(horizontal)
    vertical_length = _norm(vertical)
    normal = _unit(_cross(horizontal, vertical))
    if horizontal_length <= 1e-9 or vertical_length <= 1e-9 or normal is None:
        return _unknown(monitor_id, len(reconstructions), "degenerate_fitted_plane")

    scale_factor = None
    width_m = None
    height_m = None
    scale_status = "RELATIVE_ONLY"
    if edid_width_m is not None or edid_height_m is not None:
        if edid_width_m is None or edid_height_m is None or edid_width_m <= 0.0 or edid_height_m <= 0.0:
            return _unknown(monitor_id, len(reconstructions), "partial_metric_scale")
        width_scale = edid_width_m / horizontal_length
        height_scale = edid_height_m / vertical_length
        if abs(width_scale - height_scale) > 0.05 * max(width_scale, height_scale):
            return _unknown(monitor_id, len(reconstructions), "edid_aspect_scale_conflict")
        scale_factor = (width_scale + height_scale) / 2.0
        origin = _scale(origin, scale_factor)
        horizontal = _scale(horizontal, scale_factor)
        vertical = _scale(vertical, scale_factor)
        width_m = _norm(horizontal)
        height_m = _norm(vertical)
        scale_status = "METRIC_FROM_EDID"

    residuals = [
        _norm(_sub(_prediction(fitted[0], fitted[1], fitted[2], sample.target_u, sample.target_v), fixation.point))
        for sample, fixation in reconstructions
    ]
    if scale_factor is not None:
        residuals = [residual * scale_factor for residual in residuals]
    separations = [fixation.ray_separation for _sample, fixation in reconstructions]
    return PlaneFit(
        status="VALID_METRIC" if scale_factor is not None else "VALID_RELATIVE",
        monitor_id=monitor_id,
        sample_count=len(reconstructions),
        origin=origin,
        horizontal_axis=horizontal,
        vertical_axis=vertical,
        normal=normal,
        relative_width=horizontal_length,
        relative_height=vertical_length,
        width_m=width_m,
        height_m=height_m,
        scale_factor_m_per_relative_unit=scale_factor,
        scale_status=scale_status,
        mean_ray_separation=sum(separations) / len(separations),
        max_plane_residual=max(residuals),
        unknown_reason=None,
    )
