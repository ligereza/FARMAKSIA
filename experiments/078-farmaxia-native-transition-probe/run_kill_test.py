"""Adversarial tests for the isolated transition probe boundary."""

from __future__ import annotations

from copy import deepcopy
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_experiment import validate  # noqa: E402


def base() -> dict:
    return {
        "status": "NATIVE_TRANSITIONS_VERIFIED",
        "excel": {"status": "EXCEL_SCRATCH_TRANSITION_OBSERVED", "user_files_written": False},
        "blender": {"status": "BLENDER_SCRATCH_TRANSITION_OBSERVED", "user_files_written": False},
        "common_transitions": [
            {"kind": "create_entity"},
            {"kind": "select_entity"},
            {"kind": "modify_property"},
            {"kind": "revert"},
        ],
        "physical_input_injected": False,
        "safety": {
            "network_used": False,
            "screen_capture": False,
            "camera_capture": False,
            "mouse_or_keyboard_injected": False,
            "source_write_attempted": False,
        },
    }


def assert_blocked(payload: dict, reason: str) -> None:
    assert validate(payload), reason


def main() -> None:
    writes_user_file = base()
    writes_user_file["excel"]["user_files_written"] = True
    assert_blocked(writes_user_file, "user file write was accepted")

    physical_input = base()
    physical_input["physical_input_injected"] = True
    assert_blocked(physical_input, "physical input was accepted")

    network = base()
    network["safety"]["network_used"] = True
    assert_blocked(network, "network capability was accepted")

    wrong_kernel = deepcopy(base())
    wrong_kernel["common_transitions"][2]["kind"] = "click_button"
    assert_blocked(wrong_kernel, "button mapping replaced transition kernel")

    wrong_revert = deepcopy(base())
    wrong_revert["common_transitions"][-1]["kind"] = "leave_dirty"
    assert_blocked(wrong_revert, "non-reversible transition was accepted")

    print("FARMAXIA_078_NATIVE_TRANSITION_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
