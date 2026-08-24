"""Kill tests for the synthetic VIZZ gaze-quality gate."""

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
    if result["case_count"] != 11 or not result["all_expected_classifications"]:
        raise SystemExit("KILL_TEST_INVALID: gaze quality matrix changed")
    if result["evidence_status_counts"] != {"available": 1, "blocked": 3, "unavailable": 5, "rejected": 2}:
        raise SystemExit("KILL_TEST_INVALID: gaze quality counts changed")
    if (
        result["baseline_transition"]["last_significant_improvement"],
        result["baseline_transition"]["repetition_entry"],
    ) != ("c04", "c07"):
        raise SystemExit("KILL_TEST_INVALID: base transition changed")
    by_id = {case["id"]: case for case in result["cases"]}
    if not by_id["webgazer_consented_local_good"]["adaptation_allowed"]:
        raise SystemExit("KILL_TEST_INVALID: valid local profile did not pass")
    for case_id in (
        "webgazer_no_consent",
        "webgazer_remote_processing",
        "pupil_core_network_api",
        "webgazer_missing_calibration",
        "webgazer_calibration_error_high",
        "webgazer_latency_high",
        "webgazer_partial_coverage",
        "webgazer_unstable_head_pose",
        "unknown_candidate",
        "malformed_latency",
    ):
        if by_id[case_id]["adaptation_allowed"]:
            raise SystemExit(f"KILL_TEST_INVALID: blocked profile enabled adaptation: {case_id}")
    for key in ("human_data", "devices_started", "network_used", "raw_capture", "physiological_inference", "pharmacological_inference", "neurochemical_inference"):
        if result[key]:
            raise SystemExit(f"KILL_TEST_INVALID: prohibited flag {key}")
    print("KILL_TESTS_VALID")
    print("available=all_gate_conditions_pass")
    print("blocked=consent_or_transport_policy")
    print("unavailable=quality_or_coverage_failure")
    print("rejected=unknown_or_malformed_input")


if __name__ == "__main__":
    main()
