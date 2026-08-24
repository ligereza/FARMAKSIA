"""Kill tests for synthetic VIZZ latency and coverage."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
RUNNER = HERE / "run_experiment.py"


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
    if result["case_count"] != 5 or not result["all_expected_classifications"]:
        raise SystemExit("KILL_TEST_INVALID: latency classification matrix changed")
    if result["classification_counts"] != {"available": 2, "unavailable": 3}:
        raise SystemExit("KILL_TEST_INVALID: unexpected availability counts")
    if (
        result["baseline_transition"]["last_significant_improvement"],
        result["baseline_transition"]["repetition_entry"],
    ) != ("c04", "c07"):
        raise SystemExit("KILL_TEST_INVALID: baseline transition changed")
    for case in result["cases"]:
        if case["classification"] == "unavailable":
            if not case["hidden_event_ids"] or case["decision_available"] or case["transition"] is not None:
                raise SystemExit("KILL_TEST_INVALID: incomplete coverage produced a transition claim")
        elif case["classification"] == "available" and not case["complete_coverage"]:
            raise SystemExit("KILL_TEST_INVALID: available case lacks complete coverage")
    for key in ("human_data", "devices_started", "network_used", "raw_capture", "pharmacological_inference"):
        if result[key]:
            raise SystemExit(f"KILL_TEST_INVALID: prohibited flag {key}")
    print("KILL_TESTS_VALID")
    print("complete_coverage=required")
    print("partial_coverage=unavailable")
    print("baseline=c04_to_c07")


if __name__ == "__main__":
    main()
