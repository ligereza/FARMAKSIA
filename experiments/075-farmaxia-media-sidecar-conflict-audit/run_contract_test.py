"""Positive contract test for concurrent incompatible sidecars."""

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
        raise SystemExit(result.stderr or "experiment 075 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "CONFLICT"
    assert payload["blockers"] == []
    assert payload["candidate_count"] == 2
    assert [item["status"] for item in payload["candidates"]] == ["VERIFIED", "VERIFIED"]
    assert [item["composition_status"] for item in payload["candidates"]] == [
        "COMPOSED_COMPATIBLE",
        "COMPOSED_COMPATIBLE",
    ]
    assert payload["candidates"][0]["marker_presentation_frame"] == 12
    assert payload["candidates"][1]["marker_presentation_frame"] == 24
    assert payload["conflict"] == {
        "scope": {
            "asset_ref": "media-catalog:farmaksia:asset:interview-master",
            "asset_sha256": "sha256:synthetic-interview-master-v4",
            "source_version": 4,
            "timeline_ref": "media-catalog:farmaksia:timeline:cut-01",
            "timeline_id": "cut-01",
        },
        "candidate_ids": [
            "editorial-sidecar-cut-01-v4-a",
            "editorial-sidecar-cut-01-v4-b",
        ],
        "differing_claims": ["marker.marker_ref", "marker.source_frame"],
    }
    assert payload["selection"] is None
    assert payload["preserved_sidecar_ids"] == [
        "editorial-sidecar-cut-01-v4-a",
        "editorial-sidecar-cut-01-v4-b",
    ]
    assert payload["replay"]["all_canonical_orders_equal"] is True
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
    print("FARMAXIA_075_MEDIA_SIDECAR_CONFLICT_CONTRACT_VALID")


if __name__ == "__main__":
    main()
