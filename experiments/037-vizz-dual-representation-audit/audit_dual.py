"""Audit readiness for legacy versus eye-centric validation artifacts."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("samples"), list):
        raise ValueError(f"invalid samples artifact: {path}")
    return payload


def finite_vector(value: Any, length: int) -> bool:
    return isinstance(value, list) and len(value) == length and all(
        isinstance(item, (int, float)) and math.isfinite(float(item)) for item in value
    )


def summarize(payload: dict[str, Any]) -> dict[str, Any]:
    samples = payload["samples"]
    legacy = sum(finite_vector(sample.get("features"), 6) for sample in samples if isinstance(sample, dict))
    eye = sum(finite_vector(sample.get("eye_centric"), 6) for sample in samples if isinstance(sample, dict))
    distance = sum(
        isinstance(sample, dict)
        and isinstance(sample.get("eye_centric_distance_px"), (int, float))
        and math.isfinite(float(sample["eye_centric_distance_px"]))
        and float(sample["eye_centric_distance_px"]) > 0.0
        for sample in samples
    )
    roll = sum(
        isinstance(sample, dict)
        and isinstance(sample.get("eye_centric_roll_rad"), (int, float))
        and math.isfinite(float(sample["eye_centric_roll_rad"]))
        for sample in samples
    )
    return {
        "schema": payload.get("schema"),
        "sample_count": len(samples),
        "legacy_complete": legacy,
        "eye_centric_complete": eye,
        "eye_centric_distance_complete": distance,
        "eye_centric_roll_complete": roll,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    calibration = load(args.calibration)
    validation = load(args.validation)
    calibration_summary = summarize(calibration)
    validation_summary = summarize(validation)
    eye_ready = (
        calibration_summary["eye_centric_complete"] == calibration_summary["sample_count"]
        and validation_summary["eye_centric_complete"] == validation_summary["sample_count"]
    )
    result = {
        "schema": "farmaxia:vizz-dual-representation-audit:0.1",
        "inputs": {"calibration": str(args.calibration), "validation": str(args.validation)},
        "calibration": calibration_summary,
        "validation": validation_summary,
        "models": {
            "legacy": {"status": "AVAILABLE_FOR_EXISTING_ANALYSIS"},
            "eye_centric": {
                "status": "READY_FOR_GROUPED_COMPARISON" if eye_ready else "UNKNOWN_NOT_IDENTIFIABLE",
                "reason": None if eye_ready else "eye_centric_not_persisted_in_both_artifacts",
            },
        },
        "human_data": "present_in_existing_inputs_only",
        "raw_frames": False,
        "screen_mapper_changed": False,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print("DUAL_AUDIT_VALID")


if __name__ == "__main__":
    main()
