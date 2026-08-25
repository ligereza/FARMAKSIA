"""Eye-pair normalization independent of translation, scale and image roll."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class EyeCentricObservation:
    left: np.ndarray | None
    right: np.ndarray | None
    interocular_distance: float | None
    roll_rad: float | None
    unknown_reason: str | None

    @property
    def valid(self) -> bool:
        return self.unknown_reason is None


def _invalid(reason: str) -> EyeCentricObservation:
    return EyeCentricObservation(None, None, None, None, reason)


def normalize_eye_pair(left_points: np.ndarray, right_points: np.ndarray) -> EyeCentricObservation:
    """Normalize two eye point clouds into an interocular coordinate frame.

    The transform removes image translation, isotropic scale and in-plane roll.
    It intentionally does not claim invariance to 3D head yaw/pitch; that needs
    an independently estimated head rotation and camera geometry.
    """

    left = np.asarray(left_points, dtype=np.float64)
    right = np.asarray(right_points, dtype=np.float64)
    if left.ndim != 2 or right.ndim != 2 or left.shape[1] not in (2, 3) or right.shape[1] != left.shape[1]:
        return _invalid("invalid_eye_point_shape")
    if left.shape[0] == 0 or right.shape[0] == 0:
        return _invalid("missing_eye_points")
    if not np.isfinite(left).all() or not np.isfinite(right).all():
        return _invalid("nonfinite_eye_points")

    left_center = left.mean(axis=0)
    right_center = right.mean(axis=0)
    delta = right_center[:2] - left_center[:2]
    distance = float(np.linalg.norm(delta))
    if not np.isfinite(distance) or distance <= 1e-9:
        return _invalid("interocular_distance_too_small")

    roll = float(np.arctan2(delta[1], delta[0]))
    cosine = float(np.cos(roll))
    sine = float(np.sin(roll))
    midpoint = (left_center + right_center) * 0.5

    def transform(points: np.ndarray) -> np.ndarray:
        centered = points - midpoint
        normalized = np.empty_like(centered)
        normalized[:, 0] = cosine * centered[:, 0] + sine * centered[:, 1]
        normalized[:, 1] = -sine * centered[:, 0] + cosine * centered[:, 1]
        if points.shape[1] == 3:
            normalized[:, 2] = centered[:, 2]
        return normalized / distance

    return EyeCentricObservation(transform(left), transform(right), distance, roll, None)
