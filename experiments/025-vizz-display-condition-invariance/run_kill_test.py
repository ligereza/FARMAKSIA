"""Kill tests for VIZZ display-condition invariance."""

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
        raise SystemExit("KILL_TEST_INVALID: display profile matrix changed")
    if result["classification_counts"] != {"available": 4, "unavailable": 2}:
        raise SystemExit("KILL_TEST_INVALID: display availability counts changed")
    if not result["full_display_invariant"] or len(result["full_display_fingerprints"]) != 1:
        raise SystemExit("KILL_TEST_INVALID: display condition mutated full-session semantics")
    by_id = {case["id"]: case for case in result["cases"]}
    if not by_id["night_focus_complete"]["decision_available"] or by_id["night_focus_complete"]["context_before_anchor_preserved"]:
        raise SystemExit("KILL_TEST_INVALID: focus residue was hidden or query was lost")
    for case_id in ("night_focus_missing_anchor", "night_field"):
        case = by_id[case_id]
        if case["classification"] != "unavailable" or case["decision_available"] or case["transition"] is not None:
            raise SystemExit(f"KILL_TEST_INVALID: {case_id} produced a partial query")
    if result["physiological_inference"] or result["pharmacological_inference"] or result["optical_prescription_applied"]:
        raise SystemExit("KILL_TEST_INVALID: display profile made an out-of-scope claim")
    print("KILL_TESTS_VALID")
    print("full_display_semantics=invariant")
    print("focus_context_residue=explicit")
    print("missing_anchor_or_field=unavailable")


if __name__ == "__main__":
    main()
