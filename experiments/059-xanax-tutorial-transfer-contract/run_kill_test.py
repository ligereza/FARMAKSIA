"""Kill tests for the X-ANA-X tutorial-transfer contract."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from run_experiment import SOURCE_CARDS, bridge_status, compose, dry_run_status  # noqa: E402


def main() -> None:
    cards = json.loads(SOURCE_CARDS.read_text(encoding="utf-8"))
    maya = cards["maya"]
    blender = cards["blender"]
    bridge = cards["maya_to_blender_bridge"]

    missing_postcondition = deepcopy(maya)
    missing_postcondition["steps"][0].pop("postconditions")
    assert dry_run_status(missing_postcondition, adapter="maya-native-python")["status"] == "DRY_RUN_BLOCKED"

    assert bridge_status(maya, blender, None)["status"] == "BRIDGE_BLOCKED"

    mismatched_bridge = deepcopy(bridge)
    mismatched_bridge["to_application"] = "photoshop"
    assert bridge_status(maya, blender, mismatched_bridge)["status"] == "BRIDGE_BLOCKED"

    assert compose(maya, blender, bridge)["status"] == "COMPOSABLE_DRY_RUN"
    blocked = compose(maya, blender, None)
    assert blocked["status"] == "COMPOSITION_BLOCKED"
    assert blocked["execution_allowed"] is False

    print("XANAX_059_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
