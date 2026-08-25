"""Static contract for the CUDA-only pretrained-model probe."""

from __future__ import annotations

from pathlib import Path


HERE = Path(__file__).parent


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> None:
    failures: list[str] = []
    probe = (HERE / "run_probe.py").read_text(encoding="utf-8")
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    require('"CUDAExecutionProvider"' in probe, "probe does not require CUDA", failures)
    require('"session.disable_cpu_ep_fallback"' in probe, "CPU fallback kill switch is missing", failures)
    require('providers=["CUDAExecutionProvider"]' in probe, "probe requests a non-CUDA provider", failures)
    require('"camera_opened": False' in probe, "probe does not declare camera boundary", failures)
    require('"raw_frames_persisted": False' in probe, "probe may persist raw frames", failures)
    require("screen_coordinates_claimed" in probe, "probe does not separate gaze from screen geometry", failures)
    require("researched-not-installed" in probe, "candidate catalog is missing explicit install status", failures)
    require("run_probe.py" in readme and "CUDA" in readme and "no abre la cámara" in readme, "probe boundary is undocumented", failures)
    require("--output" in readme and ".vizz-pretrained-probe.json" in readme, "probe output is undocumented", failures)
    require("VideoCapture" not in probe and "getUserMedia" not in probe, "probe contains a camera capture path", failures)
    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CONTRACT_TESTS_VALID")
    print("cuda_only=True")
    print("camera_opened=False")
    print("raw_frames_persisted=False")
    print("screen_coordinates_claimed=False")


if __name__ == "__main__":
    main()
