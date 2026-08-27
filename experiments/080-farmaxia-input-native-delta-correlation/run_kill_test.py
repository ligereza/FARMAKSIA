"""Adversarial tests for false intent, content retention and unsafe correlation."""

from __future__ import annotations

from copy import deepcopy
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from correlator import correlate  # noqa: E402


def main() -> None:
    input_events = [{"t_monotonic": 1.0, "application_class": "excel"}]
    delta_events = [{"t_monotonic": 1.2, "application_class": "excel", "delta_kind": "modify_property"}]
    candidate = correlate(input_events, delta_events, 750.0)
    assert candidate[0]["status"] == "candidate_association"
    assert candidate[0]["intent_claimed"] is False

    cross_app = correlate(
        [{"t_monotonic": 1.0, "application_class": "blender"}],
        delta_events,
        750.0,
    )
    assert cross_app[0]["status"] == "unassociated_native_delta"

    ambiguous = correlate(
        [
            {"t_monotonic": 1.0, "application_class": "excel"},
            {"t_monotonic": 1.1, "application_class": "excel"},
        ],
        delta_events,
        750.0,
    )
    assert ambiguous[0]["status"] == "ambiguous_association"

    outside_window = correlate(
        [{"t_monotonic": 0.0, "application_class": "excel"}],
        delta_events,
        750.0,
    )
    assert outside_window[0]["status"] == "unassociated_native_delta"

    for result in (candidate, cross_app, ambiguous, outside_window):
        assert all(item["intent_claimed"] is False for item in result)
    print("FARMAXIA_080_INPUT_NATIVE_DELTA_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
