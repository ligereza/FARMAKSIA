"""Test the opt-in naturalistic trace with synthetic summaries only."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace


RUNTIME = Path(__file__).resolve().parents[1] / "033-vizz-python-headless-runtime"
sys.path.insert(0, str(RUNTIME))

from interaction_trace import InteractionTrace  # noqa: E402


def main() -> None:
    sample = SimpleNamespace(
        quality=0.9,
        disagreement_deg=2.0,
        features=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6),
        eye_centric=(0.6, 0.5, 0.4, 0.3, 0.2, 0.1),
        eye_centric_distance_px=72.0,
        eye_centric_roll_rad=-1.5,
        pose=(0.5, 0.5, 0.2, 0.3, 0.0, 0.1),
    )
    with tempfile.TemporaryDirectory(prefix="farmaxia-vizz-trace-") as directory:
        path = Path(directory) / "trace.jsonl"
        trace = InteractionTrace(path, (1707, 960), sample_hz=20.0)
        trace.write_sample(10.0, sample, (800.0, 420.0), (640, 360))
        trace.write_sample(10.05, None, None, (641, 361))
        trace.close()
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    result = {
        "schema": "farmaxia:vizz-naturalistic-trace:0.1",
        "row_types": [row["type"] for row in rows],
        "mouse_saved": rows[1]["mouse_screen"] == [640, 360],
        "gaze_and_eye_centric_saved": rows[1]["gaze_valid"] and rows[1]["eye_centric"] is not None,
        "invalid_gaze_keeps_mouse": rows[2]["gaze_valid"] is False and rows[2]["mouse_screen"] == [641, 361],
        "raw_video": any(row.get("raw_video") is True for row in rows),
        "screen_content": any(row.get("screen_content") is True for row in rows),
        "mouse_is_ground_truth": any(row.get("mouse_is_ground_truth") is True for row in rows),
        "human_data": False,
    }
    result["all_properties_hold"] = (
        result["row_types"] == ["header", "sample", "sample", "footer"]
        and result["mouse_saved"]
        and result["gaze_and_eye_centric_saved"]
        and result["invalid_gaze_keeps_mouse"]
        and not result["raw_video"]
        and not result["screen_content"]
        and not result["mouse_is_ground_truth"]
    )
    print(json.dumps(result, indent=2))
    if not result["all_properties_hold"]:
        raise SystemExit(1)
    print("NATURALISTIC_TRACE_VALID")


if __name__ == "__main__":
    main()
