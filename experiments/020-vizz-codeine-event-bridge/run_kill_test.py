"""Kill tests for the VIZZ to CODE-INE event bridge."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("bridge_runner", HERE / "run_experiment.py")
if SPEC is None or SPEC.loader is None:
    raise SystemExit("KILL_TEST_INVALID: could not load bridge runner")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def main() -> None:
    baseline = RUNNER.run_bridge()
    if baseline["transition"]["repetition_entry"] is not None:
        raise SystemExit("KILL_TEST_INVALID: short trace invented repetition")
    session = RUNNER.load_opt_in_session()
    damaged = copy.deepcopy(session)
    damaged["events"][1]["payload"].pop("action_class")
    try:
        RUNNER.normalize_events(damaged)
    except ValueError as exc:
        if "action_class" not in str(exc):
            raise SystemExit("KILL_TEST_INVALID: wrong missing-field boundary") from exc
    else:
        raise SystemExit("KILL_TEST_INVALID: bridge accepted missing action class")
    cases = json.loads(RUNNER.VIZZ_CASES.read_text(encoding="utf-8"))
    safe_default = next(case["session"] for case in cases["cases"] if case["id"] == "safe-default-off")
    if RUNNER.normalize_events(safe_default)[0] != []:
        raise SystemExit("KILL_TEST_INVALID: disabled capture produced events")
    if baseline["human_data"] or baseline["devices_started"] or baseline["network_used"] or baseline["raw_capture"]:
        raise SystemExit("KILL_TEST_INVALID: bridge acquired prohibited data")
    print("KILL_TESTS_VALID")
    print("missing_action_class=unavailable")
    print("short_trace_repetition=unavailable")


if __name__ == "__main__":
    main()
