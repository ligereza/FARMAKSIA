"""Local gaze-to-screen calibration profile without raw camera persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import numpy as np


PROFILE_SCHEMA = "farmaxia:vizz-calibration-profile:0.2"
MINIMUM_SAMPLES = 12
FEATURE_COUNT = 6


def design_row(features: Iterable[float]) -> np.ndarray:
    values = np.asarray(list(features), dtype=np.float64)
    if values.shape != (FEATURE_COUNT,) or not np.all(np.isfinite(values)):
        raise ValueError("calibration feature vector must contain six finite values")
    yaw, pitch, left_yaw, right_yaw, eye_x, eye_y = values
    return np.asarray(
        [1.0, yaw, pitch, left_yaw, right_yaw, eye_x, eye_y, yaw * pitch, yaw * yaw, pitch * pitch],
        dtype=np.float64,
    )


def fit_mapping(samples: list[dict[str, object]]) -> tuple[list[float], list[float]]:
    if len(samples) < MINIMUM_SAMPLES:
        raise ValueError(f"at least {MINIMUM_SAMPLES} samples are required")
    design = np.vstack([design_row(sample["features"]) for sample in samples])
    targets = np.asarray([sample["target"] for sample in samples], dtype=np.float64)
    if targets.shape != (len(samples), 2) or not np.all(np.isfinite(targets)):
        raise ValueError("calibration targets must be finite normalized pairs")
    ridge = np.eye(design.shape[1], dtype=np.float64) * 1e-4
    ridge[0, 0] = 0.0
    coefficients = np.linalg.solve(design.T @ design + ridge, design.T @ targets)
    return coefficients[:, 0].tolist(), coefficients[:, 1].tolist()


def seal_profile(
    path: Path,
    screen_size: tuple[int, int],
    samples: Iterable[dict[str, object]],
    model_sha256: str,
) -> Path:
    materialized = list(samples)
    if len(materialized) < MINIMUM_SAMPLES:
        raise ValueError(f"at least {MINIMUM_SAMPLES} samples are required")
    if not model_sha256:
        raise ValueError("model hash is required")
    for sample in materialized:
        design_row(sample["features"])
        target = np.asarray(sample["target"], dtype=np.float64)
        if target.shape != (2,) or not np.all(np.isfinite(target)):
            raise ValueError("invalid normalized target")
    x_coefficients, y_coefficients = fit_mapping(materialized)
    payload = {
        "schema": PROFILE_SCHEMA,
        "screen_size": [int(screen_size[0]), int(screen_size[1])],
        "sample_count": len(materialized),
        "model_sha256": model_sha256,
        "samples": materialized,
        "mapping": {"x": x_coefficients, "y": y_coefficients},
        "raw_video": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return path


class ScreenMapper:
    def __init__(self, profile: dict[str, object]) -> None:
        mapping = profile.get("mapping")
        if not isinstance(mapping, dict):
            raise ValueError("calibration profile has no mapping")
        self.x = np.asarray(mapping.get("x"), dtype=np.float64)
        self.y = np.asarray(mapping.get("y"), dtype=np.float64)
        if self.x.shape != (10,) or self.y.shape != (10,):
            raise ValueError("calibration mapping has an unexpected shape")

    def predict(self, features: Iterable[float]) -> tuple[float, float]:
        row = design_row(features)
        point = np.asarray([row @ self.x, row @ self.y], dtype=np.float64)
        if not np.all(np.isfinite(point)):
            raise ValueError("calibration produced a non-finite point")
        return float(np.clip(point[0], 0.0, 1.0)), float(np.clip(point[1], 0.0, 1.0))


def load_profile(path: Path) -> tuple[dict[str, object], ScreenMapper]:
    profile = json.loads(path.read_text(encoding="utf-8"))
    if profile.get("schema") != PROFILE_SCHEMA or profile.get("raw_video") is not False:
        raise ValueError("profile schema or raw-video policy is invalid")
    samples = profile.get("samples")
    if not isinstance(samples, list) or len(samples) < MINIMUM_SAMPLES:
        raise ValueError("profile is incomplete")
    return profile, ScreenMapper(profile)
