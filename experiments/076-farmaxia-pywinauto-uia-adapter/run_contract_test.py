"""Positive contract test using the installed pywinauto package on Windows."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    result = subprocess.run(
        [sys.executable, str(HERE / "run_experiment.py"), "--inspect-controls"],
        cwd=HERE.parents[1],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode:
        raise SystemExit(result.stderr or "experiment 076 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "PYWINAUTO_UIA_PROBE_VERIFIED"
    assert payload["validation_blockers"] == []
    assert payload["tool_available"] is True
    assert payload["tool_version"] == "0.6.9"
    assert payload["backend"] == "uia"
    assert payload["observation"]["top_level_window_count"] > 0
    assert payload["inspect_controls"] is True
    assert payload["observation"]["descendant_control_count"] >= 0
    assert payload["title_texts_emitted"] is False
    assert payload["actions_performed"] == []
    assert payload["read_only"] is True
    assert payload["safety"] == {
        "screen_capture": False,
        "camera_capture": False,
        "network_used": False,
        "mouse_or_keyboard_injected": False,
        "source_write_attempted": False,
    }
    print("FARMAXIA_076_PYWINAUTO_UIA_CONTRACT_VALID")


if __name__ == "__main__":
    main()
