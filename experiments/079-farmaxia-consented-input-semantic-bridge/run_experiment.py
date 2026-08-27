"""Run the real local input observer without capturing content or injecting input."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from input_bridge import observe  # noqa: E402


def validate(result: dict) -> list[str]:
    blockers: list[str] = []
    if result.get("status") != "CONSENTED_INPUT_OBSERVER_VERIFIED":
        blockers.append("observer_not_verified")
    if int(result.get("observation", {}).get("sample_count", 0)) <= 0:
        blockers.append("no_observation_samples")
    observation = result.get("observation", {})
    for field in ("key_values_persisted", "text_persisted", "window_titles_persisted", "raw_pixels_persisted", "semantic_intent_claimed"):
        if observation.get(field) is not False:
            blockers.append(f"privacy_boundary_broken:{field}")
    if result.get("actions_performed") != []:
        blockers.append("input_injection_boundary_broken")
    for field in ("network_used", "screen_capture", "camera_capture", "mouse_or_keyboard_injected", "source_write_attempted"):
        if result.get("safety", {}).get(field) is not False:
            blockers.append(f"unsafe_capability_enabled:{field}")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Opt-in local semantic input observer")
    parser.add_argument("--duration", type=float, default=2.0)
    parser.add_argument("--sample-hz", type=float, default=8.0)
    parser.add_argument("--pointer", action="store_true", help="record pointer position locally as an optional covariate")
    args = parser.parse_args()
    observation = observe(args.duration, args.sample_hz, args.pointer)
    result = {
        "status": "CONSENTED_INPUT_OBSERVER_VERIFIED",
        "experiment": "079-farmaxia-consented-input-semantic-bridge",
        "observation": observation,
        "event_semantics": {
            "keyboard_activity": "count_only_input_activity",
            "focus_context_changed": "foreground_app_or_UIA_role_changed",
            "pointer_motion": "pointer_position_changed_when_explicitly_enabled",
            "idle_observation": "no_observed_transition_in_sample_interval",
        },
        "actions_performed": [],
        "read_only": True,
        "safety": {
            "network_used": False,
            "screen_capture": False,
            "camera_capture": False,
            "mouse_or_keyboard_injected": False,
            "source_write_attempted": False,
        },
    }
    result["validation_blockers"] = validate(result)
    if result["validation_blockers"]:
        result["status"] = "BLOCKED"
    print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
