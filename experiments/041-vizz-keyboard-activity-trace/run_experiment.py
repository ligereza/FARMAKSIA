"""Synthetic no-human-data contract for count-only keyboard activity."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "experiments/033-vizz-python-headless-runtime"
sys.path.insert(0, str(RUNTIME))
sys.path.insert(0, str(Path(__file__).parent))

from interaction_trace import InteractionTrace  # noqa: E402
from keyboard_trace_audit import audit_keyboard_trace  # noqa: E402


def main() -> None:
    sample = SimpleNamespace(
        quality=0.91,
        disagreement_deg=1.2,
        features=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6),
        eye_centric=(0.6, 0.5, 0.4, 0.3, 0.2, 0.1),
        eye_centric_distance_px=72.0,
        eye_centric_roll_rad=0.02,
        pose=(0.5, 0.5, 0.2, 0.3, 0.0, 0.08),
        pretrained_gaze_deg=(12.0, -8.0),
        pretrained_gaze_unknown_reason=None,
        binocular_gaze_deg=(10.0, -7.0),
        raw_model_angle_delta_deg=2.236067977,
    )
    with tempfile.TemporaryDirectory(prefix="farmaxia-vizz-keyboard-audit-") as directory:
        path = Path(directory) / "trace.jsonl"
        trace = InteractionTrace(path, (1707, 960), sample_hz=20.0, keyboard_activity_only=True)
        trace.write_sample(
            10.0,
            sample,
            (0.2, 0.3),
            (640, 360),
            {"keyboard_event_count": 3, "keyboard_active": True, "keyboard_last_event_age_ms": 4.0},
        )
        trace.write_sample(
            10.05,
            None,
            None,
            (641, 361),
            {"keyboard_event_count": 0, "keyboard_active": False, "keyboard_last_event_age_ms": 54.0},
        )
        trace.close()
        result = audit_keyboard_trace(path)
    result["all_properties_hold"] = (
        result["sample_count"] == 2
        and result["active_sample_count"] == 1
        and result["event_count"] == 3
        and result["key_values_persisted"] is False
        and result["text_persisted"] is False
        and result["raw_video"] is False
        and result["screen_content"] is False
    )
    print(json.dumps(result, indent=2))
    if not result["all_properties_hold"]:
        raise SystemExit(1)
    print("KEYBOARD_TRACE_VALID")


if __name__ == "__main__":
    main()
