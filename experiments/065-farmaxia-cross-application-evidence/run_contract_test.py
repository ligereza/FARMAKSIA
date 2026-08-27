"""Positive contract test for the synthetic cross-application evidence bridge."""

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
        raise SystemExit(result.stderr or "experiment 065 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "CROSS_APPLICATION_EVIDENCE_VERIFIED"
    assert payload["blockers"] == []
    assert payload["ingestion"]["raw_event_count"] == 4
    assert payload["ingestion"]["unique_event_count"] == 3
    assert payload["ingestion"]["duplicate_event_count"] == 1
    assert payload["ingestion"]["out_of_order_input"] is True
    assert payload["ingestion"]["canonical_order"] == ["ev-mr-open", "ev-pipeline-fail", "ev-mr-comment"]
    assert payload["semantic_model"]["identity_is_project_qualified"] is True
    assert payload["semantic_model"]["representation"]["source_refs"]
    assert payload["action_proposal"]["status"] == "DRY_RUN_ONLY"
    assert payload["action_proposal"]["dry_run"] is True
    assert payload["independent_verification"]["not_verified_from_representation"] is True
    assert all(check["status"] == "VERIFIED" for check in payload["independent_verification"]["checks"])
    assert payload["safety"] == {
        "network_used": False,
        "external_execution": False,
        "human_data": False,
        "camera_used": False,
        "source_write_attempted": False,
    }
    print("FARMAXIA_065_CROSS_APPLICATION_EVIDENCE_CONTRACT_VALID")


if __name__ == "__main__":
    main()
