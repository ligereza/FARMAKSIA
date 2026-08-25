"""Synthetic contract for the GitHub-sourced pretrained gaze bridge."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


RUNTIME = Path(__file__).resolve().parents[1] / "033-vizz-python-headless-runtime"
sys.path.insert(0, str(RUNTIME))

from pretrained_gaze import (  # noqa: E402
    MODEL_RELEASE,
    MODEL_SOURCE,
    decode_mobileone_angles,
    preprocess_mobileone_face,
)


def main() -> None:
    face = np.zeros((32, 48, 3), dtype=np.uint8)
    tensor = preprocess_mobileone_face(face)
    yaw = np.full((1, 90), -100.0, dtype=np.float32)
    pitch = np.full((1, 90), -100.0, dtype=np.float32)
    yaw[0, 50] = 100.0
    pitch[0, 40] = 100.0
    decoded = decode_mobileone_angles(yaw, pitch)
    result = {
        "schema": "farmaxia:vizz-github-pretrained-gaze:0.1",
        "source": MODEL_SOURCE,
        "release": MODEL_RELEASE,
        "input_shape": list(tensor.shape),
        "input_finite": bool(np.isfinite(tensor).all()),
        "decoded_yaw_deg": decoded[0],
        "decoded_pitch_deg": decoded[1],
        "screen_coordinates_claimed": False,
        "cpu_fallback_allowed": False,
        "human_data": False,
        "raw_frames": False,
    }
    result["all_properties_hold"] = (
        result["input_shape"] == [1, 3, 448, 448]
        and result["input_finite"]
        and abs(result["decoded_yaw_deg"] - 20.0) < 1e-4
        and abs(result["decoded_pitch_deg"] + 20.0) < 1e-4
        and result["screen_coordinates_claimed"] is False
        and result["cpu_fallback_allowed"] is False
    )
    print(json.dumps(result, indent=2))
    if not result["all_properties_hold"]:
        raise SystemExit(1)
    print("GITHUB_PRETRAINED_GAZE_VALID")


if __name__ == "__main__":
    main()
