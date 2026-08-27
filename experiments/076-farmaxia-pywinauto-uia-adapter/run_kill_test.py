"""Adversarial tests for the real UIA adapter's read-only boundary."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_experiment import validate_observation  # noqa: E402


def base_observation() -> dict:
    return {
        "status": "PYWINAUTO_UIA_PROBE_VERIFIED",
        "tool_available": True,
        "tool_version": "0.6.9",
        "backend": "uia",
        "observation": {"top_level_window_count": 1},
        "title_texts_emitted": False,
        "actions_performed": [],
        "read_only": True,
        "safety": {
            "screen_capture": False,
            "camera_capture": False,
            "network_used": False,
            "mouse_or_keyboard_injected": False,
            "source_write_attempted": False,
        },
    }


def assert_blocked(observation: dict, reason: str) -> None:
    assert validate_observation(observation), reason


def main() -> None:
    raw_title = base_observation()
    raw_title["title_texts_emitted"] = True
    assert_blocked(raw_title, "raw window titles were emitted")

    injected_input = base_observation()
    injected_input["actions_performed"] = ["click"]
    assert_blocked(injected_input, "input injection was accepted")

    writable = base_observation()
    writable["read_only"] = False
    assert_blocked(writable, "write policy was accepted")

    screenshot = base_observation()
    screenshot["safety"]["screen_capture"] = True
    assert_blocked(screenshot, "screen capture was accepted")

    network = base_observation()
    network["safety"]["network_used"] = True
    assert_blocked(network, "network use was accepted")

    invalid_backend = base_observation()
    invalid_backend["backend"] = "win32"
    assert_blocked(invalid_backend, "non-UIA backend was accepted")

    invalid_count = deepcopy(base_observation())
    invalid_count["observation"]["top_level_window_count"] = -1
    assert_blocked(invalid_count, "invalid window count was accepted")

    print("FARMAXIA_076_PYWINAUTO_UIA_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
