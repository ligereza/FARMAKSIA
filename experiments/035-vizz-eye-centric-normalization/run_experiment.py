"""Synthetic metamorphic test for the eye-centric representation."""

from __future__ import annotations

import json
import math

import numpy as np

from eye_centric import normalize_eye_pair


def transformed(points: np.ndarray, scale: float, angle: float, translation: tuple[float, float]) -> np.ndarray:
    rotation = np.asarray(
        [[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]],
        dtype=np.float64,
    )
    result = points.copy()
    result[:, :2] = (points[:, :2] @ rotation.T) * scale + np.asarray(translation)
    return result


def main() -> None:
    left = np.asarray(
        [[-0.30, 0.04], [-0.25, -0.03], [-0.20, 0.02], [-0.27, 0.08]],
        dtype=np.float64,
    )
    right = np.asarray(
        [[0.20, 0.03], [0.25, -0.04], [0.30, 0.01], [0.26, 0.07]],
        dtype=np.float64,
    )
    baseline = normalize_eye_pair(left, right)
    cases = []
    for scale, angle, translation in (
        (0.5, 0.0, (2.0, -1.0)),
        (1.0, math.radians(12.0), (20.0, 30.0)),
        (2.5, math.radians(-27.0), (-80.0, 15.0)),
    ):
        candidate = normalize_eye_pair(
            transformed(left, scale, angle, translation),
            transformed(right, scale, angle, translation),
        )
        error = max(
            float(np.max(np.abs(candidate.left - baseline.left))),
            float(np.max(np.abs(candidate.right - baseline.right))),
        )
        cases.append({"scale": scale, "roll_deg": math.degrees(angle), "max_error": error})

    collapsed = normalize_eye_pair(left, left)
    result = {
        "schema": "farmaxia:vizz-eye-centric-normalization:0.1",
        "case_count": len(cases),
        "cases": cases,
        "max_invariance_error": max(case["max_error"] for case in cases),
        "collapsed_eye_unknown": collapsed.unknown_reason,
        "head_yaw_pitch_invariance_claimed": False,
        "human_data": False,
        "raw_frames": False,
    }
    result["all_properties_hold"] = (
        baseline.valid
        and result["max_invariance_error"] < 1e-12
        and collapsed.unknown_reason == "interocular_distance_too_small"
    )
    print(json.dumps(result, indent=2))
    if not result["all_properties_hold"]:
        raise SystemExit(1)
    print("EYE_CENTRIC_VALID")


if __name__ == "__main__":
    main()
