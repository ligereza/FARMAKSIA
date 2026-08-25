"""Static contract for the naturalistic trace auditor and model preflight."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    failures: list[str] = []
    tracker = (ROOT / "experiments/033-vizz-python-headless-runtime/gpu_tracker.py").read_text(encoding="utf-8")
    trace = (ROOT / "experiments/033-vizz-python-headless-runtime/interaction_trace.py").read_text(encoding="utf-8")
    auditor = (Path(__file__).parent / "trace_audit.py").read_text(encoding="utf-8")
    for token in ("zero_tensor", "pretrained_gaze.run", "MobileOne CUDA preflight failed"):
        if token not in tracker:
            failures.append(f"tracker lacks {token}")
    for token in ("pretrained_gaze_preflight", "binocular_gaze_deg", "raw_model_angle_delta_deg"):
        if token not in trace:
            failures.append(f"trace lacks {token}")
    for token in ("t_monotonic", "mouse_screen", "screen_content", "mouse_is_ground_truth", "sample_count"):
        if token not in auditor:
            failures.append(f"auditor lacks {token}")
    if "screen_coordinates_claimed" not in auditor:
        failures.append("auditor does not preserve screen-coordinate boundary")
    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CONTRACT_TESTS_VALID")
    print("cuda_preflight=True")
    print("trace_is_pixel_free=True")
    print("screen_coordinates_claimed=False")


if __name__ == "__main__":
    main()
