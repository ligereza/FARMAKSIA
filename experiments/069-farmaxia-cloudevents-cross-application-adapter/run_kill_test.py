"""Adversarial tests for the CloudEvents cross-application adapter."""

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

    missing_required_input = deepcopy(base)
    missing_required_input["adapter"]["required_event_ids"] = ["ev-missing"]
    assert_blocked(missing_required_input, "adapter accepted missing input event")

    unsafe_destination = deepcopy(base)
    unsafe_destination["action"]["dry_run"] = False
    assert_blocked(unsafe_destination, "adapter enabled external execution")

    missing_claim_provenance = deepcopy(base)
    missing_claim_provenance["representation_claims"][1]["source_refs"] = []
    assert_blocked(missing_claim_provenance, "adapter lost claim provenance")

    stale_precondition = deepcopy(base)
    stale_precondition["action"]["preconditions"][0]["source_version"] = 41
    assert_blocked(stale_precondition, "adapter accepted stale precondition")

    missing_permission = deepcopy(base)
    missing_permission["mattermost_surface"]["permissions"] = []
    assert_blocked(missing_permission, "adapter assumed destination permission")

    detached_event = deepcopy(base)
    detached_event["adapter"]["required_event_ids"] = ["ev-other"]
    assert_blocked(detached_event, "adapter accepted detached event identity")

    input_envelope_corruption = deepcopy(base)
    input_envelope_corruption["adapter"]["input_envelope"] = "not-the-approved-envelope.json"
    assert_blocked(input_envelope_corruption, "adapter ignored declared input envelope")

    print("FARMAXIA_069_CLOUDEVENTS_ADAPTER_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
