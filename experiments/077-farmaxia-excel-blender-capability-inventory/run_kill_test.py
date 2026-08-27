"""Adversarial tests for the capability inventory safety and scope boundary."""

from __future__ import annotations

from copy import deepcopy
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_experiment import validate  # noqa: E402


def base() -> dict:
    return {
        "status": "EXCEL_BLENDER_CAPABILITY_INVENTORY_VERIFIED",
        "excel": {"status": "EXCEL_COM_OBSERVED", "mutations_performed": []},
        "blender": {"status": "BLENDER_PYTHON_API_OBSERVED"},
        "adapter_layers": {
            "surface": "pywinauto_uia",
            "excel_state": "local_excel_com_object_model",
            "blender_state": "official_blender_python_api",
            "shared_layer": "typed_state_transition_graph",
        },
        "actions_performed": [],
        "read_only": True,
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
    mutated_excel = base()
    mutated_excel["excel"]["mutations_performed"] = ["set_cell_value"]
    assert_blocked(mutated_excel, "Excel mutation was accepted")

    injected_input = base()
    injected_input["actions_performed"] = ["click"]
    assert_blocked(injected_input, "input injection was accepted")

    network = base()
    network["safety"]["network_used"] = True
    assert_blocked(network, "network capability was accepted")

    screenshot = base()
    screenshot["safety"]["screen_capture"] = True
    assert_blocked(screenshot, "screenshot capability was accepted")

    camera = base()
    camera["safety"]["camera_capture"] = True
    assert_blocked(camera, "camera capability was accepted")

    writable = base()
    writable["safety"]["source_write_attempted"] = True
    assert_blocked(writable, "write capability was accepted")

    wrong_surface = deepcopy(base())
    wrong_surface["adapter_layers"] = {"surface": "screenshot_coordinates"}
    assert_blocked(wrong_surface, "unvalidated surface was accepted")

    print("FARMAXIA_077_EXCEL_BLENDER_CAPABILITY_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
