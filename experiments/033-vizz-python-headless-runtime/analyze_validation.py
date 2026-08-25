"""Offline grouped audit for the VIZZ calibration/validation boundary.

This tool never captures camera frames and never mutates the calibration
profile. It keeps the cross-session claim honest: pose-aware models cannot be
fit across sessions when calibration did not persist pose proxies.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from profile_model import load_profile


MODEL_NAMES = ("M0", "M1", "M2")
POSE_COUNT = 6
LAMBDA_GRID = np.logspace(-6, 3, 10)
CONDITION_CODE = {"with_glasses": 0.0, "without_glasses": 1.0}
CALIBRATION_POINTS = (
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


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected an object in {path}")
    return payload


def normalize_samples(raw_samples: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for raw in raw_samples:
        if not isinstance(raw, dict):
            raise ValueError("samples must contain objects")
        sample = dict(raw)
        if "target_index" not in sample:
            target = tuple(float(value) for value in sample.get("target", ()))
            matches = [index for index, point in enumerate(CALIBRATION_POINTS) if target == point]
            if len(matches) != 1:
                raise ValueError(f"sample target does not match exactly one calibration point: {target}")
            sample["target_index"] = matches[0]
        normalized.append(sample)
    return normalized


def model_values(sample: dict[str, Any], model: str) -> np.ndarray:
    features = np.asarray(sample.get("features"), dtype=np.float64)
    if features.shape != (6,) or not np.all(np.isfinite(features)):
        raise ValueError("sample has invalid six-feature vector")
    values: list[float] = features.tolist()
    if model in {"M1", "M2"}:
        pose = np.asarray(sample.get("pose"), dtype=np.float64)
        if pose.shape != (POSE_COUNT,) or not np.all(np.isfinite(pose)):
            raise ValueError(f"{model} requires six finite pose proxies")
        values.extend(pose.tolist())
    if model == "M2":
        condition = sample.get("condition")
        if condition not in CONDITION_CODE:
            raise ValueError("M2 requires a recognized visual condition")
        values.append(CONDITION_CODE[condition])
    return np.asarray(values, dtype=np.float64)


def targets(samples: Iterable[dict[str, Any]]) -> list[int]:
    return sorted({int(sample["target_index"]) for sample in samples})


def fit_ridge(samples: list[dict[str, Any]], model: str, ridge_lambda: float) -> dict[str, np.ndarray]:
    if not samples:
        raise ValueError("cannot fit an empty sample set")
    raw = np.vstack([model_values(sample, model) for sample in samples])
    mean = raw.mean(axis=0)
    scale = raw.std(axis=0)
    scale[scale < 1e-12] = 1.0
    scaled = (raw - mean) / scale
    design = np.column_stack([np.ones(len(samples)), scaled])
    target = np.asarray([sample["target"] for sample in samples], dtype=np.float64)
    if target.shape != (len(samples), 2) or not np.all(np.isfinite(target)):
        raise ValueError("samples have invalid two-coordinate targets")
    penalty = np.eye(design.shape[1], dtype=np.float64)
    penalty[0, 0] = 0.0
    coefficients = np.linalg.solve(
        design.T @ design + float(ridge_lambda) * penalty,
        design.T @ target,
    )
    return {"mean": mean, "scale": scale, "coefficients": coefficients}


def predict(fitted: dict[str, np.ndarray], samples: list[dict[str, Any]], model: str) -> np.ndarray:
    raw = np.vstack([model_values(sample, model) for sample in samples])
    scaled = (raw - fitted["mean"]) / fitted["scale"]
    design = np.column_stack([np.ones(len(samples)), scaled])
    return design @ fitted["coefficients"]


def normalized_errors(predictions: np.ndarray, samples: list[dict[str, Any]]) -> np.ndarray:
    target = np.asarray([sample["target"] for sample in samples], dtype=np.float64)
    return np.linalg.norm(predictions - target, axis=1)


def select_lambda(samples: list[dict[str, Any]], model: str) -> float:
    groups = targets(samples)
    if len(groups) < 2:
        return float(LAMBDA_GRID[0])
    scores: list[tuple[float, float]] = []
    for candidate in LAMBDA_GRID:
        fold_errors: list[float] = []
        for group in groups:
            inner_train = [sample for sample in samples if int(sample["target_index"]) != group]
            inner_test = [sample for sample in samples if int(sample["target_index"]) == group]
            fitted = fit_ridge(inner_train, model, float(candidate))
            fold_errors.extend(normalized_errors(predict(fitted, inner_test, model), inner_test).tolist())
        scores.append((float(np.mean(np.square(fold_errors))), float(candidate)))
    return min(scores, key=lambda pair: (pair[0], pair[1]))[1]


def pixel_errors(
    predictions: np.ndarray,
    samples: list[dict[str, Any]],
    screen_size: tuple[int, int],
) -> list[dict[str, Any]]:
    width, height = screen_size
    target = np.asarray([sample["target"] for sample in samples], dtype=np.float64)
    clipped = np.clip(predictions, 0.0, 1.0)
    deltas = clipped - target
    errors = np.sqrt((deltas[:, 0] * width) ** 2 + (deltas[:, 1] * height) ** 2)
    return [
        {
            "target_index": int(sample["target_index"]),
            "condition": sample["condition"],
            "error_px": float(error),
        }
        for sample, error in zip(samples, errors)
    ]


def metric(errors: list[float]) -> dict[str, float | int]:
    values = np.asarray(errors, dtype=np.float64)
    if not len(values):
        return {"n": 0}
    return {
        "n": int(len(values)),
        "median_px": float(np.percentile(values, 50)),
        "p95_px": float(np.percentile(values, 95)),
        "mean_px": float(values.mean()),
        "max_px": float(values.max()),
    }


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {"overall": metric([float(record["error_px"]) for record in records])}
    by_condition: dict[str, Any] = {}
    by_target: dict[str, Any] = {}
    for condition in sorted({record["condition"] for record in records}):
        by_condition[condition] = metric(
            [float(record["error_px"]) for record in records if record["condition"] == condition]
        )
    for target_index in sorted({int(record["target_index"]) for record in records}):
        by_target[str(target_index)] = metric(
            [float(record["error_px"]) for record in records if int(record["target_index"]) == target_index]
        )
    summary["by_condition"] = by_condition
    summary["by_target"] = by_target
    return summary


def grouped_evaluation(
    train_samples: list[dict[str, Any]],
    test_samples: list[dict[str, Any]],
    model: str,
    screen_size: tuple[int, int],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for target_index in targets(test_samples):
        train = [sample for sample in train_samples if int(sample["target_index"]) != target_index]
        test = [sample for sample in test_samples if int(sample["target_index"]) == target_index]
        ridge_lambda = select_lambda(train, model)
        fitted = fit_ridge(train, model, ridge_lambda)
        records.extend(pixel_errors(predict(fitted, test, model), test, screen_size))
        for record in records[-len(test) :]:
            record["lambda"] = ridge_lambda
    return {"summary": summarize(records), "records": records}


def evaluate_existing_profile(
    profile_path: Path,
    samples: list[dict[str, Any]],
    screen_size: tuple[int, int],
) -> dict[str, Any]:
    _profile, mapper = load_profile(profile_path)
    predictions = np.asarray([mapper.predict(sample["features"]) for sample in samples], dtype=np.float64)
    return {"summary": summarize(pixel_errors(predictions, samples, screen_size))}


def run_analysis(calibration_path: Path, validation_path: Path, output_path: Path) -> dict[str, Any]:
    profile = load_json(calibration_path)
    validation = load_json(validation_path)
    calibration_raw = profile.get("samples")
    samples_raw = validation.get("samples")
    if not isinstance(calibration_raw, list) or not isinstance(samples_raw, list):
        raise ValueError("both inputs must contain a samples list")
    calibration = normalize_samples(calibration_raw)
    samples = normalize_samples(samples_raw)
    if len(calibration) < 2 or len(samples) < 2:
        raise ValueError("analysis requires calibration and validation samples")
    screen_size = tuple(int(value) for value in profile["screen_size"])
    calibration_pose = all(sample.get("pose") is not None for sample in calibration)
    validation_pose = all(sample.get("pose") is not None for sample in samples)

    result: dict[str, Any] = {
        "schema": "farmaxia:vizz-validation-analysis:0.1",
        "inputs": {
            "calibration": str(calibration_path),
            "validation": str(validation_path),
            "profile_schema": profile.get("schema"),
            "validation_schema": validation.get("schema"),
            "calibration_sample_count": len(calibration),
            "validation_sample_count": len(samples),
            "screen_size": list(screen_size),
        },
        "design": {
            "outer_group": "target_index",
            "model_selection": "inner_leave_one_target_out_ridge",
            "frame_level_splits": False,
            "condition_code": CONDITION_CODE,
        },
        "pose_available_in_calibration": calibration_pose,
        "pose_available_in_validation": validation_pose,
        "models": {},
        "limitations": [],
    }

    result["models"]["legacy_profile_validation"] = {
        "scope": "fixed_profile_to_validation",
        "status": "evaluated",
        **evaluate_existing_profile(calibration_path, samples, screen_size),
    }
    result["models"]["M0_cross_session"] = {
        "scope": "calibration_to_validation_grouped_target_holdout",
        "status": "evaluated",
        **grouped_evaluation(calibration, samples, "M0", screen_size),
    }

    if not calibration_pose:
        result["limitations"].append(
            "M1/M2/M3 cross-session comparison is UNKNOWN_NOT_IDENTIFIABLE: calibration persisted no pose proxies."
        )
        for model in ("M1", "M2"):
            result["models"][f"{model}_cross_session"] = {
                "scope": "calibration_to_validation_grouped_target_holdout",
                "status": "UNKNOWN_NOT_IDENTIFIABLE",
                "reason": "calibration samples contain no pose field",
            }
    if not validation_pose:
        result["limitations"].append("Validation samples have no complete pose proxies; within-session M1/M2 were not run.")
    else:
        for model in MODEL_NAMES:
            result["models"][f"{model}_within_validation"] = {
                "scope": "validation_only_grouped_target_holdout_diagnostic",
                "status": "diagnostic_only",
                **grouped_evaluation(samples, samples, model, screen_size),
            }
    result["limitations"].extend(
        [
            "The validation session has one representative per target and is not a production generalization study.",
            "No model is accepted or written back to the calibration profile by this tool.",
            "Pixel error is not converted to visual degrees because physical screen geometry and viewing distance are absent.",
        ]
    )
    result["decision"] = {
        "status": "diagnostic_only",
        "accepted_model": None,
        "profile_mutated": False,
        "reason": "pose-aware cross-session models are not identifiable from the persisted calibration artifact",
    }
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline grouped audit of VIZZ validation data")
    parser.add_argument("--calibration", type=Path, default=Path(".vizz-calibration.json"))
    parser.add_argument("--validation", type=Path, default=Path(".vizz-validation-smoke.json"))
    parser.add_argument("--output", type=Path, default=Path(".vizz-validation-analysis.json"))
    args = parser.parse_args()
    result = run_analysis(args.calibration, args.validation, args.output)
    print(json.dumps(result["models"], indent=2))
    print("ANALYSIS_WRITTEN", args.output)


if __name__ == "__main__":
    main()
