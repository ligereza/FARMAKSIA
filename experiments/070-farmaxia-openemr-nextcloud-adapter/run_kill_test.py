"""Adversarial tests for the synthetic institutional document adapter."""

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

    missing_required_event = deepcopy(base)
    missing_required_event["adapter"]["required_event_ids"] = ["ev-missing"]
    assert_blocked(missing_required_event, "missing required event was accepted")

    source_mismatch = deepcopy(base)
    source_mismatch["adapter"]["source_surface"] = "nextcloud"
    assert_blocked(source_mismatch, "source surface was reassigned")

    missing_claim_provenance = deepcopy(base)
    missing_claim_provenance["representation_claims"][0]["source_refs"] = []
    assert_blocked(missing_claim_provenance, "claim lost source provenance")

    unsafe_write = deepcopy(base)
    unsafe_write["action"]["dry_run"] = False
    assert_blocked(unsafe_write, "external write was enabled")

    missing_destination_permission = deepcopy(base)
    missing_destination_permission["nextcloud_surface"]["permissions"] = ["read"]
    assert_blocked(missing_destination_permission, "destination write permission was assumed")

    stale_precondition = deepcopy(base)
    stale_precondition["action"]["preconditions"][0]["source_version"] = 11
    assert_blocked(stale_precondition, "stale source precondition was accepted")

    source_record_changed = deepcopy(base)
    source_record_changed["source_of_truth"]["records"][1]["status"] = "draft"
    assert_blocked(source_record_changed, "source snapshot conflict was hidden")

    input_policy_changed = deepcopy(base)
    input_policy_changed["policy"]["human_data"] = True
    assert_blocked(input_policy_changed, "human data policy was enabled")

    print("FARMAXIA_070_DOCUMENTAL_ADAPTER_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
