"""Kill tests for CODE-INE objective-signal derivation."""

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
    if result["case_count"] != 6 or not result["all_expected_classifications"]:
        raise SystemExit("KILL_TEST_INVALID: objective signal matrix changed")
    if result["classification_counts"] != {"available": 3, "unavailable": 2, "rejected": 1}:
        raise SystemExit("KILL_TEST_INVALID: objective classification counts changed")
    if (
        result["baseline_transition"]["last_significant_improvement"],
        result["baseline_transition"]["repetition_entry"],
    ) != ("c04", "c07"):
        raise SystemExit("KILL_TEST_INVALID: base CODE-INE transition changed")
    by_id = {case["id"]: case for case in result["cases"]}
    for case_id, expected in (("stable", "stable"), ("regressed", "regressed"), ("recovered", "recovered")):
        if by_id[case_id]["objective_state"]["drift"] != expected:
            raise SystemExit(f"KILL_TEST_INVALID: {case_id} drift status changed")
    for case_id in ("no_objective", "missing_tail_score"):
        if by_id[case_id]["classification"] != "unavailable" or by_id[case_id]["objective_state"] is not None:
            raise SystemExit(f"KILL_TEST_INVALID: {case_id} invented drift")
    if by_id["out_of_range"]["classification"] != "rejected":
        raise SystemExit("KILL_TEST_INVALID: invalid objective score crossed the gate")
    for case in result["cases"]:
        if case["human_data"] or case["pharmacological_inference"]:
            raise SystemExit("KILL_TEST_INVALID: prohibited state claim")
    if result["neurochemical_inference"]:
        raise SystemExit("KILL_TEST_INVALID: neurochemical claim")
    print("KILL_TESTS_VALID")
    print("base_transition=c04_to_c07")
    print("missing_objective=unavailable")
    print("invalid_objective=rejected")
    print("drift=declared_objective_only")


if __name__ == "__main__":
    main()
