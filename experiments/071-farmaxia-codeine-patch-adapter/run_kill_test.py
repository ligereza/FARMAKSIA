"""Adversarial tests for the synthetic CODE-INE patch adapter."""

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
    assert_blocked(missing_required_event, "missing required code event was accepted")

    source_mismatch = deepcopy(base)
    source_mismatch["adapter"]["source_surface"] = "editor-workspace"
    assert_blocked(source_mismatch, "code source surface was reassigned")

    missing_claim_provenance = deepcopy(base)
    missing_claim_provenance["representation_claims"][0]["source_refs"] = []
    assert_blocked(missing_claim_provenance, "code claim lost source provenance")

    unsafe_execution = deepcopy(base)
    unsafe_execution["patch"]["code_execution"] = True
    assert_blocked(unsafe_execution, "patch code execution was enabled")

    unsafe_write = deepcopy(base)
    unsafe_write["action"]["dry_run"] = False
    assert_blocked(unsafe_write, "workspace write was enabled")

    missing_preview_permission = deepcopy(base)
    missing_preview_permission["workspace"]["permissions"] = ["read"]
    assert_blocked(missing_preview_permission, "workspace preview permission was assumed")

    stale_precondition = deepcopy(base)
    stale_precondition["action"]["preconditions"][0]["source_version"] = 16
    assert_blocked(stale_precondition, "stale code change precondition was accepted")

    changed_source_check = deepcopy(base)
    changed_source_check["source_of_truth"]["records"][2]["status"] = "failed"
    assert_blocked(changed_source_check, "failed code check was presented as passed")

    base_sha_mismatch = deepcopy(base)
    base_sha_mismatch["patch"]["base_sha256"] = "sha256:unknown"
    assert_blocked(base_sha_mismatch, "patch was applied to an unknown base")

    print("FARMAXIA_071_CODEINE_ADAPTER_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
