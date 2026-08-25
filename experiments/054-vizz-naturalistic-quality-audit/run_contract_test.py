"""Kill tests for the offline VIZZ quality trace auditor."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from quality_audit import DisplayLayout, summarize_trace  # noqa: E402


def make_trace(path: Path, *, raw_video: bool = False, blink: bool = False) -> None:
    rows = [
        {"schema": "farmaxia:vizz-binocular-quality-trace:0.2", "type": "header", "raw_video": raw_video, "screen_content": False},
        {
            "type": "sample",
            "t_monotonic": 1.0,
            "quality": 0.9,
            "disagreement_deg": 1.0,
            "eye_centric_distance_px": 60.0,
            "binocular_ray_proxy": {"status": "VALID_RELATIVE_PROXY"},
            "mouse_screen": [100, 200],
            **({"blink_state": "closed"} if blink else {}),
        },
        {"type": "footer", "sample_count": 1, "raw_video": False, "screen_content_mutated": False},
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def main() -> None:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as directory:
        valid = Path(directory) / "valid.jsonl"
        make_trace(valid)
        summary = summarize_trace(valid, DisplayLayout())
        if summary.sample_count != 1 or summary.ray_valid_count != 1:
            failures.append("valid trace was not summarized")
        if summary.blink_signal_available:
            failures.append("blink signal was falsely inferred from a trace without blink fields")

        blink = Path(directory) / "blink.jsonl"
        make_trace(blink, blink=True)
        blink_summary = summarize_trace(blink, DisplayLayout())
        if not blink_summary.blink_signal_available:
            failures.append("blink field availability was not surfaced")

        unsafe = Path(directory) / "unsafe.jsonl"
        make_trace(unsafe, raw_video=True)
        try:
            summarize_trace(unsafe, DisplayLayout())
        except ValueError:
            pass
        else:
            failures.append("raw-video trace was not rejected")

    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("VIZZ_054_NATURALISTIC_QUALITY_AUDIT_CONTRACT_VALID")


if __name__ == "__main__":
    main()
