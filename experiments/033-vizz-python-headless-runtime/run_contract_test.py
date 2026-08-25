"""Standard-library contract test for the visible-to-headless split."""

from __future__ import annotations

import json
from pathlib import Path


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

    require(policy["calibration_visible"] is True, "calibration is not declared visible", failures)
    require(policy["headless_visible"] is False, "headless phase declares a visible interface", failures)
    require("tkinter" in calibration, "calibration UI is not isolated in calibration_ui.py", failures)
    require("root.attributes(\"-fullscreen\", True)" in calibration, "calibration is not fullscreen", failures)
    require("tkinter" not in runtime.lower(), "headless runner imports a UI toolkit", failures)
    require("tkinter" not in tracker.lower(), "GPU tracker imports a UI toolkit", failures)
    require("providers=[\"CUDAExecutionProvider\"]" in tracker, "tracker does not request CUDA only", failures)
    require("session.disable_cpu_ep_fallback" in tracker, "CPU fallback kill switch is missing", failures)
    require("CPUExecutionProvider" not in tracker, "tracker names a CPU provider", failures)
    require('"raw_video": False' in profile, "profile permits raw video persistence", failures)
    require("style = 0x80000000" in overlay, "overlay is not a borderless popup layer", failures)
    require("extended = 0x00080000" in overlay, "overlay is missing layered click-through flags", failures)
    require("CreateWindowExW" in overlay and "UpdateLayeredWindow" in overlay, "native click-through layer is missing", failures)
    require("FocusOverlay" in runtime and "overlay.set_focus" in runtime, "normal content is not modified by the overlay", failures)
    require("capture = open_camera(args.camera)" in runtime, "camera lifecycle is unclear", failures)
    require(runtime.index("tracker = GpuTracker") < runtime.index("capture = open_camera"), "camera opens before CUDA models", failures)
    require("camera" in (HERE / "README.md").read_text(encoding="utf-8"), "camera boundary is undocumented", failures)
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
