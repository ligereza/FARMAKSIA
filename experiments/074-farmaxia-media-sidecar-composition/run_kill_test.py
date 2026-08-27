"""Adversarial tests for sidecar joins and composition safety."""

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

    stale_hash = deepcopy(base)
    stale_hash["sidecar"]["asset_sha256"] = "sha256:stale"
    assert_blocked(stale_hash, "stale sidecar hash was accepted")

    stale_version = deepcopy(base)
    stale_version["sidecar"]["source_version"] = 3
    assert_blocked(stale_version, "stale sidecar version was accepted")

    wrong_identity = deepcopy(base)
    wrong_identity["sidecar"]["asset_ref"] = "media-catalog:farmaksia:asset:other"
    assert_blocked(wrong_identity, "sidecar identity mismatch was accepted")

    out_of_bounds = deepcopy(base)
    out_of_bounds["sidecar"]["video"]["source_start"]["value"] = 220
    assert_blocked(out_of_bounds, "sidecar range outside asset was accepted")

    marker_mismatch = deepcopy(base)
    marker_mismatch["sidecar"]["marker"]["source_frame"] = 61
    assert_blocked(marker_mismatch, "sidecar marker mismatch was accepted")

    audio_drift = deepcopy(base)
    audio_drift["sidecar"]["audio"]["timeline_start"]["value"] = 24
    assert_blocked(audio_drift, "sidecar audio drift was accepted")

    missing_refs = deepcopy(base)
    missing_refs["sidecar"]["source_refs"] = []
    assert_blocked(missing_refs, "sidecar provenance was omitted")

    writable_sidecar = deepcopy(base)
    writable_sidecar["sidecar"]["read_only"] = False
    assert_blocked(writable_sidecar, "sidecar write policy was enabled")

    unsafe_action = deepcopy(base)
    unsafe_action["action"]["dry_run"] = False
    assert_blocked(unsafe_action, "external media action was enabled")

    missing_event = deepcopy(base)
    missing_event["adapter"]["required_event_ids"] = ["ev-missing"]
    assert_blocked(missing_event, "required event was omitted")

    print("FARMAXIA_074_MEDIA_SIDECAR_COMPOSITION_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
