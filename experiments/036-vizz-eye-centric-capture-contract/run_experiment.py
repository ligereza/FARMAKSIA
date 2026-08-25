"""Verify that eye-centric diagnostics survive the stable capture boundary."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


RUNTIME = Path(__file__).resolve().parents[1] / "033-vizz-python-headless-runtime"
sys.path.insert(0, str(RUNTIME))

from calibration_capture import CaptureConfig, StableCapture  # noqa: E402
from gpu_tracker import _eye_centric_geometry  # noqa: E402


class SyntheticSample:
    features = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6)
    quality = 0.95
    pose = (0.5, 0.5, 0.2, 0.3, 0.01, 0.08)

    def __init__(self, eye_centric: tuple[float, ...], distance: float, roll: float) -> None:
        self.eye_centric = eye_centric
        self.eye_centric_distance_px = distance
        self.eye_centric_roll_rad = roll
        self.eye_centric_unknown_reason = None


def synthetic_eye_clouds() -> tuple[np.ndarray, np.ndarray]:
    left = np.zeros((481, 3), dtype=np.float32)
    right = np.zeros((481, 3), dtype=np.float32)
    left[:32] = np.asarray([-30.0, 0.0, 0.0], dtype=np.float32)
    right[:32] = np.asarray([30.0, 0.0, 0.0], dtype=np.float32)
    for index in (248, 252, 224, 228, 232, 236, 240, 244):
        left[index] = np.asarray([-27.0, -2.0, 5.0], dtype=np.float32)
        right[index] = np.asarray([27.0, 1.0, 5.0], dtype=np.float32)
    return left, right


def main() -> None:
    left, right = synthetic_eye_clouds()
    eye_centric, distance, roll = _eye_centric_geometry(left, right)
    if eye_centric is None or distance is None or roll is None:
        raise SystemExit("eye-centric tracker output was unexpectedly UNKNOWN")

    capture = StableCapture(
        CaptureConfig(
            settle_seconds=0.0,
            window_seconds=1.0,
            min_valid_samples=3,
            require_pose=True,
        )
    )
    capture.arm(0.0)
    for timestamp in (0.1, 0.2, 0.3):
        capture.push(timestamp, SyntheticSample(eye_centric, distance, roll))
    result = capture.push(1.1, None)
    if result is None or not result.accepted:
        raise SystemExit("stable capture rejected the valid synthetic sample")

    payload = {
        "schema": "farmaxia:vizz-eye-centric-capture-contract:0.1",
        "legacy_feature_count": len(result.features or ()),
        "eye_centric_count": len(result.eye_centric or ()),
        "eye_centric_valid_count": result.eye_centric_valid_count,
        "eye_centric_distance_px": result.eye_centric_distance_px,
        "eye_centric_roll_rad": result.eye_centric_roll_rad,
        "eye_centric_unknown_reason": result.eye_centric_unknown_reason,
        "human_data": False,
        "raw_frames": False,
        "all_properties_hold": (
            len(result.features or ()) == 6
            and len(result.eye_centric or ()) == 6
            and result.eye_centric_valid_count == 3
            and result.eye_centric_unknown_reason is None
        ),
    }
    print(json.dumps(payload, indent=2))
    if not payload["all_properties_hold"]:
        raise SystemExit(1)
    print("EYE_CENTRIC_CAPTURE_VALID")


if __name__ == "__main__":
    main()
