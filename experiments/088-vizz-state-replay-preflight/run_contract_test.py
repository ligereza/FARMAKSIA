"""Pure checks for the 088 temporal replay boundary."""

from __future__ import annotations

import sys
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_087 = ROOT / "experiments" / "087-vizz-touchdesigner-state-renderer"
sys.path.insert(0, str(EXPERIMENT_087))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_replay import replay_records  # noqa: E402


def payload(**overrides):
    value = {
        "schema": "farmaxia:vizz-state:0.1",
        "seq": 1,
        "timestamp_monotonic_ms": 1000.0,
        "source": "manual",
        "confidence": 0.9,
        "head": {"x": 0.2, "y": -0.1, "z": 0.0, "rx": 0.0, "ry": 0.0, "rz": 0.0},
        "focus": {"x": 0.2, "y": 0.2, "w": 0.4, "h": 0.3, "interest": 0.9},
        "input": {"keyboard_activity": 0.0, "pointer_x": 0.5, "pointer_y": 0.5, "pointer_active": False},
        "window": {
            "selected": True,
            "monitor_id": "display-1",
            "source_rect": {"left": 0, "top": 0, "width": 1280, "height": 720},
        },
        "permissions": {"camera": False, "capture": True, "overlay": True, "input_remap": False},
    }
    value.update(overrides)
    return value


def check_sequence_and_neutral_fallback():
    results = replay_records(
        [
            payload(seq=1, timestamp_monotonic_ms=1000.0),
            payload(seq=2, timestamp_monotonic_ms=1050.0, head={"x": -0.3, "y": 0.1, "z": 0.0, "rx": 0.0, "ry": 0.0, "rz": 0.0}),
            payload(seq=2, timestamp_monotonic_ms=1090.0),
            payload(seq=1, timestamp_monotonic_ms=1095.0),
            payload(seq=3, timestamp_monotonic_ms=1095.0, confidence=0.1),
            payload(seq=4, timestamp_monotonic_ms=0.0),
        ],
        now_ms=1100.0,
    )
    assert [item["status"] for item in results] == ["VALID", "VALID", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN"]
    assert results[0]["plan"]["status"] == "ACTIVE"
    assert results[1]["plan"]["parallax_x"] < 0.0
    assert results[2]["reason"] == "SEQUENCE_NOT_MONOTONIC"
    assert results[3]["reason"] == "SEQUENCE_NOT_MONOTONIC"
    assert results[4]["reason"] == "CONFIDENCE_TOO_LOW"
    assert results[5]["reason"] == "STATE_STALE"
    for item in results[2:]:
        assert item["plan"]["status"] == "NEUTRAL"
        assert item["plan"]["parallax_x"] == 0.0
        assert item["plan"]["critical_sharpness"] == 1.0


def check_invalid_json_is_not_silently_recovered():
    command = [
        sys.executable,
        str(Path(__file__).resolve().parent / "run_replay.py"),
        "--input",
        str(Path(__file__).resolve().parent / "fixtures" / "malformed.jsonl"),
        "--now-ms",
        "1100",
    ]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    assert completed.returncode == 2
    assert "REPLAY_INVALID" in completed.stderr


if __name__ == "__main__":
    check_sequence_and_neutral_fallback()
    check_invalid_json_is_not_silently_recovered()
    print("VIZZ_088_REPLAY_CONTRACT=PASS")
