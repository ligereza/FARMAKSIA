"""Adversarial tests for false equivalence and unsafe adapter capabilities."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from lighting_surface_contract import ContractError, LightingSurfaceContract  # noqa: E402


def load_fixture() -> dict:
    return json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))


def assert_rejected(fixture: dict, reason: str) -> None:
    try:
        LightingSurfaceContract.from_value(fixture)
    except (ContractError, TypeError, ValueError):
        return
    raise AssertionError(reason)


def main() -> None:
    base = load_fixture()

    overlapping_destination = deepcopy(base)
    overlapping_destination["regions"][1]["destination_rect"] = overlapping_destination["regions"][0]["destination_rect"]
    assert_rejected(overlapping_destination, "adapter accepted overlapping destination regions")

    missing_target_term = deepcopy(base)
    missing_target_term["regions"][0]["target_term"] = None
    assert_rejected(missing_target_term, "adapter called an unmapped task equivalent")

    unsupported_with_confidence = deepcopy(base)
    unsupported_with_confidence["regions"][2]["status"] = "unsupported"
    unsupported_with_confidence["regions"][2]["confidence"] = 0.5
    assert_rejected(unsupported_with_confidence, "adapter assigned confidence to unsupported mapping")

    unsafe_capability = deepcopy(base)
    unsafe_capability["capabilities"] = ["read_only", "preview"]
    assert_rejected(unsafe_capability, "adapter omitted execute_blocked capability")

    wrong_target = deepcopy(base)
    wrong_target["target_vocabulary"] = "grandMA3"
    assert_rejected(wrong_target, "adapter accepted a target other than Titan")

    incomplete_tasks = deepcopy(base)
    incomplete_tasks["regions"] = incomplete_tasks["regions"][:-1]
    assert_rejected(incomplete_tasks, "adapter accepted missing canonical task")

    print("FARMAXIA_083_LIGHTING_SURFACE_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
