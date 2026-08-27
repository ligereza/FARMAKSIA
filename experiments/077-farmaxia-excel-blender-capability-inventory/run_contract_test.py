"""Positive contract for the real Excel/Blender capability inventory."""

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
        raise SystemExit(completed.stderr or "experiment 077 failed")
    payload = json.loads(completed.stdout)
    assert payload["status"] == "EXCEL_BLENDER_CAPABILITY_INVENTORY_VERIFIED"
    assert payload["validation_blockers"] == []
    assert payload["excel"]["status"] == "EXCEL_COM_OBSERVED"
    assert payload["blender"]["status"] == "BLENDER_PYTHON_API_OBSERVED"
    assert payload["excel"]["mutations_performed"] == []
    assert payload["actions_performed"] == []
    assert payload["read_only"] is True
    assert payload["adapter_layers"] == {
        "surface": "pywinauto_uia",
        "excel_state": "local_excel_com_object_model",
        "blender_state": "official_blender_python_api",
        "shared_layer": "typed_state_transition_graph",
    }
    print("FARMAXIA_077_EXCEL_BLENDER_CAPABILITY_CONTRACT_VALID")


if __name__ == "__main__":
    main()
