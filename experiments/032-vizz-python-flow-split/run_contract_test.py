"""Static and transition tests for the two-phase VIZZ Python flow."""

from __future__ import annotations

import json
from pathlib import Path

from calibration_ui import CALIBRATION_POINT_COUNT, seal_local_profile
from flow_contract import FlowContractError, Phase, VizzFlow


HERE = Path(__file__).parent


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> None:
    failures: list[str] = []
    policy = json.loads((HERE / "runtime_policy.json").read_text(encoding="utf-8"))
    calibration = (HERE / "calibration_ui.py").read_text(encoding="utf-8")
    runtime = (HERE / "runtime.py").read_text(encoding="utf-8")

    require(policy["phases"]["calibration_ui"]["visible_interface"] is True, "calibration must be visible", failures)
    require(policy["phases"]["headless_runtime"]["visible_interface"] is False, "runtime must be invisible", failures)
    require(policy["gpu_policy"]["requested_providers"] == ["CUDAExecutionProvider"], "runtime permits a provider fallback", failures)
    require(policy["gpu_policy"]["cpu_fallback"] is False, "CPU fallback is not disabled", failures)
    require(policy["content_modifier"]["vizz_ui_visible_after_calibration"] is False, "VIZZ UI remains visible after calibration", failures)
    require("tkinter" not in runtime.lower(), "headless runtime imports a UI toolkit", failures)
    require("PySide" not in runtime and "pygame" not in runtime, "headless runtime owns a visible UI", failures)
    require('providers=["CUDAExecutionProvider"]' in runtime, "CUDA-only session is not explicit", failures)
    require("CPUExecutionProvider" not in runtime, "runtime contains a CPU provider fallback", failures)
    require("getUserMedia" not in runtime and "VideoCapture" not in runtime, "runtime opens a device before CUDA integration", failures)
    require('"raw_video": False' in calibration, "calibration profile does not disable raw video persistence", failures)

    flow = VizzFlow()
    flow.start_calibration()
    require(flow.phase is Phase.CALIBRATION_UI and flow.interface_visible, "calibration phase is not visible", failures)
    for _ in range(CALIBRATION_POINT_COUNT):
        flow.capture_sample(feature_vector_present=True)
    profile_path = HERE / "_contract_profile.json"
    sealed = seal_local_profile(
        profile_path,
        (1920, 1080),
        ({"target": [0.5, 0.5], "features": [0.0] * 16} for _ in range(CALIBRATION_POINT_COUNT)),
        "model-hash",
    )
    flow.seal_profile(sealed)
    require(flow.phase is Phase.PROFILE_SEALED and not flow.interface_visible, "profile sealing did not close UI", failures)
    flow.start_headless_runtime(cuda_ready=True)
    flow.attach_content_modifier(modifier_ready=True)
    require(flow.phase is Phase.CONTENT_MODIFIER and not flow.interface_visible, "content modifier exposes VIZZ UI", failures)
    flow.stop()
    require(flow.phase is Phase.STOPPED and flow.sample_count == 0, "stop did not clear volatile flow state", failures)
    profile_path.unlink(missing_ok=True)

    try:
        invalid_flow = VizzFlow()
        invalid_flow.start_calibration()
        invalid_flow.seal_profile(HERE / "invalid.json", minimum_samples=CALIBRATION_POINT_COUNT)
    except FlowContractError:
        pass
    else:
        failures.append("incomplete calibration was accepted")

    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CONTRACT_TESTS_VALID")
    print("calibration_ui_visible_only_during_calibration=True")
    print("headless_runtime_owns_no_ui=True")
    print("content_modifier_is_external_to_vizz_ui=True")
    print("cuda_provider_only=True")
    print("raw_video_persistence=False")


if __name__ == "__main__":
    main()
