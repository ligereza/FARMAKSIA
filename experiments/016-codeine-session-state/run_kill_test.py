"""Kill tests for the minimal CODE-INE state transition."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("codeine_runner", HERE / "run_experiment.py")
if SPEC is None or SPEC.loader is None:
    raise SystemExit("KILL_TEST_INVALID: could not load runner")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def main() -> None:
    document = json.loads((HERE / "trace.json").read_text(encoding="utf-8"))
    events = document["events"]
    baseline = RUNNER.derive_transition(events)
    activity_only = RUNNER.activity_only_view(events)
    if baseline["repetition_entry"] != "c07":
        raise SystemExit("KILL_TEST_INVALID: baseline repetition entry changed")
    if not activity_only["low_gain_tail_proxy"] or activity_only["repetition_entry"] != "unavailable_without_action_class":
        raise SystemExit("KILL_TEST_INVALID: aggregate view recovered exact repetition")
    without_action = [{key: value for key, value in event.items() if key != "action_class"} for event in events]
    if any("action_class" in event for event in without_action):
        raise SystemExit("KILL_TEST_INVALID: action field survived removal adversary")
    if baseline["drift"] != "unavailable_without_objective_signal":
        raise SystemExit("KILL_TEST_INVALID: detector inferred drift without an objective signal")
    result = json.loads(__import__("subprocess").check_output([__import__("sys").executable, str(HERE / "run_experiment.py")], text=True))
    if result["human_data"] or result["pharmacological_inference"]:
        raise SystemExit("KILL_TEST_INVALID: runner made human or pharmacological claim")
    print("KILL_TESTS_VALID")
    print("exact_repetition_without_action_class=unavailable")
    print("drift_without_objective_signal=unavailable")


if __name__ == "__main__":
    main()
