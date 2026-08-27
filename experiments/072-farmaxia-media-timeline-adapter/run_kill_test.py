"""Adversarial tests for media clocks, ranges, codec, sync and permissions."""

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

    missing_event = deepcopy(base)
    missing_event["adapter"]["required_event_ids"] = ["ev-missing"]
    assert_blocked(missing_event, "missing media event was accepted")

    out_of_bounds = deepcopy(base)
    out_of_bounds["timeline"]["tracks"][0]["clips"][0]["source_range"]["start"]["value"] = 200
    assert_blocked(out_of_bounds, "source range outside asset was accepted")

    unsupported_codec = deepcopy(base)
    unsupported_codec["player"]["decoder_capabilities"] = []
    assert_blocked(unsupported_codec, "unsupported codec was accepted")

    sync_drift = deepcopy(base)
    sync_drift["timeline"]["tracks"][1]["clips"][0]["timeline_start"]["value"] = 24
    assert_blocked(sync_drift, "audio video drift was hidden")

    invalid_timebase = deepcopy(base)
    invalid_timebase["timeline"]["timebase"]["value"] = 0
    assert_blocked(invalid_timebase, "invalid timebase was accepted")

    marker_mismatch = deepcopy(base)
    marker_mismatch["timeline"]["markers"][0]["source_frame"] = 61
    assert_blocked(marker_mismatch, "marker source mismatch was accepted")

    missing_permission = deepcopy(base)
    missing_permission["player"]["permissions"] = ["read"]
    assert_blocked(missing_permission, "preview without permission was accepted")

    unsafe_export = deepcopy(base)
    unsafe_export["action"]["dry_run"] = False
    assert_blocked(unsafe_export, "external media action was enabled")

    stale_asset = deepcopy(base)
    stale_asset["action"]["preconditions"][0]["sha256"] = "sha256:stale"
    assert_blocked(stale_asset, "stale media hash was accepted")

    missing_provenance = deepcopy(base)
    missing_provenance["representation_claims"][0]["source_refs"] = []
    assert_blocked(missing_provenance, "media claim lost provenance")

    print("FARMAXIA_072_MEDIA_TIMELINE_ADAPTER_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
