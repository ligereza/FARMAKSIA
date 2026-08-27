"""Adversarial tests for temporal replay, retraction and conflict boundaries."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_experiment import compile_fixture  # noqa: E402


def load_fixture() -> dict:
    return json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))


def assert_blocked(fixture: dict, reason: str) -> None:
    result = compile_fixture(fixture)
    assert result["status"] == "BLOCKED", reason
    assert result["blockers"], reason


def main() -> None:
    base = load_fixture()

    missing_valid_time = deepcopy(base)
    missing_valid_time["events"][0]["valid_time"] = None
    assert_blocked(missing_valid_time, "timeless set event was applied")

    unknown_retraction_target = deepcopy(base)
    unknown_retraction_target["events"][1]["revokes"] = ["ev-missing"]
    assert_blocked(unknown_retraction_target, "retraction targeted unknown evidence")

    conflicting_duplicate = deepcopy(base)
    conflicting_duplicate["events"][5]["payload"]["value"] = "success"
    assert_blocked(conflicting_duplicate, "duplicate delivery changed meaning")

    conflict_collapsed = deepcopy(base)
    conflict_collapsed["events"][3]["source_version"] = 7
    assert_blocked(conflict_collapsed, "same-version conflict disappeared without audit")

    retraction_history_lost = deepcopy(base)
    retraction_history_lost["events"] = [event for event in retraction_history_lost["events"] if event["event_id"] != "ev-pipeline-retract"]
    assert_blocked(retraction_history_lost, "retraction history was lost")

    unknown_promoted = deepcopy(base)
    unknown_promoted["events"][8]["kind"] = "set"
    assert_blocked(unknown_promoted, "missing temporal authority became a supported fact")

    source_version_ahead = deepcopy(base)
    source_version_ahead["events"][0]["source_version"] = 99
    assert_blocked(source_version_ahead, "event version exceeded source version")

    print("FARMAXIA_066_TEMPORAL_REPLAY_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
