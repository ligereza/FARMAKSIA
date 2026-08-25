"""Static boundary for the GitHub-only pretrained gaze integration."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    failures: list[str] = []
    tracker = (ROOT / "experiments/033-vizz-python-headless-runtime/gpu_tracker.py").read_text(encoding="utf-8")
    runner = (ROOT / "experiments/033-vizz-python-headless-runtime/run_vizz.py").read_text(encoding="utf-8")
    downloader = (ROOT / "experiments/033-vizz-python-headless-runtime/download_models.py").read_text(encoding="utf-8")
    adapter = (ROOT / "experiments/033-vizz-python-headless-runtime/pretrained_gaze.py").read_text(encoding="utf-8")
    for token in ("pretrained_gaze_model", "create_cuda_session(pretrained_gaze_model)", "pretrained_gaze_deg"):
        if token not in tracker:
            failures.append(f"tracker lacks {token}")
    for token in ("--pretrained-gaze-model", "DEFAULT_PRETRAINED_GAZE_MODEL"):
        if token not in runner:
            failures.append(f"runtime lacks {token}")
    if "github.com/yakhyo/gaze-estimation/releases/download/weights/mobileone_s0_gaze.onnx" not in downloader:
        failures.append("download manifest is not pinned to the GitHub release")
    for token in ("CUDAExecutionProvider", "session.disable_cpu_ep_fallback"):
        if token not in tracker:
            failures.append(f"tracker lacks {token}")
    for token in ("MODEL_SOURCE", "decode_mobileone_angles"):
        if token not in adapter:
            failures.append(f"adapter lacks {token}")
    source_text = "\n".join((tracker, runner, downloader, adapter))
    if "huggingface" in source_text.lower() or "drive.google" in source_text.lower():
        failures.append("untrusted/non-GitHub model source leaked into runtime")
    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CONTRACT_TESTS_VALID")
    print("source_policy=github_only")
    print("cuda_only=True")
    print("screen_coordinates_claimed=False")


if __name__ == "__main__":
    main()
