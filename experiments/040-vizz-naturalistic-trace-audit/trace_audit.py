"""Audit an opt-in VIZZ interaction trace without reading pixels or video."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def audit_trace(path: Path) -> dict[str, Any]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) < 2 or rows[0].get("type") != "header" or rows[-1].get("type") != "footer":
        raise ValueError("trace must have header and footer")
    samples = [row for row in rows if row.get("type") == "sample"]
    timestamps = [float(row["t_monotonic"]) for row in samples]
    if any(not math.isfinite(value) for value in timestamps) or any(
        right <= left for left, right in zip(timestamps, timestamps[1:])
    ):
        raise ValueError("sample timestamps are not strictly monotonic")
    header = rows[0]
    if header.get("raw_video") is not False or header.get("screen_content") is not False:
        raise ValueError("trace header violates no-video/no-content contract")
    if header.get("mouse_is_ground_truth") is not False:
        raise ValueError("mouse is incorrectly declared as gaze ground truth")
    forbidden_true = any(
        row.get(field) is True
        for row in rows
        for field in ("raw_video", "screen_content", "mouse_is_ground_truth")
    )
    if forbidden_true:
        raise ValueError("trace contains a forbidden true flag")
    if rows[-1].get("sample_count") != len(samples):
        raise ValueError("footer sample_count does not match rows")
    for row in samples:
        pointer = row.get("mouse_screen")
        if pointer is not None and (not isinstance(pointer, list) or len(pointer) != 2):
            raise ValueError("mouse_screen is not a 2D OS pointer")
        delta = row.get("raw_model_angle_delta_deg")
        if delta is not None and (not math.isfinite(float(delta)) or float(delta) < 0.0):
            raise ValueError("raw model angle delta is invalid")
    return {
        "schema": "farmaxia:vizz-naturalistic-trace-audit:0.1",
        "sample_count": len(samples),
        "mouse_present_count": sum(row.get("mouse_screen") is not None for row in samples),
        "gaze_valid_count": sum(row.get("gaze_valid") is True for row in samples),
        "pretrained_gaze_valid_count": sum(row.get("pretrained_gaze_valid") is True for row in samples),
        "model_delta_count": sum(row.get("raw_model_angle_delta_deg") is not None for row in samples),
        "pretrained_gaze_preflight": header.get("pretrained_gaze_preflight"),
        "screen_coordinates_claimed": False,
        "human_data": False,
        "raw_frames": False,
    }
