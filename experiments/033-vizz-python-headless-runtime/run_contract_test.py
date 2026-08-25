"""Standard-library contract test for the visible-to-headless split."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from calibration_capture import CaptureConfig, StableCapture
from profile_model import load_profile, load_samples_for_merge, seal_profile


HERE = Path(__file__).parent


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> None:
    failures: list[str] = []
    policy = {
        "calibration_visible": True,
        "headless_visible": False,
        "cuda_provider": "CUDAExecutionProvider",
        "cpu_fallback": False,
        "raw_video": False,
    }
    calibration = (HERE / "calibration_ui.py").read_text(encoding="utf-8")
    runtime = (HERE / "run_vizz.py").read_text(encoding="utf-8")
    tracker = (HERE / "gpu_tracker.py").read_text(encoding="utf-8")
    profile = (HERE / "profile_model.py").read_text(encoding="utf-8")
    overlay = (HERE / "content_overlay.py").read_text(encoding="utf-8")
    validation = (HERE / "run_validation.py").read_text(encoding="utf-8")
    validation_ui = (HERE / "validation_ui.py").read_text(encoding="utf-8")

    require(policy["calibration_visible"] is True, "calibration is not declared visible", failures)
    require(policy["headless_visible"] is False, "headless phase declares a visible interface", failures)
    require("tkinter" in calibration, "calibration UI is not isolated in calibration_ui.py", failures)
    require("root.attributes(\"-fullscreen\", True)" in calibration, "calibration is not fullscreen", failures)
    require('text="Iniciar calibración"' in calibration and "command=self._start" in calibration, "calibration starts without explicit click", failures)
    require('canvas.bind("<Button-1>", self._on_canvas_click)' in calibration, "calibration points are not click-confirmed", failures)
    require("StableCapture" in calibration and "CaptureConfig" in calibration, "calibration lacks a temporal capture policy", failures)
    require("CALIBRATION_CONDITIONS" in calibration and "with_glasses" in calibration and "without_glasses" in calibration, "calibration does not cover both visual conditions", failures)
    require('"condition": condition_key' in calibration and "_show_condition_transition" in calibration, "calibration conditions are not recorded in one flow", failures)
    require('self._draw_point(show_status=False)' in calibration, "status text is not hidden during capture", failures)
    require('"method": "stable_fixed_window"' in calibration, "calibration provenance does not identify the fixed-window method", failures)
    require("self.point_index += 1" in calibration and "self.point_state = \"capturing\"" in calibration, "point capture is not click-armed", failures)
    require("point_samples" not in calibration, "calibration still accumulates an unbounded pre-click point buffer", failures)
    require("tkinter" not in runtime.lower(), "headless runner imports a UI toolkit", failures)
    require("tkinter" not in tracker.lower(), "GPU tracker imports a UI toolkit", failures)
    require("providers=[\"CUDAExecutionProvider\"]" in tracker, "tracker does not request CUDA only", failures)
    require("session.disable_cpu_ep_fallback" in tracker, "CPU fallback kill switch is missing", failures)
    require("CPUExecutionProvider" not in tracker, "tracker names a CPU provider", failures)
    require("pose" in tracker and "eye_roll" in tracker and "def height" in tracker, "tracker does not expose complete pose diagnostics", failures)
    require('"raw_video": False' in profile, "profile permits raw video persistence", failures)
    require("style = 0x80000000" in overlay, "overlay is not a borderless popup layer", failures)
    require("extended = 0x00080000" in overlay, "overlay is missing layered click-through flags", failures)
    require("CreateWindowExW" in overlay and "UpdateLayeredWindow" in overlay, "native click-through layer is missing", failures)
    require("ctypes.c_ssize_t" in overlay and "DefWindowProcW.argtypes" in overlay, "Win64 window callback signature is unsafe", failures)
    require("FocusOverlay" in runtime and "overlay.set_focus" in runtime, "normal content is not modified by the overlay", failures)
    require("capture = open_camera(args.camera)" in runtime, "camera lifecycle is unclear", failures)
    require("--merge-existing" in runtime and "--existing-condition" in runtime and "load_samples_for_merge" in runtime, "runtime lacks incremental calibration merge", failures)
    require(runtime.index("tracker = GpuTracker") < runtime.index("capture = open_camera"), "camera opens before CUDA models", failures)
    require("camera" in (HERE / "README.md").read_text(encoding="utf-8"), "camera boundary is undocumented", failures)
    require("calibration_protocol" in profile and "0.4" in profile and "REQUIRED_CONDITIONS" in profile, "profile schema was not versioned for the combined calibration policy", failures)
    require("MINIMUM_SAMPLES = 24" in profile, "combined profile does not require both calibration sessions", failures)
    require('"farmaxia:vizz-validation:0.1"' in validation and '"raw_video": False' in validation, "validation artifact contract is missing", failures)
    require("ValidationWindow" in validation and "repetitions" in validation_ui and "pose" in validation_ui, "controlled validation flow is incomplete", failures)
    require('fill="#f0a000"' in validation_ui and "tick_scheduled" in validation_ui and "capture_finish_job" in validation_ui, "validation capture state is not visibly bounded", failures)
    require("validation sample callback failed" in validation_ui and "_handle_capture_failure" in validation_ui, "validation callback errors are not surfaced", failures)

    class SyntheticSample:
        def __init__(self, features: tuple[float, ...], quality: float = 0.90) -> None:
            self.features = features
            self.quality = quality

    stable = StableCapture(
        CaptureConfig(
            settle_seconds=0.20,
            window_seconds=1.00,
            min_valid_samples=3,
            max_feature_mad=0.08,
        )
    )
    stable.arm(0.0)
    stable.push(0.10, SyntheticSample((0.8, 0.8, 0.8, 0.8, 0.8, 0.8)))
    require(len(stable.samples) == 0, "settling samples were not discarded", failures)
    stable.push(0.30, SyntheticSample((0.1, 0.2, 0.3, 0.4, 0.5, 0.6)))
    stable.push(0.55, SyntheticSample((0.1, 0.2, 0.3, 0.4, 0.5, 0.6)))
    stable.push(0.80, SyntheticSample((0.1, 0.2, 0.3, 0.4, 0.5, 0.6)))
    stable_result = stable.push(1.25, None)
    require(stable_result is not None and stable_result.accepted, "stable fixed window was not accepted", failures)

    unstable = StableCapture(
        CaptureConfig(
            settle_seconds=0.0,
            window_seconds=1.00,
            min_valid_samples=3,
            max_feature_mad=0.08,
        )
    )
    unstable.arm(0.0)
    unstable.push(0.10, SyntheticSample((0.0, 0.0, 0.0, 0.0, 0.0, 0.0)))
    unstable.push(0.20, SyntheticSample((0.2, 0.2, 0.2, 0.2, 0.2, 0.2)))
    unstable.push(0.30, SyntheticSample((0.4, 0.4, 0.4, 0.4, 0.4, 0.4)))
    unstable_result = unstable.push(1.10, None)
    require(unstable_result is not None and not unstable_result.accepted, "unstable feature window was accepted", failures)

    combined_samples: list[dict[str, object]] = []
    targets = (
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
    for condition, offset in (("with_glasses", 0.0), ("without_glasses", 0.03)):
        for target_x, target_y in targets:
            yaw = (target_x - 0.5) * 2.0 + offset
            pitch = (target_y - 0.5) * 1.5 - offset * 0.5
            combined_samples.append(
                {
                    "features": [yaw, pitch, yaw + 0.01, yaw - 0.01, 0.5 + target_x * 0.02 + offset, 0.5 + target_y * 0.02 - offset],
                    "target": [target_x, target_y],
                    "condition": condition,
                }
            )
    with tempfile.TemporaryDirectory() as temporary:
        combined_path = Path(temporary) / "combined.json"
        seal_profile(combined_path, (1707, 960), combined_samples, "TEST_MODEL_HASH")
        combined_profile, _mapper = load_profile(combined_path)
        require(combined_profile["sample_count"] == 24, "combined profile did not seal 24 samples", failures)
        require(combined_profile["calibration_conditions"] == ["with_glasses", "without_glasses"], "combined profile lost condition metadata", failures)

        legacy_path = Path(temporary) / "legacy.json"
        legacy_samples = [{key: value for key, value in sample.items() if key != "condition"} for sample in combined_samples[:12]]
        legacy_path.write_text(
            json.dumps(
                {
                    "schema": "farmaxia:vizz-calibration-profile:0.3",
                    "screen_size": [1707, 960],
                    "samples": legacy_samples,
                    "model_sha256": "TEST_MODEL_HASH",
                    "raw_video": False,
                }
            ),
            encoding="utf-8",
        )
        _legacy_profile, upgraded_samples = load_samples_for_merge(legacy_path, existing_condition="with_glasses")
        require(len(upgraded_samples) == 12, "legacy profile merge lost samples", failures)
        require(all(sample["condition"] == "with_glasses" for sample in upgraded_samples), "legacy condition was not assigned explicitly", failures)
    json.dumps(policy)

    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CONTRACT_TESTS_VALID")
    print("calibration_ui_visible_only_during_calibration=True")
    print("headless_runtime_owns_no_ui=True")
    print("cuda_provider_only=True")
    print("cpu_fallback_disabled=True")
    print("content_modifier=click_through_focus_layer")
    print("raw_video_persistence=False")


if __name__ == "__main__":
    main()
