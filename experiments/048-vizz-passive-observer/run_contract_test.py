"""Contract test for the privacy boundary of VIZZ passive observation."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from passive_trace import PassiveTraceWriter, audit_trace  # noqa: E402


def main() -> None:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="farmaxia-vizz-048-contract-") as directory:
        path = Path(directory) / "trace.jsonl"
        writer = PassiveTraceWriter(path, "layout-v1")
        writer.write_sample(
            1.0,
            {
                "status": "VALID",
                "monitor_id": "primary",
                "uv": [0.5, 0.5],
                "confidence": 0.9,
                "uncertainty_deg": 0.5,
                "safe_radius_deg": 3.0,
                "fixation_state": "fixation",
                "unknown_reason": None,
                "candidate_monitor_ids": ["primary"],
            },
            {"keyboard_event_count": 1, "keyboard_active": True, "mouse_screen": (12, 20)},
        )
        writer.write_sample(
            1.1,
            {
                "status": "UNKNOWN",
                "monitor_id": None,
                "uv": None,
                "confidence": 0.2,
                "uncertainty_deg": 8.5,
                "safe_radius_deg": 0.0,
                "fixation_state": "unknown",
                "unknown_reason": "low_confidence",
                "candidate_monitor_ids": [],
            },
            {"keyboard_event_count": 0, "keyboard_active": False, "mouse_screen": (13, 21)},
        )
        writer.close()
        audit = audit_trace(path)
        raw = path.read_text(encoding="utf-8")
    if audit["sample_count"] != 2 or audit["valid_gaze_count"] != 1:
        failures.append("passive audit counts are incorrect")
    if audit["unknown_counts"] != {"low_confidence": 1}:
        failures.append("UNKNOWN reason was not preserved")
    if audit["mouse_is_ground_truth"] is not False:
        failures.append("mouse ground truth boundary was not explicit")
    if '"key_value":' in raw.lower() or '"text_value":' in raw.lower() or '"video_path":' in raw.lower():
        failures.append("privacy markers are missing or forbidden content is present")
    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("VIZZ_048_PASSIVE_TRACE_CONTRACT_VALID")


if __name__ == "__main__":
    main()
