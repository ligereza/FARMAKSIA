"""Adversarial tests for read-only media representation normalization."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_experiment import compile_fixture, load_fixture  # noqa: E402


def assert_blocked(fixture: dict, reason: str) -> None:
    result = compile_fixture(fixture)
    assert result["status"] == "BLOCKED", reason
    assert result["blockers"], reason


def main() -> None:
    base = load_fixture()

    otio_hash = deepcopy(base)
    otio_hash["representations"]["otio"]["tracks"][0]["children"][0]["media_reference"]["metadata"]["sha256"] = "sha256:unknown"
    assert_blocked(otio_hash, "OTIO unknown hash was accepted")

    otio_range = deepcopy(base)
    otio_range["representations"]["otio"]["tracks"][0]["children"][0]["source_range"]["start_time"]["value"] = 220
    assert_blocked(otio_range, "OTIO source range was accepted outside asset")

    otio_marker = deepcopy(base)
    otio_marker["representations"]["otio"]["markers"] = []
    assert_blocked(otio_marker, "OTIO marker loss was hidden")

    ffprobe_stream = deepcopy(base)
    ffprobe_stream["representations"]["ffprobe"]["streams"] = []
    assert_blocked(ffprobe_stream, "missing ffprobe streams were accepted")

    ffprobe_timebase = deepcopy(base)
    ffprobe_timebase["representations"]["ffprobe"]["streams"][0]["time_base"] = "0/0"
    assert_blocked(ffprobe_timebase, "invalid ffprobe timebase was accepted")

    ffprobe_claim = deepcopy(base)
    ffprobe_claim["representations"]["ffprobe"]["claims_complete"] = True
    assert_blocked(ffprobe_claim, "incomplete ffprobe representation claimed complete")

    identity_mismatch = deepcopy(base)
    identity_mismatch["representations"]["ffprobe"]["format"]["tags"]["farmaxia_asset_ref"] = "media-catalog:farmaksia:asset:other"
    assert_blocked(identity_mismatch, "cross-representation identity mismatch was accepted")

    read_write = deepcopy(base)
    read_write["adapter"]["read_only"] = False
    assert_blocked(read_write, "representation bridge write policy was enabled")

    missing_representation = deepcopy(base)
    del missing_representation["representations"]["otio"]
    assert_blocked(missing_representation, "missing OTIO representation was accepted")

    missing_event = deepcopy(base)
    missing_event["adapter"]["required_event_ids"] = ["ev-missing"]
    assert_blocked(missing_event, "missing bridge event was accepted")

    print("FARMAXIA_073_MEDIA_REPRESENTATION_BRIDGE_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
