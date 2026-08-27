"""Positive contract for real, isolated Excel/Blender transitions."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    completed = subprocess.run(
        [sys.executable, str(HERE / "run_experiment.py")],
        cwd=HERE.parents[1],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode:
        raise SystemExit(completed.stderr or "experiment 078 failed")
    payload = json.loads(completed.stdout)
    assert payload["status"] == "NATIVE_TRANSITIONS_VERIFIED"
    assert payload["validation_blockers"] == []
    assert payload["scratch_scope"] == "isolated_unsaved_application_sessions"
    assert payload["physical_input_injected"] is False
    assert payload["common_transitions"][-1]["kind"] == "revert"
    assert payload["excel"]["after_modify"]["computed_numeric_result"] == 5.0
    assert payload["excel"]["after_revert"]["nonempty_cells_in_target"] == 0
    assert payload["blender"]["after_select"]["active_is_scratch"] is True
    assert payload["blender"]["after_modify"]["location_x"] == 2.0
    assert payload["blender"]["after_revert"]["object_count"] == payload["blender"]["before"]["object_count"]
    assert payload["blender"]["after_revert"]["selected_count"] == payload["blender"]["before"]["selected_count"]
    assert payload["blender"]["after_revert"]["active_restored"] is True
    print("FARMAXIA_078_NATIVE_TRANSITION_CONTRACT_VALID")


if __name__ == "__main__":
    main()
