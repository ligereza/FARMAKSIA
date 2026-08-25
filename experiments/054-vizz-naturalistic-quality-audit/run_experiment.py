"""Synthetic contract fixture for the offline VIZZ trace auditor."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from quality_audit import DisplayLayout, summarize_trace  # noqa: E402


def main() -> None:
    rows = [
        {
            "schema": "farmaxia:vizz-binocular-quality-trace:0.2",
            "type": "header",
            "raw_video": False,
            "screen_content": False,
        },
        {
            "type": "sample",
            "t_monotonic": 10.0,
            "quality": 0.9,
            "disagreement_deg": 1.0,
            "eye_centric_distance_px": 60.0,
            "binocular_ray_proxy": {"status": "VALID_RELATIVE_PROXY"},
            "mouse_screen": [100, 200],
        },
        {
            "type": "sample",
            "t_monotonic": 10.1,
            "quality": 0.8,
            "disagreement_deg": 2.0,
            "eye_centric_distance_px": 62.0,
            "binocular_ray_proxy": {"status": "VALID_RELATIVE_PROXY"},
            "mouse_screen": [2700, 200],
        },
        {
            "type": "footer",
            "sample_count": 2,
            "raw_video": False,
            "screen_content_mutated": False,
            "keyboard_event_count_total": 1,
            "keyboard_active_sample_count": 1,
        },
    ]
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "trace.jsonl"
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
        summary = summarize_trace(path, DisplayLayout())
    if summary.sample_count != 2 or summary.ray_valid_count != 2:
        raise SystemExit("synthetic trace counts were not recovered")
    if summary.pointer_regions != {"DISPLAY1": 1, "DISPLAY2": 1, "GAP_OR_UNMAPPED": 0, "OUTSIDE_KNOWN_LAYOUT": 0}:
        raise SystemExit("pointer-to-layout classification failed")
    print(json.dumps({"sample_count": summary.sample_count, "ray_valid_count": summary.ray_valid_count, "contract": "VIZZ_054_NATURALISTIC_QUALITY_AUDIT_CONTRACT_VALID"}))


if __name__ == "__main__":
    main()
