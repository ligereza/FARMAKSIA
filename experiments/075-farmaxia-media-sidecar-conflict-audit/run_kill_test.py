"""Adversarial tests for conflict preservation and safe abstention."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_experiment import compile_fixture, load_fixture  # noqa: E402


def assert_blocked(fixture: dict, reason: str) -> None:
    result = compile_fixture(fixture)
    assert result["status"] == "BLOCKED", reason
    assert result["blockers"], reason


def main() -> None:
    base = load_fixture()

    missing_candidates = deepcopy(base)
    missing_candidates["sidecars"] = [missing_candidates["sidecars"][0]]
    assert_blocked(missing_candidates, "missing candidate was accepted")

    duplicate_ids = deepcopy(base)
    duplicate_ids["sidecars"][1]["sidecar_id"] = duplicate_ids["sidecars"][0]["sidecar_id"]
    assert_blocked(duplicate_ids, "duplicate sidecar id was accepted")

    wrong_hash = deepcopy(base)
    wrong_hash["sidecars"][1]["asset_sha256"] = "sha256:stale"
    assert_blocked(wrong_hash, "stale sidecar hash was accepted")

    wrong_version = deepcopy(base)
    wrong_version["sidecars"][1]["source_version"] = 3
    assert_blocked(wrong_version, "stale sidecar version was accepted")

    wrong_scope = deepcopy(base)
    wrong_scope["sidecars"][1]["asset_ref"] = "media-catalog:farmaksia:asset:other"
    assert_blocked(wrong_scope, "cross-asset sidecar was accepted")

    writable = deepcopy(base)
    writable["sidecars"][1]["read_only"] = False
    assert_blocked(writable, "writable sidecar was accepted")

    unsafe_action = deepcopy(base)
    unsafe_action["action"]["dry_run"] = False
    assert_blocked(unsafe_action, "non-dry-run conflict action was accepted")

    preferred = deepcopy(base)
    preferred["preferred_sidecar_id"] = preferred["sidecars"][0]["sidecar_id"]
    assert_blocked(preferred, "silent preferred sidecar was accepted")

    missing_event = deepcopy(base)
    missing_event["adapter"]["required_event_ids"] = ["ev-missing"]
    assert_blocked(missing_event, "missing required event was accepted")

    same_claim = deepcopy(base)
    same_claim["sidecars"][1]["marker"] = deepcopy(same_claim["sidecars"][0]["marker"])
    same_claim["sidecars"][1]["source_refs"] = deepcopy(same_claim["sidecars"][0]["source_refs"])
    assert_blocked(same_claim, "identical claims were accepted as a conflict")

    print("FARMAXIA_075_MEDIA_SIDECAR_CONFLICT_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
