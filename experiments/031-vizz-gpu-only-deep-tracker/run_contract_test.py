"""Static safety and GPU-only contract test for VIZZ 031; never opens a device."""

from __future__ import annotations

import json
import re
from pathlib import Path


HERE = Path(__file__).parent


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> None:
    failures: list[str] = []
    policy = json.loads((HERE / "runtime_policy.json").read_text(encoding="utf-8"))
    html = (HERE / "index.html").read_text(encoding="utf-8")
    js = (HERE / "app.js").read_text(encoding="utf-8")

    require(policy["schema"] == "farmaxia:vizz-gpu-only-runtime:0.1", "wrong runtime policy schema", failures)
    require(policy["gpu_policy"]["onnx_execution_providers"] == ["webgpu"], "ONNX policy permits a fallback", failures)
    require(policy["gpu_policy"]["mediapipe_delegate"] == "GPU", "MediaPipe policy is not GPU-only", failures)
    require(policy["gpu_policy"]["cpu_or_wasm_fallback"] is False, "CPU/WASM fallback is not disabled", failures)
    require(policy["privacy"]["consent_required"] is True, "camera consent is not required", failures)
    require(policy["privacy"]["camera_default"] == "off", "camera is not off by default", failures)
    require(policy["privacy"]["sample_persistence"] == "none", "samples may persist", failures)

    scripts = re.findall(r'<script[^>]+src="([^"]+)"', html, flags=re.IGNORECASE)
    require(scripts == ["./vendor/ort.webgpu.min.js", "./app.js"], "HTML has an unpinned or remote script", failures)
    require('id="consent-checkbox" type="checkbox"' in html, "consent checkbox is missing", failures)
    require('id="start-button" type="button" disabled' in html, "start is not disabled by default", failures)
    require('id="calibration-stage"' in html, "full calibration stage is missing", failures)
    require("script-src 'self' 'unsafe-eval' 'wasm-unsafe-eval'" in html, "CSP does not allow local WASM runtime", failures)
    require("connect-src 'self'" in html, "CSP does not allow same-origin model assets", failures)
    require("https://" not in html and "http://" not in html, "HTML contains a remote runtime URL", failures)
    require("vision_bundle.js" in js and "vision_bundle.mjs" not in js, "MediaPipe module uses an HTTP-server-safe JavaScript extension", failures)

    required_tokens = [
        'navigator.gpu.requestAdapter({ powerPreference: "low-power" })',
        'ort.env.webgpu.powerPreference = "low-power"',
        'ort.env.webgpu.adapter = adapter',
        'executionProviders: ["webgpu"]',
        'delegate: "GPU"',
        'await initializeGpuPipeline()',
        'navigator.mediaDevices.getUserMedia',
        'track.stop()',
        'ui.camera.srcObject = null',
    ]
    for token in required_tokens:
        require(token in js, f"required runtime token is missing: {token}", failures)
    start_function = js[js.index("async function startRuntime()"):]
    require(start_function.index("await initializeGpuPipeline()") < start_function.index("await requestCameraAfterGpuGate()"), "camera gate is ordered after GPU initialization", failures)
    require('executionProviders: ["wasm"]' not in js and 'executionProviders: ["cpu"]' not in js, "runtime requests a CPU/WASM provider", failures)
    require('delegate: "CPU"' not in js, "runtime requests a CPU delegate", failures)
    require("getUserMedia" in js and "ui.consent.checked" in js, "camera path is not consent-gated", failures)
    require(not re.search(r"\b(fetch|XMLHttpRequest|sendBeacon|localStorage|sessionStorage)\b", js), "runtime contains persistence or network primitives", failures)

    required_files = [
        "vendor/ort.webgpu.min.js",
        "vendor/tasks-vision/vision_bundle.js",
        "vendor/tasks-vision/wasm/vision_wasm_internal.js",
        "vendor/tasks-vision/wasm/vision_wasm_internal.wasm",
        "vendor/tasks-vision/wasm/vision_wasm_nosimd_internal.js",
        "vendor/tasks-vision/wasm/vision_wasm_nosimd_internal.wasm",
        "models/face_landmarker.task",
        "models/tiny_gaze_encoder.onnx",
    ]
    for relative in required_files:
        path = HERE / relative
        require(path.is_file() and path.stat().st_size > 0, f"required local asset is missing: {relative}", failures)
    require((HERE / "models/face_landmarker.task").stat().st_size > 3_000_000, "official face model is unexpectedly small", failures)

    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CONTRACT_TESTS_VALID")
    print("camera_started_by_automation=False")
    print("external_network_used_by_adapter=False")
    print("onnx_execution_provider=webgpu")
    print("mediapipe_delegate=GPU")
    print("cpu_or_wasm_fallback=False")


if __name__ == "__main__":
    main()
