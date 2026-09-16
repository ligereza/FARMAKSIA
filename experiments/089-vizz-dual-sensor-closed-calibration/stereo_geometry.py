"""Metric stereo primitives for the VIZZ dual-sensor experiment.

This module is intentionally separate from the point UI.  A pair of
calibrated 2-D mappers is not enough for 3-D triangulation; this module only
accepts a solved intrinsic/extrinsic calibration and then performs the actual
ray intersection through OpenCV's triangulation routine.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence

import cv2
import numpy as np


class StereoGeometryError(ValueError):
    """Stereo geometry is missing or numerically invalid."""


def _matrix(name: str, value: Any, shape: tuple[int, int]) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if array.shape != shape or not np.all(np.isfinite(array)):
        raise StereoGeometryError(f"{name} must be a finite matrix with shape {shape}")
    return array


@dataclass(frozen=True)
class StereoCalibration:
    """Intrinsics and relative pose for webcam (camera 1) and Hikvision (2)."""

    webcam_k: tuple[tuple[float, ...], ...]
    hikvision_k: tuple[tuple[float, ...], ...]
    rotation_2_from_1: tuple[tuple[float, ...], ...]
    translation_2_from_1: tuple[float, float, float]
    webcam_distortion: tuple[float, ...] = ()
    hikvision_distortion: tuple[float, ...] = ()

    def matrices(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        webcam_k = _matrix("webcam_k", self.webcam_k, (3, 3))
        hikvision_k = _matrix("hikvision_k", self.hikvision_k, (3, 3))
        rotation = _matrix("rotation_2_from_1", self.rotation_2_from_1, (3, 3))
        translation = np.asarray(self.translation_2_from_1, dtype=np.float64).reshape(-1, 1)
        if translation.shape != (3, 1) or not np.all(np.isfinite(translation)):
            raise StereoGeometryError("translation_2_from_1 must be a finite vector with three values")
        webcam_distortion = np.asarray(self.webcam_distortion, dtype=np.float64).reshape(1, -1)
        hikvision_distortion = np.asarray(self.hikvision_distortion, dtype=np.float64).reshape(1, -1)
        if webcam_distortion.size and not np.all(np.isfinite(webcam_distortion)):
            raise StereoGeometryError("webcam distortion must be finite")
        if hikvision_distortion.size and not np.all(np.isfinite(hikvision_distortion)):
            raise StereoGeometryError("Hikvision distortion must be finite")
        if np.linalg.det(rotation) <= 0.0:
            raise StereoGeometryError("relative rotation has invalid orientation")
        if not math.isfinite(float(np.linalg.norm(translation))) or np.linalg.norm(translation) <= 1e-9:
            raise StereoGeometryError("stereo baseline must be positive")
        return webcam_k, hikvision_k, rotation, translation, webcam_distortion, hikvision_distortion

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "StereoCalibration":
        if payload.get("schema") != "farmaxia:vizz-stereo-calibration:0.1":
            raise StereoGeometryError("unexpected stereo calibration schema")
        return cls(
            webcam_k=tuple(tuple(float(item) for item in row) for row in payload["webcam_k"]),
            hikvision_k=tuple(tuple(float(item) for item in row) for row in payload["hikvision_k"]),
            rotation_2_from_1=tuple(tuple(float(item) for item in row) for row in payload["rotation_2_from_1"]),
            translation_2_from_1=tuple(float(item) for item in payload["translation_2_from_1"]),
            webcam_distortion=tuple(float(item) for item in payload.get("webcam_distortion", [])),
            hikvision_distortion=tuple(float(item) for item in payload.get("hikvision_distortion", [])),
        )


def _undistort(K: np.ndarray, distortion: np.ndarray, point: Sequence[float]) -> np.ndarray:
    value = np.asarray([[float(point[0]), float(point[1])]], dtype=np.float64).reshape(1, 1, 2)
    return cv2.undistortPoints(value, K, distortion if distortion.size else None).reshape(2)


def triangulate_point(
    calibration: StereoCalibration,
    webcam_point_px: Sequence[float],
    hikvision_point_px: Sequence[float],
) -> dict[str, Any]:
    """Triangulate one corresponding point in the webcam camera frame."""

    if len(webcam_point_px) != 2 or len(hikvision_point_px) != 2:
        raise StereoGeometryError("stereo observations must be 2-D points")
    webcam_k, hikvision_k, rotation, translation, webcam_distortion, hikvision_distortion = calibration.matrices()
    point_1 = _undistort(webcam_k, webcam_distortion, webcam_point_px).reshape(2, 1)
    point_2 = _undistort(hikvision_k, hikvision_distortion, hikvision_point_px).reshape(2, 1)
    projection_1 = np.hstack((np.eye(3), np.zeros((3, 1))))
    projection_2 = np.hstack((rotation, translation))
    homogeneous = cv2.triangulatePoints(projection_1, projection_2, point_1, point_2)
    if homogeneous.shape != (4, 1) or abs(float(homogeneous[3, 0])) <= 1e-12:
        raise StereoGeometryError("triangulation returned an invalid homogeneous point")
    point_3d = (homogeneous[:3, 0] / homogeneous[3, 0]).astype(np.float64)
    if not np.all(np.isfinite(point_3d)):
        raise StereoGeometryError("triangulated point is non-finite")
    projected_1 = projection_1 @ np.concatenate((point_3d, [1.0]))
    projected_2 = projection_2 @ np.concatenate((point_3d, [1.0]))
    if projected_1[2] <= 0.0 or projected_2[2] <= 0.0:
        raise StereoGeometryError("triangulated point is behind one camera")
    return {
        "point_camera_1": [float(value) for value in point_3d],
        "depth_camera_1": float(point_3d[2]),
        "baseline": float(np.linalg.norm(translation)),
        "reprojection_proxy": {
            "webcam": [float(projected_1[0] / projected_1[2]), float(projected_1[1] / projected_1[2])],
            "hikvision": [float(projected_2[0] / projected_2[2]), float(projected_2[1] / projected_2[2])],
        },
        "status": "METRIC_STEREO_POINT",
    }
