"""Kill tests for declared versus verified CODE-INE objective evidence."""

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
        raise SystemExit("KILL_TEST_INVALID: oracle evidence matrix changed")
    if result["evidence_status_counts"] != {"verified": 3, "declared_only": 1, "conflict": 1, "unavailable": 1, "rejected": 1}:
        raise SystemExit("KILL_TEST_INVALID: oracle evidence counts changed")
    if (
        result["baseline_transition"]["last_significant_improvement"],
        result["baseline_transition"]["repetition_entry"],
    ) != ("c04", "c07"):
        raise SystemExit("KILL_TEST_INVALID: base transition changed")
    by_id = {case["id"]: case for case in result["cases"]}
    for case_id, expected in (("aligned_stable", "stable"), ("aligned_regressed", "regressed"), ("aligned_recovered", "recovered")):
        if by_id[case_id]["evidence_status"] != "verified" or by_id[case_id]["verified_drift"] != expected:
            raise SystemExit(f"KILL_TEST_INVALID: {case_id} was not independently verified")
    if by_id["declared_only"]["evidence_status"] != "declared_only" or by_id["declared_only"]["verified_drift"] is not None:
        raise SystemExit("KILL_TEST_INVALID: score without oracle became verified")
    if by_id["conflict"]["evidence_status"] != "conflict" or by_id["conflict"]["verified_drift"] is not None:
        raise SystemExit("KILL_TEST_INVALID: conflicting oracle produced verified drift")
    if by_id["incomplete_oracle"]["evidence_status"] != "unavailable":
        raise SystemExit("KILL_TEST_INVALID: incomplete oracle crossed gate")
    if by_id["malformed_oracle"]["evidence_status"] != "rejected":
        raise SystemExit("KILL_TEST_INVALID: malformed oracle crossed gate")
    for case in result["cases"]:
        if case["human_data"] or case["pharmacological_inference"] or case["neurochemical_inference"]:
            raise SystemExit("KILL_TEST_INVALID: prohibited state claim")
    print("KILL_TESTS_VALID")
    print("verified=score_and_oracle_agree")
    print("declared_only=no_oracle")
    print("conflict=oracle_disagrees")
    print("incomplete_or_malformed=blocked")


if __name__ == "__main__":
    main()
