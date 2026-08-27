"""Positive contract test for the read-only media representation bridge."""

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
        raise SystemExit(result.stderr or "experiment 073 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "MEDIA_REPRESENTATION_BRIDGE_VERIFIED"
    assert payload["blockers"] == []
    assert payload["input_envelope"]["raw_event_count"] == 4
    assert payload["input_envelope"]["unique_event_count"] == 3
    assert payload["replay"] == {
        "permutation_count": 3,
        "all_canonical_orders_equal": True,
        "canonical_order": [
            "ev-asset-ingested",
            "ev-timeline-published",
            "ev-marker-declared",
        ],
    }
    assert payload["representations"]["otio"]["status"] == "COMPATIBLE"
    assert payload["representations"]["otio"]["marker_presentation_frame"] == 12
    assert payload["representations"]["otio"]["marker_presentation_time"] == "1/2"
    assert payload["representations"]["ffprobe"]["status"] == "PARTIAL_UNKNOWN"
    assert payload["representations"]["ffprobe"]["missing_semantics"] == [
        "editorial_timeline",
        "clip_source_range",
        "marker_mapping",
    ]
    assert payload["comparison"] == {
        "same_asset_identity": True,
        "same_asset_hash": True,
        "same_codec": True,
        "same_timebase": True,
        "full_contract_equivalent": False,
        "ffprobe_sidecar_required": True,
        "safe_abstention": True,
    }
    assert payload["adapter"] == {
        "source": "media-representation",
        "destination": "farmaxia-media-contract",
        "same_shared_cloudevents_kernel": True,
        "read_only": True,
    }
    assert payload["safety"] == {
        "network_used": False,
        "external_execution": False,
        "human_data": False,
        "media_decoded": False,
        "source_write_attempted": False,
    }
    print("FARMAXIA_073_MEDIA_REPRESENTATION_BRIDGE_CONTRACT_VALID")


if __name__ == "__main__":
    main()
