"""Audit the privacy and interval semantics of a VIZZ keyboard trace."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


FORBIDDEN_FIELDS = {
    "key",
    "keys",
    "key_code",
    "key_value",
    "vk_code",
    "character",
    "characters",
    "text",
    "typed_text",
    "active_window",
    "window_title",
}


def audit_keyboard_trace(path: Path) -> dict[str, Any]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) < 2 or rows[0].get("type") != "header" or rows[-1].get("type") != "footer":
        raise ValueError("keyboard trace must have header and footer")
    header = rows[0]
    if header.get("keyboard_activity_only") is not True:
        raise ValueError("trace does not declare keyboard activity only")
    if header.get("key_values_persisted") is not False or header.get("text_persisted") is not False:
        raise ValueError("trace privacy flags are invalid")
    samples = [row for row in rows if row.get("type") == "sample"]
    if rows[-1].get("sample_count") != len(samples):
        raise ValueError("footer sample_count does not match rows")
    timestamps = [float(row["t_monotonic"]) for row in samples]
    if any(not math.isfinite(value) for value in timestamps) or any(
        right <= left for left, right in zip(timestamps, timestamps[1:])
    ):
        raise ValueError("sample timestamps are not strictly monotonic")
    for row in samples:
        count = row.get("keyboard_event_count")
        if not isinstance(count, int) or count < 0:
            raise ValueError("keyboard_event_count must be a non-negative integer")
        if row.get("keyboard_active") is not (count > 0):
            raise ValueError("keyboard_active disagrees with interval count")
        age_ms = row.get("keyboard_last_event_age_ms")
        if age_ms is not None and (not math.isfinite(float(age_ms)) or float(age_ms) < 0.0):
            raise ValueError("keyboard_last_event_age_ms is invalid")
        if FORBIDDEN_FIELDS.intersection(row):
            raise ValueError("trace contains a key/text/window field")
    return {
        "schema": "farmaxia:vizz-keyboard-activity-audit:0.1",
        "sample_count": len(samples),
        "active_sample_count": sum(row["keyboard_active"] for row in samples),
        "event_count": sum(row["keyboard_event_count"] for row in samples),
        "key_values_persisted": False,
        "text_persisted": False,
        "raw_video": False,
        "screen_content": False,
        "human_data": False,
    }
