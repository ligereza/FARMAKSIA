"""Adversarial tests for watermarks, late events and causal authority."""

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

    dropped_late_event = deepcopy(base)
    dropped_late_event["messages"] = [message for message in dropped_late_event["messages"] if message.get("message_id") != "ev-pipeline-failed-correction"]
    assert_blocked(dropped_late_event, "late correction was dropped")

    reject_late_policy = deepcopy(base)
    reject_late_policy["policy"]["late_event_policy"] = "drop"
    assert_blocked(reject_late_policy, "late-event policy dropped evidence")

    non_monotone_watermark = deepcopy(base)
    non_monotone_watermark["messages"][4]["watermark"] = 150
    assert_blocked(non_monotone_watermark, "watermark moved backwards")

    conflicting_duplicate = deepcopy(base)
    conflicting_duplicate["messages"][7]["payload"]["value"] = "failed"
    assert_blocked(conflicting_duplicate, "duplicate delivery changed meaning")

    lost_supersession = deepcopy(base)
    lost_supersession["messages"][5]["supersedes"] = []
    assert_blocked(lost_supersession, "correction lost its supersession relation")

    promoted_unknown = deepcopy(base)
    promoted_unknown["messages"][8]["parents"] = ["ev-pipeline-success"]
    assert_blocked(promoted_unknown, "missing causal authority became a fact")

    causal_child_detached = deepcopy(base)
    causal_child_detached["messages"][9]["parents"] = ["ev-missing-parent"]
    assert_blocked(causal_child_detached, "causal child was detached from its authority")

    future_source_version = deepcopy(base)
    future_source_version["messages"][1]["source_version"] = 99
    assert_blocked(future_source_version, "future source version was accepted")

    print("FARMAXIA_067_WATERMARK_LATE_REPLAY_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
