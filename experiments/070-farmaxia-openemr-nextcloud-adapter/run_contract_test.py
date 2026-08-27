"""Positive contract test for the synthetic institutional document adapter."""

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
        raise SystemExit(result.stderr or "experiment 070 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "DOCUMENTAL_CLOUDEVENTS_ADAPTER_VERIFIED"
    assert payload["blockers"] == []
    assert payload["input_envelope"] == {
        "status": "CLOUDEVENTS_ENVELOPE_VERIFIED",
        "raw_event_count": 4,
        "unique_event_count": 3,
        "duplicate_event_count": 1,
        "canonical_order": [
            "ev-patient-context",
            "ev-care-plan-published",
            "ev-document-ready",
        ],
        "original_envelopes_retained": True,
    }
    assert payload["adapter"]["source"] == "openemr"
    assert payload["adapter"]["destination"] == "nextcloud"
    assert payload["adapter"]["same_shared_cloudevents_kernel"] is True
    assert payload["adapter"]["source_refs"] == [
        "openemr:synthetic-clinic:care_plan:plan-demo-001",
        "openemr:synthetic-clinic:document:doc-demo-001",
    ]
    assert payload["action"] == {
        "operation": "create_document_index_entry",
        "status": "DRY_RUN_ONLY",
        "requires_confirmation": True,
        "target_folder_id": "folder-education",
    }
    assert payload["independent_verification"]["not_verified_from_representation"] is True
    assert all(
        check["status"] == "VERIFIED"
        for check in payload["independent_verification"]["checks"]
    )
    assert payload["safety"] == {
        "network_used": False,
        "external_execution": False,
        "human_data": False,
        "camera_used": False,
        "source_write_attempted": False,
    }
    print("FARMAXIA_070_DOCUMENTAL_ADAPTER_CONTRACT_VALID")


if __name__ == "__main__":
    main()
