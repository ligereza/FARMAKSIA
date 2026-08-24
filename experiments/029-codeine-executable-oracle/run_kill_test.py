"""Kill tests for the executable CODE-INE oracle and mutation matrix."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
RUNNER = HERE / "run_experiment.py"
ORACLE = HERE / "objective_oracle.py"


def main() -> None:
    if "objective_scores" in ORACLE.read_text(encoding="utf-8"):
        raise SystemExit("KILL_TEST_INVALID: executable oracle reads declared score")
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
    if result["case_count"] != 9 or not result["all_expected_classifications"]:
        raise SystemExit("KILL_TEST_INVALID: executable oracle matrix changed")
    if result["evidence_status_counts"] != {"verified": 3, "conflict": 2, "unavailable": 1, "rejected": 3}:
        raise SystemExit("KILL_TEST_INVALID: executable oracle counts changed")
    if (
        result["baseline_transition"]["last_significant_improvement"],
        result["baseline_transition"]["repetition_entry"],
    ) != ("c04", "c07"):
        raise SystemExit("KILL_TEST_INVALID: base transition changed")
    by_id = {case["id"]: case for case in result["cases"]}
    for case_id, expected in (
        ("reference_stable", "stable"),
        ("task_regressed_matches", "regressed"),
        ("task_recovered_matches", "recovered"),
    ):
        if by_id[case_id]["evidence_status"] != "verified" or by_id[case_id]["verified_drift"] != expected:
            raise SystemExit(f"KILL_TEST_INVALID: verified mutation outcome changed: {case_id}")
    for case_id in ("score_conflicts_with_regression", "score_conflicts_with_action"):
        if by_id[case_id]["evidence_status"] != "conflict" or by_id[case_id]["verified_drift"] is not None:
            raise SystemExit(f"KILL_TEST_INVALID: conflict crossed verified gate: {case_id}")
    if by_id["missing_task_event"]["evidence_status"] != "unavailable":
        raise SystemExit("KILL_TEST_INVALID: missing event crossed oracle gate")
    for case_id in ("anchor_rejected", "unknown_mutation_rejected", "invalid_score_rejected"):
        if by_id[case_id]["evidence_status"] != "rejected":
            raise SystemExit(f"KILL_TEST_INVALID: rejected input crossed gate: {case_id}")
    for key in ("human_data", "devices_started", "network_used", "raw_capture", "pharmacological_inference", "neurochemical_inference"):
        if result[key]:
            raise SystemExit(f"KILL_TEST_INVALID: prohibited flag {key}")
    print("KILL_TESTS_VALID")
    print("oracle=executable_specification_without_score_input")
    print("mutations=regression_recovery_action_anchor_and_schema")
    print("conflicts=never_verified")


if __name__ == "__main__":
    main()
