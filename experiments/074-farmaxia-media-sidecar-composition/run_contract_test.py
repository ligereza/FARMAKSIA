"""Positive contract test for the synthetic media sidecar composition."""

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
        raise SystemExit(result.stderr or "experiment 074 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "MEDIA_SIDECAR_COMPOSITION_VERIFIED"
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
    assert payload["ffprobe_before"]["status"] == "PARTIAL_UNKNOWN"
    assert payload["sidecar"] == {
        "status": "VERIFIED",
        "sidecar_id": "editorial-sidecar-cut-01-v4",
        "asset_ref": "media-catalog:farmaksia:asset:interview-master",
        "asset_sha256": "sha256:synthetic-interview-master-v4",
        "source_version": 4,
        "timeline_id": "cut-01",
        "provenance_refs": [
            "media-catalog:farmaksia:asset:interview-master",
            "media-catalog:farmaksia:timeline:cut-01",
            "media-catalog:farmaksia:marker:insight-01",
        ],
    }
    assert payload["composition"] == {
        "status": "COMPOSED_COMPATIBLE",
        "join_keys": {"asset_ref": True, "asset_sha256": True, "source_version": True},
        "marker_presentation_frame": 12,
        "marker_presentation_time": "1/2",
        "audio_video_sync_offset_frames": 0,
        "full_contract_equivalent": True,
    }
    assert payload["adapter"] == {
        "source": "media-representation-composition",
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
    print("FARMAXIA_074_MEDIA_SIDECAR_COMPOSITION_CONTRACT_VALID")


if __name__ == "__main__":
    main()
