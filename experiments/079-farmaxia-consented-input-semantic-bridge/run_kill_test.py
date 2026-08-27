"""Adversarial tests for the consented input observer privacy boundary."""

from __future__ import annotations

from copy import deepcopy
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_experiment import validate  # noqa: E402


def base() -> dict:
    return {
        "status": "CONSENTED_INPUT_OBSERVER_VERIFIED",
        "observation": {
            "sample_count": 3,
            "key_values_persisted": False,
            "text_persisted": False,
            "window_titles_persisted": False,
            "raw_pixels_persisted": False,
            "semantic_intent_claimed": False,
        },
        "actions_performed": [],
        "safety": {
            "network_used": False,
            "screen_capture": False,
            "camera_capture": False,
            "mouse_or_keyboard_injected": False,
            "source_write_attempted": False,
        },
    }


def assert_blocked(payload: dict, reason: str) -> None:
    assert validate(payload), reason


def main() -> None:
    raw_keys = base()
    raw_keys["observation"]["key_values_persisted"] = True
    assert_blocked(raw_keys, "raw key values were accepted")

    raw_titles = base()
    raw_titles["observation"]["window_titles_persisted"] = True
    assert_blocked(raw_titles, "window titles were accepted")

    intent = base()
    intent["observation"]["semantic_intent_claimed"] = True
    assert_blocked(intent, "intent was inferred without state outcome")

    injected = deepcopy(base())
    injected["actions_performed"] = ["click"]
    assert_blocked(injected, "input injection was accepted")

    camera = base()
    camera["safety"]["camera_capture"] = True
    assert_blocked(camera, "camera capability was accepted")

    print("FARMAXIA_079_CONSENTED_INPUT_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
