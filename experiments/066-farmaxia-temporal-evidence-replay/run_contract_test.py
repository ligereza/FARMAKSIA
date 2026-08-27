"""Positive contract test for temporal evidence replay."""

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
    if result.returncode:
        raise SystemExit(result.stderr or "experiment 066 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "TEMPORAL_REPLAY_VERIFIED"
    assert payload["blockers"] == []
    assert payload["ledger"]["raw_event_count"] == 9
    assert payload["ledger"]["unique_event_count"] == 8
    assert payload["ledger"]["duplicate_event_count"] == 1
    assert payload["ledger"]["out_of_order_input"] is True
    assert payload["ledger"]["retractions_preserve_history"] is True
    assert payload["replay"]["permutation_count"] == 3
    assert payload["replay"]["all_projection_signatures_equal"] is True
    actual = {(item["entity_ref"], item["field"]): item for item in payload["replay"]["projection"]}
    assert actual[("gitlab:proj-alpha:merge_request:mr-7", "state")]["value"] == "merged"
    assert actual[("gitlab:proj-alpha:pipeline:pipe-3", "status")]["value"] == "success"
    assert actual[("gitlab:proj-alpha:deployment:deploy-9", "status")]["status"] == "CONFLICT"
    assert actual[("gitlab:proj-alpha:deployment:deploy-9", "status")]["value"] is None
    assert payload["replay"]["unknowns"][0]["status"] == "UNKNOWN"
    assert "ev-pipeline-failed" in payload["replay"]["revoked_event_ids"]
    assert payload["safety"] == {
        "network_used": False,
        "external_execution": False,
        "human_data": False,
        "camera_used": False,
        "source_write_attempted": False,
    }
    print("FARMAXIA_066_TEMPORAL_REPLAY_CONTRACT_VALID")


if __name__ == "__main__":
    main()
