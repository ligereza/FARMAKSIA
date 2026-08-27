"""Positive contract test for progressive commitment."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    result = subprocess.run(
        [sys.executable, str(HERE / "run_experiment.py")],
        cwd=HERE.parents[1],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr or "experiment 061 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "PROGRESSIVE_COMMITMENT_VERIFIED"
    assert [item["maturity"] for item in payload["intent_history"]] == ["emergent", "emergent", "provisional", "provisional", "committed"]
    assert [item["outcome_verifiability"] for item in payload["intent_history"]] == ["open", "open", "constrained", "constrained", "verifiable"]
    assert payload["policies"][0]["allowed_operations"] == ["represent", "suggest", "compare", "branch"]
    assert "execute_if_authorized" in payload["policies"][-1]["allowed_operations"]
    assert payload["metrics"]["alternatives_offered_before_commitment"] == 4
    assert payload["metrics"]["premature_commitment_rate_fixture"] == 0.0
    assert payload["metrics"]["plans_not_selected_are_not_wrong"] is True
    plan_status = {plan["id"]: plan["context_status"] for plan in payload["representation_space"]}
    assert plan_status["plan-map"] == "selected_in_context"
    assert sum(status == "not_selected_in_context" for status in plan_status.values()) == 3
    assert payload["oracle"]["final_state"] == "verified"
    assert payload["execution_allowed"] is False
    assert payload["human_data"] is False
    assert payload["camera_used"] is False
    assert payload["network_used"] is False
    assert payload["arbitrary_code_executed"] is False
    print("CODEINE_061_PROGRESSIVE_COMMITMENT_CONTRACT_VALID")


if __name__ == "__main__":
    main()
