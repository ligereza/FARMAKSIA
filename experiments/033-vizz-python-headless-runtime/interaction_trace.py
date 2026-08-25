"""Opt-in, no-video trace of gaze diagnostics and OS mouse position."""

from __future__ import annotations

import ctypes
import json
import math
from pathlib import Path
from typing import Any


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def read_pointer_position() -> tuple[int, int] | None:
    point = POINT()
    if not ctypes.windll.user32.GetCursorPos(ctypes.byref(point)):
        return None
    return int(point.x), int(point.y)


def _finite_vector(value: Any, length: int) -> list[float] | None:
    if value is None:
        return None
    values = [float(item) for item in value]
    if len(values) != length or not all(math.isfinite(item) for item in values):
        return None
    return values


class InteractionTrace:
    """Append timestamp-aligned summaries; never writes pixels or screen content."""

    def __init__(self, path: Path, screen_size: tuple[int, int], sample_hz: float = 20.0) -> None:
        if sample_hz <= 0.0 or not math.isfinite(sample_hz):
            raise ValueError("trace sample_hz must be finite and positive")
        self.path = path
        self.sample_hz = float(sample_hz)
        self._stream = path.open("w", encoding="utf-8")
        self._count = 0
        self._write(
            {
                "schema": "farmaxia:vizz-interaction-trace:0.2",
                "type": "header",
                "sample_hz": self.sample_hz,
                "screen_size": list(screen_size),
                "pointer_space": "os_cursor_pixels",
                "raw_video": False,
                "screen_content": False,
                "mouse_is_ground_truth": False,
                "pretrained_gaze_model": "github:yakhyo/gaze-estimation:mobileone_s0_gaze.onnx",
                "pretrained_gaze_preflight": "cuda_zero_tensor",
            }
        )

    def _write(self, payload: dict[str, Any]) -> None:
        self._stream.write(json.dumps(payload, separators=(",", ":")) + "\n")
        self._stream.flush()

    def write_sample(
        self,
        timestamp: float,
        sample: Any | None,
        gaze_screen: tuple[float, float] | None,
        pointer: tuple[int, int] | None,
    ) -> None:
        if not math.isfinite(timestamp):
            raise ValueError("trace timestamp must be finite")
        payload: dict[str, Any] = {
            "type": "sample",
            "t_monotonic": float(timestamp),
            "mouse_screen": list(pointer) if pointer is not None else None,
            "gaze_screen": _finite_vector(gaze_screen, 2),
            "gaze_valid": False,
            "quality": None,
            "disagreement_deg": None,
            "legacy_features": None,
            "eye_centric": None,
            "eye_centric_distance_px": None,
            "eye_centric_roll_rad": None,
            "pose": None,
            "pretrained_gaze_deg": None,
            "pretrained_gaze_valid": False,
            "pretrained_gaze_unknown_reason": None,
            "binocular_gaze_deg": None,
            "raw_model_angle_delta_deg": None,
        }
        if sample is not None:
            payload["quality"] = float(sample.quality) if math.isfinite(float(sample.quality)) else None
            payload["disagreement_deg"] = (
                float(sample.disagreement_deg) if math.isfinite(float(sample.disagreement_deg)) else None
            )
            payload["legacy_features"] = _finite_vector(getattr(sample, "features", None), 6)
            payload["eye_centric"] = _finite_vector(getattr(sample, "eye_centric", None), 6)
            payload["pose"] = _finite_vector(getattr(sample, "pose", None), 6)
            payload["pretrained_gaze_deg"] = _finite_vector(getattr(sample, "pretrained_gaze_deg", None), 2)
            payload["pretrained_gaze_valid"] = payload["pretrained_gaze_deg"] is not None
            payload["pretrained_gaze_unknown_reason"] = getattr(sample, "pretrained_gaze_unknown_reason", None)
            payload["binocular_gaze_deg"] = _finite_vector(getattr(sample, "binocular_gaze_deg", None), 2)
            delta = getattr(sample, "raw_model_angle_delta_deg", None)
            if delta is not None and math.isfinite(float(delta)) and float(delta) >= 0.0:
                payload["raw_model_angle_delta_deg"] = float(delta)
            distance = getattr(sample, "eye_centric_distance_px", None)
            if distance is not None and math.isfinite(float(distance)) and float(distance) > 0.0:
                payload["eye_centric_distance_px"] = float(distance)
            roll = getattr(sample, "eye_centric_roll_rad", None)
            if roll is not None and math.isfinite(float(roll)):
                payload["eye_centric_roll_rad"] = float(roll)
        payload["gaze_valid"] = payload["gaze_screen"] is not None and payload["quality"] is not None
        self._write(payload)
        self._count += 1

    def close(self) -> None:
        if self._stream.closed:
            return
        self._write({"type": "footer", "sample_count": self._count, "raw_video": False})
        self._stream.close()
