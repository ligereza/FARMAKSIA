"""Positive contract test for the synthetic CODE-INE patch adapter."""

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
        raise SystemExit(result.stderr or "experiment 071 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "CODEINE_CLOUDEVENTS_ADAPTER_VERIFIED"
    assert payload["blockers"] == []
    assert payload["input_envelope"] == {
        "status": "CLOUDEVENTS_ENVELOPE_VERIFIED",
        "raw_event_count": 4,
        "unique_event_count": 3,
        "duplicate_event_count": 1,
        "canonical_order": ["ev-change-opened", "ev-check-passed", "ev-file-patch"],
        "original_envelopes_retained": True,
    }
    assert payload["replay"] == {
        "permutation_count": 3,
        "all_canonical_signatures_equal": True,
        "canonical_order": ["ev-change-opened", "ev-check-passed", "ev-file-patch"],
    }
    assert payload["adapter"]["source"] == "code-host"
    assert payload["adapter"]["destination"] == "editor-workspace"
    assert payload["adapter"]["same_shared_cloudevents_kernel"] is True
    assert payload["patch"] == {
        "patch_id": "patch-renderer-v17",
        "target_ref": "code-host:farmaksia-core:file:renderer.py",
        "base_sha256": "sha256:baseline-renderer-v16",
        "code_execution": False,
    }
    assert payload["action"] == {
        "operation": "preview_code_patch",
        "status": "DRY_RUN_ONLY",
        "requires_confirmation": True,
        "target_workspace_id": "farmaksia-workspace",
    }
    assert payload["independent_verification"]["not_verified_from_representation"] is True
    assert all(
        item["status"] == "VERIFIED"
        for item in payload["independent_verification"]["checks"]
    )
    assert payload["safety"] == {
        "network_used": False,
        "external_execution": False,
        "human_data": False,
        "camera_used": False,
        "source_write_attempted": False,
        "arbitrary_code_executed": False,
    }
    print("FARMAXIA_071_CODEINE_ADAPTER_CONTRACT_VALID")


if __name__ == "__main__":
    main()
