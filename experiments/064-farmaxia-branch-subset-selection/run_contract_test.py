"""Positive contract test for marginal branch selection."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    result = subprocess.run([sys.executable, str(HERE / "run_experiment.py")], cwd=HERE.parents[1], capture_output=True, text=True, encoding="utf-8", check=False)
    if result.returncode:
        raise SystemExit(result.stderr or "experiment 064 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "BRANCH_SUBSET_SELECTION_VERIFIED"
    assert payload["selection"]["selected_ids"] == ["plan-full", "plan-oracle", "plan-sequence", "plan-map"]
    assert payload["selection"]["total_display_cost"] == 5.6
    assert payload["selection"]["unselected_recoverable_ids"] == ["plan-analogy", "plan-focus", "plan-redundant"]
    assert payload["metrics"]["unselected_branches_recoverable"] is True
    assert payload["metrics"]["mmr_is_not_selection_authority"] is True
    print("FARMAXIA_064_BRANCH_SUBSET_SELECTION_CONTRACT_VALID")


if __name__ == "__main__":
    main()
