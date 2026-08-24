"""Kill tests for the VIZZ-CODE-INE observability boundary."""

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
    if result["case_count"] != 7 or not result["all_expected_classifications"]:
        raise SystemExit("KILL_TEST_INVALID: expected classification matrix changed")
    by_id = {item["id"]: item for item in result["cases"]}
    if by_id["baseline"]["classification"] != "available":
        raise SystemExit("KILL_TEST_INVALID: baseline transition became unavailable")
    for case_id in ("missing_action_class", "non_monotonic_time", "duplicate_event_id"):
        if by_id[case_id]["classification"] != "rejected":
            raise SystemExit(f"KILL_TEST_INVALID: {case_id} crossed structural gate")
    for case_id in ("remove_anchor", "change_anchor_gain", "relabel_repetition"):
        if by_id[case_id]["classification"] != "ambiguous" or not by_id[case_id]["vizz_valid"]:
            raise SystemExit(f"KILL_TEST_INVALID: {case_id} was treated as a safe equivalent")
    if any(result[key] for key in ("human_data", "devices_started", "network_used", "raw_capture", "pharmacological_inference")):
        raise SystemExit("KILL_TEST_INVALID: prohibited state or capture flag was set")
    print("KILL_TESTS_VALID")
    print("baseline=c04_to_c07")
    print("structural_mutations=rejected")
    print("semantic_mutations=ambiguous")


if __name__ == "__main__":
    main()
