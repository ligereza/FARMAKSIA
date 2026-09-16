"""Positive tests for the VIZZ distance/scale contract."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    completed = subprocess.run(
        [sys.executable, str(HERE / "run_experiment.py")],
        cwd=HERE.parents[1],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode:
        raise SystemExit(completed.stderr or "experiment 084 failed")
    payload = json.loads(completed.stdout)
    assert payload["status"] == "VIZZ_DISTANCE_SCALE_CONTRACT_VERIFIED"
    assert payload["contract"]["required_measurements"] == [
        "eye_distance_px",
        "face_width_px",
    ]
    assert payload["contract"]["card_role"] == "one_time_reference_only"
    observations = {row["name"]: row for row in payload["observations"]}
    closer = observations["closer"]
    farther = observations["farther"]
    posed = observations["same_distance_pose"]
    contradictory = observations["contradictory_signals"]
    assert closer["estimate"]["status"] == "VALID"
    assert abs(closer["estimate"]["fused_scale"] - 4.0 / 3.0) < 1e-9
    assert abs(closer["constant_angle_target"]["diameter_px"] - 75.0) < 1e-9
    assert abs(farther["constant_angle_target"]["diameter_px"] - 150.0) < 1e-9
    assert abs(posed["estimate"]["fused_scale"] - 1.0) < 1e-9
    assert contradictory["estimate"]["status"] == "UNKNOWN"
    assert payload["safety"] == {
        "camera_started": False,
        "network_used": False,
        "input_injected": False,
        "raw_frames_persisted": False,
        "screen_mutated": False,
    }
    capture = (HERE / "run_capture.py").read_text(encoding="utf-8")
    assert "GpuTracker" in capture
    assert "collect_reference" in capture and "key == 32" in capture
    assert '"raw_video": False' in capture
    assert "observe_face" in capture and "tracker.detect_face" in capture
    assert "scale_only=True" in capture
    tracker_source = (HERE.parents[1] / "experiments/033-vizz-python-headless-runtime/gpu_tracker.py").read_text(encoding="utf-8")
    assert "if scale_only:" in tracker_source and "gaze model is required outside scale_only mode" in tracker_source
    assert "key == 32 and observation is not None" in capture
    assert "ROSTRO + 2 OJOS OK" in capture
    assert "card_role\": \"not_used_for_relative_scale\"" in capture
    assert "setMouseCallback" not in capture
    assert '"camera_preview_during_p0": True' in capture
    assert '"camera_preview_after_p0": False' in capture
    assert "pose_correction" in capture
    assert "cv2.imshow(WINDOW_NAME, canvas)" in capture
    assert "imshow(WINDOW_NAME, frame)" not in capture
    print("FARMAXIA_084_VIZZ_DISTANCE_SCALE_CONTRACT_VALID")


if __name__ == "__main__":
    main()
