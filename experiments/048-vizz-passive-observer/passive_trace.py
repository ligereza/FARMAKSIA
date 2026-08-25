"""Privacy-preserving passive trace adapter for VIZZ state and context."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _finite(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


class PassiveTraceWriter:
    """Write gaze diagnostics and interaction context without content data."""

    def __init__(self, path: Path, layout_version: str, sample_hz: float = 20.0) -> None:
        if not layout_version or not math.isfinite(sample_hz) or sample_hz <= 0.0:
            raise ValueError("passive trace requires layout_version and positive sample_hz")
        self.path = path
        self._stream = path.open("w", encoding="utf-8")
        self._count = 0
        self._write(
            {
                "schema": "farmaxia:vizz-passive-trace:0.1",
                "type": "header",
                "layout_version": layout_version,
                "sample_hz": sample_hz,
                "raw_video": False,
                "screen_content": False,
                "key_values_persisted": False,
                "text_persisted": False,
                "mouse_is_ground_truth": False,
                "active_window_title_persisted": False,
            }
        )

    def _write(self, payload: dict[str, Any]) -> None:
        self._stream.write(json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n")
        self._stream.flush()

    def write_sample(self, timestamp: float, gaze_state: Any, interaction: Any) -> None:
        timestamp_value = _finite(timestamp)
        if timestamp_value is None:
            raise ValueError("timestamp must be finite")
        state = gaze_state.as_dict() if hasattr(gaze_state, "as_dict") else dict(gaze_state or {})
        context = interaction if isinstance(interaction, dict) else vars(interaction)
        keyboard_count = context.get("keyboard_event_count", 0)
        if not isinstance(keyboard_count, int) or keyboard_count < 0:
            raise ValueError("keyboard_event_count must be a non-negative integer")
        mouse = context.get("mouse_screen")
        if mouse is not None:
            if not isinstance(mouse, (tuple, list)) or len(mouse) != 2 or not all(isinstance(v, int) for v in mouse):
                raise ValueError("mouse_screen must be an integer pair")
            mouse = [int(mouse[0]), int(mouse[1])]
        self._write(
            {
                "type": "sample",
                "t_monotonic": timestamp_value,
                "gaze_status": state.get("status", "UNKNOWN"),
                "monitor_id": state.get("monitor_id"),
                "gaze_uv": state.get("uv"),
                "confidence": _finite(state.get("confidence")),
                "uncertainty_deg": _finite(state.get("uncertainty_deg")),
                "safe_radius_deg": _finite(state.get("safe_radius_deg")),
                "fixation_state": state.get("fixation_state"),
                "unknown_reason": state.get("unknown_reason"),
                "candidate_monitor_ids": state.get("candidate_monitor_ids", []),
                "keyboard_event_count": keyboard_count,
                "keyboard_active": bool(context.get("keyboard_active", keyboard_count > 0)),
                "mouse_screen": mouse,
                "mouse_is_ground_truth": False,
            }
        )
        self._count += 1

    def close(self) -> None:
        if self._stream.closed:
            return
        self._write({"type": "footer", "sample_count": self._count, "raw_video": False})
        self._stream.close()


def audit_trace(path: Path) -> dict[str, Any]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) < 2 or rows[0].get("type") != "header" or rows[-1].get("type") != "footer":
        raise ValueError("passive trace must have header and footer")
    samples = [row for row in rows[1:-1] if row.get("type") == "sample"]
    forbidden_tokens = (
        '"key_value":',
        '"vkCode":',
        '"text_value":',
        '"screen_text":',
        '"screenshot":',
        '"frame_bytes":',
        '"video_path":',
        '"window_title":',
    )
    serialized = path.read_text(encoding="utf-8").lower()
    forbidden = [token for token in forbidden_tokens if token.lower() in serialized and token.lower() not in {"video"}]
    if forbidden:
        raise ValueError(f"trace contains forbidden content tokens: {forbidden}")
    if any(row.get("mouse_is_ground_truth") is not False for row in samples):
        raise ValueError("mouse must not be gaze ground truth")
    if any(not isinstance(row.get("keyboard_event_count"), int) for row in samples):
        raise ValueError("keyboard count is not integer-only")
    unknown_counts: dict[str, int] = {}
    monitors: dict[str, int] = {}
    for row in samples:
        if row.get("gaze_status") == "UNKNOWN":
            reason = row.get("unknown_reason") or "unspecified"
            unknown_counts[reason] = unknown_counts.get(reason, 0) + 1
        monitor = row.get("monitor_id")
        if monitor is not None:
            monitors[monitor] = monitors.get(monitor, 0) + 1
    return {
        "schema": "farmaxia:vizz-passive-trace-audit:0.1",
        "sample_count": len(samples),
        "valid_gaze_count": sum(row.get("gaze_status") == "VALID" for row in samples),
        "unknown_counts": unknown_counts,
        "monitor_counts": monitors,
        "keyboard_active_count": sum(row.get("keyboard_active") is True for row in samples),
        "mouse_is_ground_truth": False,
        "raw_video": False,
        "screen_content": False,
        "text_persisted": False,
    }
