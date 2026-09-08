"""Pure contracts for the VIZZ dual-camera closed calibration.

The runtime feeds this module summaries from two sensors.  It deliberately
keeps the numerical estimate total: when one sensor is absent the caller can
still use the other calibrated estimate, and the result carries mode,
coverage and disagreement instead of disappearing.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


CALIBRATION_POINTS: tuple[tuple[float, float], ...] = (
    (0.08, 0.08),
    (0.50, 0.08),
    (0.92, 0.08),
    (0.08, 0.33),
    (0.50, 0.33),
    (0.92, 0.33),
    (0.08, 0.67),
    (0.50, 0.67),
    (0.92, 0.67),
    (0.08, 0.92),
    (0.50, 0.92),
    (0.92, 0.92),
)

FEATURE_COUNT = 6
DESIGN_COUNT = 10
DEFAULT_RIDGE_LAMBDA = 1e-2


class DualContractError(ValueError):
    """The dual estimate cannot be constructed from the supplied values."""


def _finite(name: str, value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise DualContractError(f"{name} must be numeric") from exc
    if not math.isfinite(number):
        raise DualContractError(f"{name} must be finite")
    return number


def _median(values: Sequence[float]) -> float:
    if not values:
        raise DualContractError("median requires at least one value")
    return float(np.median(np.asarray(values, dtype=np.float64)))


def _mad(values: Sequence[float], center: float | None = None) -> float:
    if not values:
        raise DualContractError("MAD requires at least one value")
    median = _median(values) if center is None else float(center)
    return float(np.median(np.abs(np.asarray(values, dtype=np.float64) - median)))


def robust_vector_center(vectors: Sequence[Sequence[float]]) -> tuple[list[float], float]:
    """Return component-wise median and the largest component MAD."""

    if not vectors:
        raise DualContractError("at least one vector is required")
    array = np.asarray(vectors, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != FEATURE_COUNT:
        raise DualContractError(f"expected vectors with {FEATURE_COUNT} components")
    if not np.all(np.isfinite(array)):
        raise DualContractError("vectors must be finite")
    center = np.median(array, axis=0)
    deviations = np.median(np.abs(array - center), axis=0)
    return center.tolist(), float(np.max(deviations))


def design_row(features: Iterable[float]) -> np.ndarray:
    values = np.asarray(list(features), dtype=np.float64)
    if values.shape != (FEATURE_COUNT,) or not np.all(np.isfinite(values)):
        raise DualContractError(f"features must contain {FEATURE_COUNT} finite values")
    yaw, pitch, left_yaw, right_yaw, eye_x, eye_y = values
    return np.asarray(
        [
            1.0,
            yaw,
            pitch,
            left_yaw,
            right_yaw,
            eye_x,
            eye_y,
            yaw * pitch,
            yaw * yaw,
            pitch * pitch,
        ],
        dtype=np.float64,
    )


@dataclass(frozen=True)
class MappingModel:
    """A fixed-term ridge mapper from one sensor to normalized screen space."""

    x: tuple[float, ...]
    y: tuple[float, ...]
    ridge_lambda: float
    sample_count: int

    def predict(self, features: Iterable[float]) -> tuple[float, float]:
        row = design_row(features)
        point = np.asarray([row @ np.asarray(self.x), row @ np.asarray(self.y)])
        if not np.all(np.isfinite(point)):
            raise DualContractError("mapping produced a non-finite point")
        return float(np.clip(point[0], 0.0, 1.0)), float(np.clip(point[1], 0.0, 1.0))

    def as_dict(self) -> dict[str, Any]:
        return {
            "x": list(self.x),
            "y": list(self.y),
            "ridge_lambda": self.ridge_lambda,
            "sample_count": self.sample_count,
            "terms": DESIGN_COUNT,
        }


def _record_features(record: Mapping[str, Any]) -> Sequence[float]:
    features = record.get("features")
    if not isinstance(features, (list, tuple)):
        raise DualContractError("record has no feature vector")
    return features


def _summarize_ir_optics(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize scalar pupil/glint diagnostics without treating them as gaze."""

    status_counts: dict[str, int] = {}
    pupil_diameters: list[float] = []
    confidences: list[float] = []
    contrasts: list[float] = []
    vector_x: list[float] = []
    vector_y: list[float] = []
    polarity_counts: dict[str, int] = {}
    sample_count = 0
    eye_count = 0
    for record in records:
        optics = record.get("ir_optics")
        if not isinstance(optics, (list, tuple)) or len(optics) != 2:
            continue
        sample_count += 1
        for eye in optics:
            if not isinstance(eye, Mapping):
                continue
            eye_count += 1
            status = str(eye.get("status") or "NO_FEATURES")
            status_counts[status] = status_counts.get(status, 0) + 1
            polarity = str(eye.get("pupil_polarity") or "unknown")
            polarity_counts[polarity] = polarity_counts.get(polarity, 0) + 1
            try:
                confidence = float(eye.get("confidence"))
                contrast = float(eye.get("local_contrast"))
            except (TypeError, ValueError):
                confidence = float("nan")
                contrast = float("nan")
            if math.isfinite(confidence):
                confidences.append(confidence)
            if math.isfinite(contrast):
                contrasts.append(contrast)
            try:
                diameter = float(eye.get("pupil_diameter_px"))
            except (TypeError, ValueError):
                diameter = float("nan")
            if math.isfinite(diameter):
                pupil_diameters.append(diameter)
            vector = eye.get("pupil_glint_vector_px")
            if isinstance(vector, (list, tuple)) and len(vector) == 2:
                try:
                    x_value, y_value = float(vector[0]), float(vector[1])
                except (TypeError, ValueError):
                    continue
                if math.isfinite(x_value) and math.isfinite(y_value):
                    vector_x.append(x_value)
                    vector_y.append(y_value)
    pair_count = status_counts.get("PUPIL_GLINT", 0)
    return {
        "ir_optics_status": "available" if sample_count else "not_collected",
        "ir_optics_sample_count": sample_count,
        "ir_eye_count": eye_count,
        "ir_status_counts": status_counts,
        "ir_pupil_polarity_counts": polarity_counts,
        "ir_pupil_glint_eye_count": pair_count,
        "ir_pupil_glint_pair_rate": (pair_count / eye_count) if eye_count else None,
        "ir_pupil_diameter_median_px": _median(pupil_diameters) if pupil_diameters else None,
        "ir_pupil_diameter_mad_px": _mad(pupil_diameters) if pupil_diameters else None,
        "ir_pupil_glint_vector_median_px": (
            [_median(vector_x), _median(vector_y)] if vector_x and vector_y else None
        ),
        "ir_pupil_glint_vector_mad_px": (
            [_mad(vector_x), _mad(vector_y)] if vector_x and vector_y else None
        ),
        "ir_local_contrast_median": _median(contrasts) if contrasts else None,
        "ir_confidence_median": _median(confidences) if confidences else None,
    }


def fit_mapping(
    records: Sequence[Mapping[str, Any]],
    *,
    ridge_lambda: float = DEFAULT_RIDGE_LAMBDA,
) -> MappingModel:
    """Fit one sensor mapper using the same ten terms as the existing profile."""

    if len(records) < DESIGN_COUNT:
        raise DualContractError(f"at least {DESIGN_COUNT} records are required")
    ridge_lambda = _finite("ridge_lambda", ridge_lambda)
    if ridge_lambda <= 0.0:
        raise DualContractError("ridge_lambda must be positive")
    design = np.vstack([design_row(_record_features(record)) for record in records])
    targets = np.asarray([record["target"] for record in records], dtype=np.float64)
    if targets.shape != (len(records), 2) or not np.all(np.isfinite(targets)):
        raise DualContractError("records must contain finite target pairs")
    penalty = np.eye(DESIGN_COUNT, dtype=np.float64) * ridge_lambda
    penalty[0, 0] = 0.0
    lhs = design.T @ design + penalty
    try:
        coefficients = np.linalg.solve(lhs, design.T @ targets)
    except np.linalg.LinAlgError as exc:
        raise DualContractError("mapping design is singular") from exc
    if not np.all(np.isfinite(coefficients)):
        raise DualContractError("mapping coefficients are non-finite")
    return MappingModel(
        tuple(float(value) for value in coefficients[:, 0]),
        tuple(float(value) for value in coefficients[:, 1]),
        ridge_lambda,
        len(records),
    )


def summarize_sensor_window(
    records: Sequence[Mapping[str, Any]],
    *,
    min_samples: int = 4,
    min_quality: float = 0.50,
    max_feature_mad: float = 0.08,
) -> dict[str, Any]:
    """Summarize only the pre-click samples for one sensor."""

    if min_samples < 1 or not 0.0 <= min_quality <= 1.0 or max_feature_mad <= 0.0:
        raise DualContractError("invalid window thresholds")
    valid: list[Mapping[str, Any]] = []
    frame_read_count = 0
    numeric_feature_count = 0
    quality_pass_count = 0
    rejection_counts: dict[str, int] = {}

    def reject(reason: str) -> None:
        rejection_counts[reason] = rejection_counts.get(reason, 0) + 1

    for record in records:
        if not bool(record.get("frame_read", False)):
            reject(str(record.get("reason") or "frame_not_read"))
            continue
        frame_read_count += 1
        try:
            features = _record_features(record)
            design_row(features)
            numeric_feature_count += 1
        except (DualContractError, TypeError, ValueError):
            reject(str(record.get("reason") or "invalid_features"))
            continue
        quality = float(record.get("quality", 0.0))
        if not math.isfinite(quality) or quality < min_quality:
            reject("quality_below_threshold")
            continue
        quality_pass_count += 1
        valid.append(record)
    diagnostics = {
        "window_record_count": len(records),
        "frame_read_count": frame_read_count,
        "numeric_feature_count": numeric_feature_count,
        "quality_pass_count": quality_pass_count,
        "accepted_sample_count": len(valid),
        "rejection_counts": rejection_counts,
    }
    ir_summary = _summarize_ir_optics(valid)
    if len(valid) < min_samples:
        return {
            "status": "DEGRADED",
            "mode": "NO_NUMERIC_ESTIMATE",
            "reason": "insufficient_sensor_samples",
            "sample_count": len(valid),
            "features": None,
            "feature_mad": None,
            "quality_median": _median([float(item.get("quality", 0.0)) for item in valid]) if valid else 0.0,
            "diagnostics": diagnostics,
            **ir_summary,
        }

    center, feature_mad = robust_vector_center([_record_features(item) for item in valid])
    quality_median = _median([float(item.get("quality", 0.0)) for item in valid])
    poses = [item.get("pose") for item in valid if isinstance(item.get("pose"), (list, tuple))]
    pose_center: list[float] | None = None
    pose_mad: float | None = None
    if poses:
        pose_array = np.asarray(poses, dtype=np.float64)
        if pose_array.ndim == 2 and np.all(np.isfinite(pose_array)):
            pose_center = [float(value) for value in np.median(pose_array, axis=0)]
            pose_mad = float(np.max(np.median(np.abs(pose_array - np.asarray(pose_center)), axis=0)))
    eye_distances = [float(item["eye_distance_px"]) for item in valid if item.get("eye_distance_px") is not None]
    face_widths = [float(item["face_width_px"]) for item in valid if item.get("face_width_px") is not None]
    face_heights = [float(item["face_height_px"]) for item in valid if item.get("face_height_px") is not None]
    face_areas = [
        float(item["face_width_px"]) * float(item["face_height_px"])
        for item in valid
        if item.get("face_width_px") is not None and item.get("face_height_px") is not None
    ]
    eye_distance_ratios = [
        float(item["eye_distance_px"]) / float(item["face_width_px"])
        for item in valid
        if item.get("eye_distance_px") is not None
        and item.get("face_width_px") is not None
        and float(item["face_width_px"]) > 0.0
    ]
    pretrained_angles = [
        item.get("pretrained_gaze_deg")
        for item in valid
        if isinstance(item.get("pretrained_gaze_deg"), (list, tuple))
        and len(item["pretrained_gaze_deg"]) == 2
    ]
    pretrained_deltas = [
        float(item["raw_model_angle_delta_deg"])
        for item in valid
        if item.get("raw_model_angle_delta_deg") is not None
    ]
    if pretrained_angles:
        pretrained_center = [
            _median([float(angle[index]) for angle in pretrained_angles])
            for index in range(2)
        ]
    else:
        pretrained_center = None
    return {
        "status": "VALID" if feature_mad <= max_feature_mad else "DEGRADED",
        "mode": "CALIBRATED_SENSOR" if feature_mad <= max_feature_mad else "UNSTABLE_WINDOW",
        "reason": "accepted" if feature_mad <= max_feature_mad else "feature_window_unstable",
        "sample_count": len(valid),
        "features": center,
        "feature_mad": feature_mad,
        "quality_median": quality_median,
        "pose": pose_center,
        "pose_mad": pose_mad,
        "eye_distance_px": _median(eye_distances) if eye_distances else None,
        "eye_distance_mad_px": _mad(eye_distances) if eye_distances else None,
        "eye_distance_to_face_width": _median(eye_distance_ratios) if eye_distance_ratios else None,
        "face_width_px": _median(face_widths) if face_widths else None,
        "face_width_mad_px": _mad(face_widths) if face_widths else None,
        "face_height_px": _median(face_heights) if face_heights else None,
        "face_height_mad_px": _mad(face_heights) if face_heights else None,
        "face_bbox_area_px2": _median(face_areas) if face_areas else None,
        "face_bbox_area_mad_px2": _mad(face_areas) if face_areas else None,
        "pretrained_gaze_deg": pretrained_center,
        "pretrained_gaze_sample_count": len(pretrained_angles),
        "pretrained_angle_delta_median_deg": _median(pretrained_deltas) if pretrained_deltas else None,
        "diagnostics": diagnostics,
        **ir_summary,
    }


def fuse_estimates(
    estimates: Mapping[str, tuple[float, float] | None],
    *,
    qualities: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Always return a numerical screen estimate when at least one exists."""

    qualities = qualities or {}
    available = [(name, point) for name, point in estimates.items() if point is not None]
    if not available:
        return {
            "screen": [0.5, 0.5],
            "mode": "HOLD_LAST_ESTIMATE",
            "sensor_count": 0,
            "confidence": 0.0,
            "disagreement": None,
        }
    if len(available) == 1:
        name, point = available[0]
        return {
            "screen": [float(point[0]), float(point[1])],
            "mode": f"{name.upper()}_ONLY",
            "sensor_count": 1,
            "confidence": max(0.05, min(1.0, float(qualities.get(name, 0.5)))),
            "disagreement": None,
        }

    first_name, first = available[0]
    second_name, second = available[1]
    difference = math.hypot(first[0] - second[0], first[1] - second[1])
    first_weight = max(0.05, min(1.0, float(qualities.get(first_name, 0.5))))
    second_weight = max(0.05, min(1.0, float(qualities.get(second_name, 0.5))))
    total = first_weight + second_weight
    point = (
        (first[0] * first_weight + second[0] * second_weight) / total,
        (first[1] * first_weight + second[1] * second_weight) / total,
    )
    confidence = max(0.05, min(1.0, (first_weight + second_weight) * 0.5 * math.exp(-difference * 2.0)))
    return {
        "screen": [float(np.clip(point[0], 0.0, 1.0)), float(np.clip(point[1], 0.0, 1.0))],
        "mode": "STEREO_DUAL_FUSION",
        "sensor_count": 2,
        "confidence": confidence,
        "disagreement": difference,
    }


def evaluate_leave_one_target_out(
    records_by_sensor: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    screen_size: tuple[int, int],
    ridge_lambda: float = DEFAULT_RIDGE_LAMBDA,
) -> dict[str, Any]:
    """Evaluate paired calibrations without splitting correlated frames."""

    width, height = screen_size
    if width <= 0 or height <= 0:
        raise DualContractError("screen dimensions must be positive")
    all_targets = sorted(
        {
            int(record["target_index"])
            for records in records_by_sensor.values()
            for record in records
            if "target_index" in record
        }
    )
    fold_errors: dict[str, list[float]] = {name: [] for name in records_by_sensor}
    fold_errors["fused"] = []
    fold_counts = 0
    evaluation_count = 0
    for held_out in all_targets:
        fitted: dict[str, MappingModel] = {}
        test_records: dict[str, list[Mapping[str, Any]]] = {}
        for name, records in records_by_sensor.items():
            train = [record for record in records if int(record["target_index"]) != held_out]
            test_records[name] = [record for record in records if int(record["target_index"]) == held_out]
            if len(train) >= DESIGN_COUNT and test_records[name]:
                fitted[name] = fit_mapping(train, ridge_lambda=ridge_lambda)
        if len(fitted) < 1:
            continue
        trial_ids = sorted(
            {
                record.get("trial_id")
                for items in test_records.values()
                for record in items
                if record.get("trial_id") is not None
            }
        )
        for trial_id in trial_ids:
            predictions: dict[str, tuple[float, float] | None] = {}
            qualities: dict[str, float] = {}
            target: tuple[float, float] | None = None
            for name, model in fitted.items():
                record = next(
                    (item for item in test_records[name] if item.get("trial_id") == trial_id),
                    None,
                )
                if record is None:
                    continue
                predictions[name] = model.predict(_record_features(record))
                qualities[name] = float(record.get("quality", 0.5))
                target = tuple(float(value) for value in record["target"])
                fold_errors[name].append(
                    math.hypot(
                        (predictions[name][0] - target[0]) * width,
                        (predictions[name][1] - target[1]) * height,
                    )
                )
            if target is not None and len(predictions) >= 2:
                fused = fuse_estimates(predictions, qualities=qualities)
                fold_errors["fused"].append(
                    math.hypot(
                        (fused["screen"][0] - target[0]) * width,
                        (fused["screen"][1] - target[1]) * height,
                    )
                )
            evaluation_count += 1
        fold_counts += 1

    summary: dict[str, Any] = {
        "target_fold_count": fold_counts,
        "evaluation_count": evaluation_count,
        "screen_size": [width, height],
    }
    for name, errors in fold_errors.items():
        if errors:
            summary[name] = {
                "count": len(errors),
                "median_error_px": float(np.median(errors)),
                "p95_error_px": float(np.percentile(errors, 95)),
            }
        else:
            summary[name] = {"count": 0, "median_error_px": None, "p95_error_px": None}
    return summary
