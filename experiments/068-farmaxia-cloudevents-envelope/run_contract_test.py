"""Positive contract test for the local CloudEvents envelope."""

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
        raise SystemExit(result.stderr or "experiment 068 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "CLOUDEVENTS_ENVELOPE_VERIFIED"
    assert payload["blockers"] == []
    assert payload["envelope"]["specversion"] == "1.0"
    assert payload["envelope"]["raw_event_count"] == 4
    assert payload["envelope"]["unique_event_count"] == 3
    assert payload["envelope"]["duplicate_event_count"] == 1
    assert payload["envelope"]["duplicate_conflict_ids"] == []
    assert payload["envelope"]["identity_rule"] == "source_plus_id"
    assert payload["envelope"]["out_of_order_input"] is True
    assert payload["envelope"]["canonical_order"] == [
        "ev-mr-open",
        "ev-pipeline-fail",
        "ev-mr-comment",
    ]
    assert payload["envelope"]["original_envelopes_retained"] is True
    assert payload["compatibility"] == {
        "maps_to_farmaxia_event_contract": True,
        "source_identity_preserved": True,
        "provenance_extensions_preserved": True,
    }
    assert payload["safety"] == {
        "network_used": False,
        "external_execution": False,
        "human_data": False,
        "camera_used": False,
        "source_write_attempted": False,
    }
    print("FARMAXIA_068_CLOUDEVENTS_ENVELOPE_CONTRACT_VALID")


if __name__ == "__main__":
    main()
