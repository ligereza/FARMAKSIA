"""Final kill tests for X-ANA-X independent novelty."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).parent
RUNNER = HERE / "run_experiment.py"


def main() -> None:
    completed = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=HERE.parents[1],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(f"KILL_TEST_INVALID: runner failed: {completed.stderr.strip()}")
    result = json.loads(completed.stdout)
    direct = result["direct_route"]
    analogy = result["analogy_route"]
    expected = {
        "valid": "valid",
        "hash-mismatch": "invalid",
        "unknown-reference": "invalid",
        "missing-file": "invalid",
    }
    for case, expected_status in expected.items():
        if direct[case]["status"] != expected_status or analogy[case]["predicted_status"] != expected_status:
            raise SystemExit(f"KILL_TEST_INVALID: custody boundary failed for {case}")
    comparison = result["comparison"]
    if not comparison["same_statuses"] or comparison["unique_analogy_decision"]:
        raise SystemExit("KILL_TEST_INVALID: analogy claimed a unique validator decision")
    if result["human_data"] or result["network_used"] or result["arbitrary_corpus"]:
        raise SystemExit("KILL_TEST_INVALID: prohibited data source crossed boundary")
    print("KILL_TESTS_VALID")
    print("hash_or_reference_failure=invalid")
    print("unique_analogy_decision=not_demonstrated")


if __name__ == "__main__":
    main()
