"""Positive contract for real Excel state deltas without human-data claims."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    completed = subprocess.run(
        [sys.executable, str(HERE / "run_experiment.py"), "--mode", "scratch"],
        cwd=HERE.parents[1],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode:
        raise SystemExit(completed.stderr or "experiment 080 failed")
    payload = json.loads(completed.stdout)
    assert payload["status"] == "INPUT_NATIVE_DELTA_CORRELATION_VERIFIED"
    assert payload["validation_blockers"] == []
    assert payload["mode"] == "scratch"
    assert payload["human_input_claimed"] is False
    assert payload["excel"]["transition_kinds"] == ["create_entity", "modify_property", "revert"]
    assert payload["excel"]["delta_count"] == 3
    assert all(item["status"] == "unassociated_native_delta" for item in payload["excel"]["associations_without_input"])
    assert all(item["intent_claimed"] is False for item in payload["excel"]["associations_without_input"])
    assert payload["excel"]["raw_content_persisted"] is False
    print("FARMAXIA_080_INPUT_NATIVE_DELTA_CONTRACT_VALID")


if __name__ == "__main__":
    main()
