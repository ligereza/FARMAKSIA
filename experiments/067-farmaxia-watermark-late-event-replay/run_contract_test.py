"""Positive contract test for watermark and late-event replay."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    result = subprocess.run([sys.executable, str(HERE / "run_experiment.py")], cwd=HERE.parents[1], capture_output=True, text=True, encoding="utf-8", check=False)
    if result.returncode:
        raise SystemExit(result.stderr or "experiment 067 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "WATERMARK_LATE_REPLAY_VERIFIED"
    assert payload["blockers"] == []
    assert payload["stream"]["raw_message_count"] == 11
    assert payload["stream"]["watermark_count"] == 3
    assert payload["stream"]["raw_event_count"] == 8
    assert payload["stream"]["unique_event_count"] == 7
    assert payload["stream"]["duplicate_event_count"] == 1
    assert payload["stream"]["late_event_ids"] == ["ev-deploy-green", "ev-pipeline-failed-correction"]
    assert payload["stream"]["final_watermark"] == 300
    assert payload["stream"]["watermark_monotone"] is True
    assert payload["replay"]["all_batch_projection_signatures_equal"] is True
    assert payload["replay"]["final_projection_equals_batch_replay"] is True
    assert payload["causal"]["pending_resolved_ids"] == ["ev-review-child"]
    assert payload["causal"]["unresolved_ids"] == ["ev-approval-observed"]
    projection = {(item["entity_ref"], item["field"]): item for item in payload["replay"]["projection"]}
    assert projection[("gitlab:proj-alpha:pipeline:pipe-3", "status")]["value"] == "failed"
    assert projection[("gitlab:proj-alpha:deployment:deploy-9", "status")]["status"] == "CONFLICT"
    assert projection[("gitlab:proj-alpha:merge_request:mr-7:approval", "approved")]["status"] == "UNKNOWN"
    assert projection[("gitlab:proj-alpha:review_note:note-1", "state")]["value"] == "ready"
    assert "ev-pipeline-success" in payload["replay"]["superseded_event_ids"]
    snapshots = {snapshot["message_id"]: snapshot for snapshot in payload["stream"]["snapshots"]}
    assert snapshots["wm-300"]["pipeline_status"] == "success"
    assert snapshots["ev-pipeline-failed-correction"]["pipeline_status"] == "failed"
    assert payload["safety"] == {"network_used": False, "external_execution": False, "human_data": False, "camera_used": False, "source_write_attempted": False}
    print("FARMAXIA_067_WATERMARK_LATE_REPLAY_CONTRACT_VALID")


if __name__ == "__main__":
    main()
