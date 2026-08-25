"""Temporal and quality policy for one static VIZZ calibration target.

The target shown by the UI is the only label.  A mouse event may arm a
capture window, but it is never treated as gaze ground truth.  This module is
kept free of Tk, OpenCV and ONNX imports so its timing and rejection rules can
be tested with synthetic samples.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol


class SampleLike(Protocol):
    features: tuple[float, ...]
    quality: float
    pose: tuple[float, ...] | None


@dataclass(frozen=True)
class CaptureConfig:
    """Initial, deliberately versioned calibration hyperparameters.

    These values are engineering starting points, not physiological claims.
    They must be revisited against held-out calibration sessions.
    """

    settle_seconds: float = 0.30
    window_seconds: float = 0.90
    min_valid_samples: int = 12
    min_quality: float = 0.50
    max_feature_mad: float = 0.08
    require_pose: bool = False


@dataclass(frozen=True)
class CaptureResult:
    accepted: bool
    features: tuple[float, ...] | None
    valid_count: int
    quality_mean: float
    max_feature_mad: float
    reason: str
    pose: tuple[float, ...] | None = None
    max_pose_mad: float = 0.0


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) * 0.5


def _robust_center(samples: list[tuple[float, ...]]) -> tuple[tuple[float, ...], float]:
    feature_count = len(samples[0])
    center = tuple(_median([sample[index] for sample in samples]) for index in range(feature_count))
    deviations = [
        _median([abs(sample[index] - center[index]) for sample in samples])
        for index in range(feature_count)
    ]
    return center, max(deviations, default=0.0)


class StableCapture:
    """Collect one fixed, post-settling window and reject unstable labels."""

    def __init__(self, config: CaptureConfig = CaptureConfig()) -> None:
        if config.settle_seconds < 0.0 or config.window_seconds <= 0.0:
            raise ValueError("capture timing must be non-negative and non-zero")
        if config.min_valid_samples < 1 or not 0.0 <= config.min_quality <= 1.0:
            raise ValueError("capture thresholds are invalid")
        if config.max_feature_mad <= 0.0:
            raise ValueError("max_feature_mad must be positive")
        self.config = config
        self.armed_at: float | None = None
        self.active_at: float | None = None
        self.deadline: float | None = None
        self.samples: list[tuple[float, ...]] = []
        self.poses: list[tuple[float, ...]] = []
        self.qualities: list[float] = []
        self.finished = False

    @property
    def active(self) -> bool:
        return self.armed_at is not None and not self.finished

    def arm(self, now: float) -> None:
        if not math.isfinite(now):
            raise ValueError("capture start time must be finite")
        self.armed_at = now
        self.active_at = now + self.config.settle_seconds
        self.deadline = self.active_at + self.config.window_seconds
        self.samples = []
        self.poses = []
        self.qualities = []
        self.finished = False

    def push(self, now: float, sample: SampleLike | None) -> CaptureResult | None:
        """Feed one camera result; return a result exactly when the window ends."""

        if not self.active or self.active_at is None or self.deadline is None:
            return None
        if not math.isfinite(now):
            raise ValueError("sample time must be finite")
        if now < self.active_at:
            # The settling interval is intentionally discarded.
            return None
        if now >= self.deadline:
            return self.finish()
        if sample is None or sample.quality < self.config.min_quality:
            return None
        features = tuple(float(value) for value in sample.features)
        if not features or not all(math.isfinite(value) for value in features):
            return None
        pose = getattr(sample, "pose", None)
        pose_values: tuple[float, ...] | None = None
        if pose is not None:
            candidate = tuple(float(value) for value in pose)
            if candidate and all(math.isfinite(value) for value in candidate):
                pose_values = candidate
        self.samples.append(features)
        if pose_values is not None:
            self.poses.append(pose_values)
        self.qualities.append(float(sample.quality))
        return None

    def finish(self) -> CaptureResult:
        if self.finished:
            raise RuntimeError("capture window has already finished")
        self.finished = True
        if len(self.samples) < self.config.min_valid_samples:
            return CaptureResult(
                accepted=False,
                features=None,
                valid_count=len(self.samples),
                quality_mean=_mean(self.qualities),
                max_feature_mad=math.inf,
                reason="insufficient_valid_samples",
            )
        if self.config.require_pose and len(self.poses) < self.config.min_valid_samples:
            return CaptureResult(
                accepted=False,
                features=None,
                valid_count=len(self.samples),
                quality_mean=_mean(self.qualities),
                max_feature_mad=math.inf,
                reason="insufficient_pose_samples",
            )
        features, max_feature_mad = _robust_center(self.samples)
        if max_feature_mad > self.config.max_feature_mad:
            return CaptureResult(
                accepted=False,
                features=None,
                valid_count=len(self.samples),
                quality_mean=_mean(self.qualities),
                max_feature_mad=max_feature_mad,
                reason="unstable_feature_window",
            )
        pose = None
        max_pose_mad = 0.0
        if self.poses:
            pose, max_pose_mad = _robust_center(self.poses)
        return CaptureResult(
            accepted=True,
            features=features,
            valid_count=len(self.samples),
            quality_mean=_mean(self.qualities),
            max_feature_mad=max_feature_mad,
            reason="accepted",
            pose=pose,
            max_pose_mad=max_pose_mad,
        )


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0
