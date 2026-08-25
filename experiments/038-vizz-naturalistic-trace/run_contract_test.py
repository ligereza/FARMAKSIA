"""Static contract for optional naturalistic trace recording."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    failures: list[str] = []
    trace = (ROOT / "experiments/033-vizz-python-headless-runtime/interaction_trace.py").read_text(encoding="utf-8")
    runner = (ROOT / "experiments/033-vizz-python-headless-runtime/run_vizz.py").read_text(encoding="utf-8")
    experiment = (Path(__file__).parent / "run_experiment.py").read_text(encoding="utf-8")
    for token in ("GetCursorPos", "t_monotonic", "mouse_screen", "mouse_is_ground_truth", "raw_video", "screen_content"):
        if token not in trace:
            failures.append(f"trace lacks {token}")
    for token in ("--trace", "--trace-hz", "InteractionTrace", "read_pointer_position"):
        if token not in runner:
            failures.append(f"runtime lacks {token}")
    if "NATURALISTIC_TRACE_VALID" not in experiment or "TemporaryDirectory" not in experiment:
        failures.append("synthetic trace test is missing")
    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CONTRACT_TESTS_VALID")
    print("trace_opt_in=True")
    print("mouse_is_ground_truth=False")
    print("raw_video=False")
    print("screen_content=False")


if __name__ == "__main__":
    main()
