"""Deterministic tests for the VIZZ 084 trace analyzer."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from analyze_trace import analyze_trace  # noqa: E402


def main() -> None:
    header = {
        "schema": "farmaxia:vizz-distance-scale-trace:0.3",
        "reference_source": "explicit_space_face_geometry",
        "card_role": "not_used_for_relative_scale",
        "reference": {"eye_distance_px": 60.0, "face_width_px": 120.0},
        "raw_video": False,
        "screen_content_mutated": False,
        "input_injected": False,
        "text_persisted": False,
    }
    samples = []
    for index, scale in enumerate((1.0, 0.8, 0.6)):
        samples.append(
            {
                "type": "sample",
                "t_monotonic": float(index),
                "eye_distance_px": 60.0 * scale,
                "face_width_px": 120.0 * scale,
                "target_diameter_px": 100.0 / scale,
                "scale": {
                    "status": "VALID",
                    "eye_scale": scale,
                    "face_scale": scale,
                    "fused_scale": scale,
                    "relative_distance_ratio": 1.0 / scale,
                    "log_disagreement": 0.0,
                },
            }
        )
    samples.append({"type": "sample", "t_monotonic": 3.0, "scale": {"status": "UNKNOWN"}})
    footer = {"type": "footer", "sample_count": 4, "valid_count": 3, "unknown_count": 1}
    result = analyze_trace(header, samples, footer)
    assert result["status"] == "VIZZ_TRACE_ANALYZED_EXPLORATORY"
    assert result["input"]["valid_rate"] == 0.75
    assert result["integrity"]["footer_consistent"] is True
    assert result["interpretation"]["rulers_agree"] is True
    assert result["relative_estimate"]["target_diameter_px"]["median"] == 100.0 / 0.8
    assert result["interpretation"]["absolute_distance_mm"].startswith("UNKNOWN")
    print("FARMAXIA_084_VIZZ_TRACE_ANALYZER_TEST_VALID")


if __name__ == "__main__":
    main()
