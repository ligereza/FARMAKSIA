"""Contract and kill tests for the relative binocular ray adapter."""

from __future__ import annotations

import math
import sys
from pathlib import Path


HERE = Path(__file__).parent
TRACKER_DIR = HERE.parent / "033-vizz-python-headless-runtime"
sys.path.insert(0, str(TRACKER_DIR))

from ray_proxy import build_binocular_ray_proxy  # noqa: E402


def main() -> None:
    valid, reason = build_binocular_ray_proxy(
        left_center_px=(300.0, 240.0),
        right_center_px=(340.0, 240.0),
        left_yaw_deg=-3.0,
        left_pitch_deg=1.0,
        right_yaw_deg=3.0,
        right_pitch_deg=1.0,
        width=640,
        height=480,
        disagreement_deg=6.0,
    )
    failures: list[str] = []
    if valid is None or reason is not None:
        failures.append("valid binocular input did not produce a proxy")
    else:
        if valid.coordinate_frame != "camera_proxy_normalized_v1":
            failures.append("coordinate frame is not versioned")
        if valid.status != "VALID_RELATIVE_PROXY":
            failures.append("valid output was not explicitly marked relative-only")
        if valid.interocular_baseline_proxy <= 0.0:
            failures.append("interocular baseline was lost")
        for direction in (valid.left_direction, valid.right_direction):
            if abs(math.sqrt(sum(value * value for value in direction)) - 1.0) > 1e-9:
                failures.append("ray direction was not normalized")
        payload = valid.as_dict()
        if payload["left_origin"] == payload["right_origin"]:
            failures.append("both eyes collapsed to one origin")

    bad_disagreement, bad_reason = build_binocular_ray_proxy(
        left_center_px=(300.0, 240.0),
        right_center_px=(340.0, 240.0),
        left_yaw_deg=-40.0,
        left_pitch_deg=0.0,
        right_yaw_deg=40.0,
        right_pitch_deg=0.0,
        width=640,
        height=480,
        disagreement_deg=80.0,
    )
    if bad_disagreement is not None or bad_reason != "binocular_disagreement_too_large":
        failures.append("large binocular disagreement did not fail closed")

    coincident, coincident_reason = build_binocular_ray_proxy(
        left_center_px=(320.0, 240.0),
        right_center_px=(320.0, 240.0),
        left_yaw_deg=0.0,
        left_pitch_deg=0.0,
        right_yaw_deg=0.0,
        right_pitch_deg=0.0,
        width=640,
        height=480,
        disagreement_deg=0.0,
    )
    if coincident is not None or coincident_reason != "interocular_baseline_too_small":
        failures.append("coincident eye centres did not fail closed")

    capture_script = (HERE / "run_quality_capture.py").read_text(encoding="utf-8")
    if "screen_content_mutated" not in capture_script or '"raw_video": False' not in capture_script:
        failures.append("quality capture does not declare screen/video boundaries")
    if "FocusOverlay" in capture_script or "CalibrationWindow" in capture_script:
        failures.append("quality capture unexpectedly imports a visible VIZZ surface")
    if capture_script.index("tracker = GpuTracker") > capture_script.index("capture = open_camera"):
        failures.append("quality capture opens camera before CUDA preflight")
    if "binocular_ray_proxy" not in capture_script or "mouse_screen" not in capture_script:
        failures.append("quality capture does not persist rays and optional pointer")
    if "KeyboardActivity" not in capture_script or "keyboard_event_count" not in capture_script:
        failures.append("quality capture does not expose count-only keyboard activity")
    if '"key_values_persisted": False' not in capture_script or "text_persisted" not in capture_script:
        failures.append("quality capture does not declare keyboard/text privacy boundary")

    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("VIZZ_053_GPU_BINOCULAR_RAY_ADAPTER_CONTRACT_VALID")


if __name__ == "__main__":
    main()
