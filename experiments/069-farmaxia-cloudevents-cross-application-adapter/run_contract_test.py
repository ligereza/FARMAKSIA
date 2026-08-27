"""Positive contract test for the CloudEvents cross-application adapter."""

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
        raise SystemExit(result.stderr or "experiment 069 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "CROSS_APPLICATION_CLOUDEVENTS_ADAPTER_VERIFIED"
    assert payload["blockers"] == []
    assert payload["input_envelope"] == {
        "status": "CLOUDEVENTS_ENVELOPE_VERIFIED",
        "raw_event_count": 4,
        "unique_event_count": 3,
        "duplicate_event_count": 1,
        "canonical_order": ["ev-mr-open", "ev-pipeline-fail", "ev-mr-comment"],
        "original_envelopes_retained": True,
    }
    assert payload["adapter"]["destination"] == "mattermost"
    assert payload["adapter"]["normalized_event_ids"] == [
        "ev-mr-open",
        "ev-pipeline-fail",
        "ev-mr-comment",
    ]
    assert payload["adapter"]["source_identity_preserved"] is True
    assert payload["adapter"]["provenance_preserved"] is True
    assert payload["bridge"]["status"] == "CROSS_APPLICATION_EVIDENCE_VERIFIED"
    assert payload["bridge"]["action_status"] == "DRY_RUN_ONLY"
    assert all(
        check["status"] == "VERIFIED"
        for check in payload["bridge"]["verification"]["checks"]
    )
    assert payload["safety"] == {
        "network_used": False,
        "external_execution": False,
        "human_data": False,
        "camera_used": False,
        "source_write_attempted": False,
    }
    print("FARMAXIA_069_CLOUDEVENTS_ADAPTER_CONTRACT_VALID")


if __name__ == "__main__":
    main()
