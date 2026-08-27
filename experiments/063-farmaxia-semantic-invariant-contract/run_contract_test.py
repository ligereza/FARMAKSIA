"""Positive test for query-relative semantic preservation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    result = subprocess.run([sys.executable, str(HERE / "run_experiment.py")], cwd=HERE.parents[1], capture_output=True, text=True, encoding="utf-8", check=False)
    if result.returncode:
        raise SystemExit(result.stderr or "experiment 063 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "SEMANTIC_INVARIANT_CONTRACT_VERIFIED"
    assert payload["metrics"]["view_count"] == 4
    assert payload["metrics"]["query_preservation_rate"] == 1.0
    assert payload["metrics"]["semantic_hallucination_rate"] == 0.0
    assert payload["metrics"]["unknown_escalation_rate"] == 0.0
    assert payload["metrics"]["provenance_completeness"] == 1.0
    assert payload["metrics"]["round_trip_loss"] is None
    assert payload["execution_allowed"] is False
    assert payload["external_execution"] is False
    assert payload["human_data"] is False
    print("FARMAXIA_063_SEMANTIC_INVARIANT_CONTRACT_VALID")


if __name__ == "__main__":
    main()
