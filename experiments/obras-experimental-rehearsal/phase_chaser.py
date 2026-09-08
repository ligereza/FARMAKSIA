"""Pure PhaseChaser equivalent used by the Obras rehearsal experiment."""

from __future__ import annotations

from datetime import datetime
import math
from typing import Any, Iterable, Mapping, Sequence


SCHEMA = "farmaxia:phase-chaser-state:0.1"
CHECKPOINT_SCHEMA = "farmaxia:phase-chaser-checkpoint:0.1"


class PhaseChaserError(ValueError):
    """Raised when a choreography state cannot be advanced safely."""


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PhaseChaserError(f"{field_name} must be non-empty text")
    value = value.strip()
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise PhaseChaserError(f"{field_name} must be ASCII") from exc
    return value


def _finite(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PhaseChaserError(f"{field_name} must be finite")
    result = float(value)
    if not math.isfinite(result):
        raise PhaseChaserError(f"{field_name} must be finite")
    return result


def _timestamp(value: Any) -> str:
    text = _text(value, "timestamp")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PhaseChaserError("timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise PhaseChaserError("timestamp must include a timezone")
    return text


def _bounded(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


class PhaseChaser:
    """Coordinate a rotating phase field over a configurable fixture count."""

    def __init__(
        self,
        fixture_ids: Sequence[str],
        *,
        cycle_seconds: float = 2.4,
        base_angle_degrees: float = 0.0,
    ) -> None:
        if not isinstance(fixture_ids, Sequence) or isinstance(fixture_ids, (str, bytes)) or not fixture_ids:
            raise PhaseChaserError("fixture_ids must be a non-empty sequence")
        normalized_ids = tuple(_text(item, "fixture_id") for item in fixture_ids)
        if len(set(normalized_ids)) != len(normalized_ids):
            raise PhaseChaserError("fixture_ids must be unique")
        if len(normalized_ids) > 64:
            raise PhaseChaserError("fixture count exceeds rehearsal limit")
        cycle_seconds = _finite(cycle_seconds, "cycle_seconds")
        base_angle_degrees = _finite(base_angle_degrees, "base_angle_degrees")
        if cycle_seconds <= 0:
            raise PhaseChaserError("cycle_seconds must be > 0")
        self.fixture_ids = normalized_ids
        self.cycle_seconds = cycle_seconds
        self.base_angle_degrees = base_angle_degrees % 360.0
        self.last_sequence = 0
        self.last_event_id: str | None = None
        self.last_timestamp: str | None = None

    def process(self, event: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(event, Mapping):
            raise PhaseChaserError("event must be an object")
        sequence = event.get("sequence")
        if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence <= self.last_sequence:
            raise PhaseChaserError("PhaseChaser sequence must increase strictly")
        event_id = _text(event.get("event_id"), "event_id")
        timestamp = _timestamp(event.get("timestamp"))
        time_seconds = _finite(event.get("time_seconds"), "time_seconds")
        timecode = _text(event.get("timecode"), "timecode")
        payload = event.get("payload")
        if not isinstance(payload, Mapping):
            raise PhaseChaserError("event payload must be an object")
        amplitude = _bounded(_finite(payload.get("amplitude", 0.0), "payload.amplitude"))
        pulse = _bounded(_finite(payload.get("pulse", 0.0), "payload.pulse"))
        signal_state = _text(payload.get("signal_state", "present"), "signal_state")
        if signal_state not in {"present", "missing"}:
            raise PhaseChaserError("unsupported signal_state")

        base_phase = (time_seconds / self.cycle_seconds) % 1.0
        lights: list[dict[str, Any]] = []
        for index, fixture_id in enumerate(self.fixture_ids):
            phase = (base_phase + (index / len(self.fixture_ids))) % 1.0
            angle = (self.base_angle_degrees + phase * 360.0) % 360.0
            wave = 0.5 + 0.5 * math.sin(phase * math.tau)
            intensity = 0.0 if signal_state == "missing" else _bounded(amplitude * (0.35 + 0.65 * wave) + pulse * 0.08)
            lights.append(
                {
                    "fixture_id": fixture_id,
                    "angle_degrees": round(angle, 6),
                    "phase": round(phase, 6),
                    "intensity": round(intensity, 6),
                    "pulse": round(0.0 if signal_state == "missing" else pulse, 6),
                }
            )
        state = {
            "schema": SCHEMA,
            "sequence": sequence,
            "event_id": event_id,
            "timestamp": timestamp,
            "time_seconds": round(time_seconds, 6),
            "timecode": timecode,
            "signal_state": signal_state,
            "source_event_type": _text(event.get("event_type"), "event_type"),
            "lights": lights,
        }
        self.last_sequence = sequence
        self.last_event_id = event_id
        self.last_timestamp = timestamp
        return state

    def process_all(self, events: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return [self.process(event) for event in events]

    def checkpoint(self) -> dict[str, Any]:
        return {
            "schema": CHECKPOINT_SCHEMA,
            "fixture_ids": list(self.fixture_ids),
            "cycle_seconds": round(self.cycle_seconds, 6),
            "base_angle_degrees": round(self.base_angle_degrees, 6),
            "last_sequence": self.last_sequence,
            "last_event_id": self.last_event_id,
            "last_timestamp": self.last_timestamp,
        }

    @classmethod
    def from_checkpoint(cls, checkpoint: Mapping[str, Any]) -> "PhaseChaser":
        if not isinstance(checkpoint, Mapping) or checkpoint.get("schema") != CHECKPOINT_SCHEMA:
            raise PhaseChaserError("invalid PhaseChaser checkpoint")
        chaser = cls(
            checkpoint.get("fixture_ids", []),
            cycle_seconds=checkpoint.get("cycle_seconds", 2.4),
            base_angle_degrees=checkpoint.get("base_angle_degrees", 0.0),
        )
        last_sequence = checkpoint.get("last_sequence", 0)
        if isinstance(last_sequence, bool) or not isinstance(last_sequence, int) or last_sequence < 0:
            raise PhaseChaserError("checkpoint last_sequence is invalid")
        chaser.last_sequence = last_sequence
        if checkpoint.get("last_event_id") is not None:
            chaser.last_event_id = _text(checkpoint["last_event_id"], "last_event_id")
        if checkpoint.get("last_timestamp") is not None:
            chaser.last_timestamp = _timestamp(checkpoint["last_timestamp"])
        return chaser


__all__ = ["CHECKPOINT_SCHEMA", "SCHEMA", "PhaseChaser", "PhaseChaserError"]
