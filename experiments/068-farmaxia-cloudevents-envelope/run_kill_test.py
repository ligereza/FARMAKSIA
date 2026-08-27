"""Adversarial tests for CloudEvents identity and FARMAKSIA mapping."""

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


def event_by_id(fixture: dict, event_id: str, occurrence: int = 0) -> dict:
    matches = [event for event in fixture["events"] if event.get("id") == event_id]
    return matches[occurrence]


def assert_blocked(fixture: dict, reason: str) -> None:
    result = compile_fixture(fixture)
    assert result["status"] == "BLOCKED", reason
    assert result["blockers"], reason


def main() -> None:
    base = load_fixture()

    missing_specversion = deepcopy(base)
    missing_specversion["events"][0].pop("specversion")
    assert_blocked(missing_specversion, "missing CloudEvents version was accepted")

    invalid_source_uri = deepcopy(base)
    invalid_source_uri["events"][0]["source"] = "gitlab://"
    assert_blocked(invalid_source_uri, "relative source was accepted")

    identity_mismatch = deepcopy(base)
    event_by_id(identity_mismatch, "ev-mr-open")["data"]["event_id"] = "ev-other"
    assert_blocked(identity_mismatch, "data identity detached from CloudEvent id")

    missing_provenance = deepcopy(base)
    event_by_id(missing_provenance, "ev-pipeline-fail").pop("farmaxia-source-version")
    assert_blocked(missing_provenance, "missing source version was accepted")

    subject_mismatch = deepcopy(base)
    event_by_id(subject_mismatch, "ev-mr-comment")["subject"] = "projects/proj-other/merge_requests/mr-7"
    assert_blocked(subject_mismatch, "subject detached from qualified entity")

    conflicting_duplicate = deepcopy(base)
    event_by_id(conflicting_duplicate, "ev-mr-open", occurrence=1)["data"]["payload"]["state"] = "merged"
    assert_blocked(conflicting_duplicate, "duplicate source plus id changed meaning")

    foreign_extension = deepcopy(base)
    foreign_extension["events"][0]["traceparent"] = "00-test"
    assert_blocked(foreign_extension, "unscoped extension was accepted")

    unsafe_policy = deepcopy(base)
    unsafe_policy["policy"]["network_allowed"] = True
    assert_blocked(unsafe_policy, "network policy was enabled")

    print("FARMAXIA_068_CLOUDEVENTS_ENVELOPE_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
