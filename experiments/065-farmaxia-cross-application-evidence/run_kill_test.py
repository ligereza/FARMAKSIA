"""Adversarial tests for identity, provenance, safety and independent verification."""

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

    missing_project_identity = deepcopy(base)
    missing_project_identity["events"][0]["project_id"] = None
    assert_blocked(missing_project_identity, "event detached from project identity")

    external_write = deepcopy(base)
    external_write["action"]["dry_run"] = False
    assert_blocked(external_write, "external write became executable")

    missing_provenance = deepcopy(base)
    missing_provenance["representation_claims"][1]["source_refs"] = []
    assert_blocked(missing_provenance, "claim lost source provenance")

    stale_precondition = deepcopy(base)
    stale_precondition["action"]["preconditions"][0]["source_version"] = 41
    assert_blocked(stale_precondition, "stale source version was accepted")

    conflicting_duplicate = deepcopy(base)
    conflicting_duplicate["events"][3]["payload"]["state"] = "merged"
    assert_blocked(conflicting_duplicate, "duplicate delivery changed meaning")

    permission_mismatch = deepcopy(base)
    permission_mismatch["mattermost_surface"]["permissions"] = []
    assert_blocked(permission_mismatch, "target permission was assumed")

    fake_success = deepcopy(base)
    fake_success["action"]["claimed_outcome"] = "SUCCESS"
    assert_blocked(fake_success, "representation claimed success without effect observation")

    unqualified_claim = deepcopy(base)
    unqualified_claim["representation_claims"][0]["source_refs"] = ["gitlab:merge_request:mr-7"]
    assert_blocked(unqualified_claim, "claim used an unqualified identity")

    print("FARMAXIA_065_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
