"""Kill tests for the VIZZ session envelope."""

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
    cases = {item["case"]: item for item in result["cases"]}
    if not cases["safe-default-off"]["valid"] or cases["safe-default-off"]["event_count"] != 0:
        raise SystemExit("KILL_TEST_INVALID: disabled default accepted non-empty capture")
    if not cases["opt-in-task-events"]["valid"] or cases["opt-in-task-events"]["event_count"] != 3:
        raise SystemExit("KILL_TEST_INVALID: valid task-event opt-in was rejected")
    if cases["reject-raw-text"]["valid"] or "forbidden payload field" not in cases["reject-raw-text"]["reason"]:
        raise SystemExit("KILL_TEST_INVALID: raw text crossed the session boundary")
    if result["human_data"] or result["devices_started"] or result["network_used"] or result["raw_capture"]:
        raise SystemExit("KILL_TEST_INVALID: runner acquired external or raw data")
    print("KILL_TESTS_VALID")
    print("default_capture=off")
    print("raw_payload=unavailable")


if __name__ == "__main__":
    main()
