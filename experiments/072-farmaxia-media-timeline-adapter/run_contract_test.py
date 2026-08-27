"""Positive contract test for the synthetic media timeline adapter."""

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
        raise SystemExit(result.stderr or "experiment 072 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "MEDIA_TIMELINE_ADAPTER_VERIFIED"
    assert payload["blockers"] == []
    assert payload["input_envelope"] == {
        "status": "CLOUDEVENTS_ENVELOPE_VERIFIED",
        "raw_event_count": 4,
        "unique_event_count": 3,
        "duplicate_event_count": 1,
        "canonical_order": [
            "ev-asset-ingested",
            "ev-timeline-published",
            "ev-marker-declared",
        ],
        "original_envelopes_retained": True,
    }
    assert payload["replay"] == {
        "permutation_count": 3,
        "all_canonical_orders_equal": True,
        "canonical_order": [
            "ev-asset-ingested",
            "ev-timeline-published",
            "ev-marker-declared",
        ],
    }
    assert payload["adapter"]["source"] == "media-catalog"
    assert payload["adapter"]["destination"] == "media-review-player"
    assert payload["adapter"]["same_shared_cloudevents_kernel"] is True
    assert payload["timeline"] == {
        "timeline_id": "cut-01",
        "timebase": "24/1",
        "marker_id": "media-catalog:farmaksia:marker:insight-01",
        "marker_source_frame": 60,
        "marker_presentation_frame": 12,
        "marker_presentation_time": "1/2",
        "media_clock_separate_from_event_clock": True,
        "audio_video_sync_offset_frames": 0,
    }
    assert payload["decoder"] == {"codec": "h264", "status": "SUPPORTED"}
    assert payload["action"] == {
        "operation": "preview_media_timeline",
        "status": "DRY_RUN_ONLY",
        "requires_confirmation": True,
        "target_player_id": "farmaksia-review-player",
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
        "media_decoded": False,
    }
    print("FARMAXIA_072_MEDIA_TIMELINE_ADAPTER_CONTRACT_VALID")


if __name__ == "__main__":
    main()
