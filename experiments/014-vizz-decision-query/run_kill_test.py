"""Kill tests for the VIZZ decision-query contract."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = Path(__file__).with_name("run_experiment.py")


def main() -> None:
    completed = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(f"KILL_TEST_INVALID: runner failed: {completed.stderr.strip()}")
    result = json.loads(completed.stdout)
    by_name = {item["representation"]: item for item in result["representations"]}
    by_window = {item["representation"]: item for item in result["focus_window_sensitivity"]}

    if not by_name["text"]["global_tail_available"]:
        raise SystemExit("KILL_TEST_INVALID: complete text lost the global query")
    if not by_name["timeline"]["global_tail_available"]:
        raise SystemExit("KILL_TEST_INVALID: complete timeline lost the global query")
    if by_name["field"]["global_tail_available"]:
        raise SystemExit("KILL_TEST_INVALID: aggregate field recovered a global sequence")
    if not by_name["field"]["proxy_repetition_signal"]:
        raise SystemExit("KILL_TEST_INVALID: aggregate proxy signal disappeared")
    if by_window["focus:4m"]["global_tail_available"] or by_window["focus:8m"]["global_tail_available"]:
        raise SystemExit("KILL_TEST_INVALID: narrow focus claimed a hidden global tail")
    if not by_window["focus:16m"]["global_tail_available"]:
        raise SystemExit("KILL_TEST_INVALID: sufficient focus window lost the query")
    print("KILL_TESTS_VALID")
    print("narrow_focus_global_query=unavailable")
    print("aggregate_global_query=unavailable")


if __name__ == "__main__":
    main()
