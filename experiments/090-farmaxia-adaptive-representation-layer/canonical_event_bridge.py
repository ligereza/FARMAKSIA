"""Bridge canonical application events into metadata-only VIZZ/PUPILA input."""

from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any, Mapping

from contracts import normalize_context, normalize_signal
from pupila_adapter import PupilaAdapter
from vizz_adapter import VizzAdapter


class CanonicalEventError(ValueError):
    """Raised when an external event cannot cross the VIZZ/PUPILA boundary."""


_REQUIRED_FIELDS = frozenset(
    {
        "event_id",
        "schema_version",
        "source_app",
        "event_type",
        "channel",
        "payload",
        "source_timestamp",
        "received_timestamp",
        "session_id",
        "peer_id",
        "sequence",
        "raw_hash",
        "provenance",
    }
)
_TECHNICAL_ID = re.compile(r"^[A-Za-z0-9_.:-]+$")
_INTERACTION_CHANNELS = {
    "pointer": "pointer",
    "mouse": "pointer",
    "keyboard": "keyboard",
    "key": "keyboard",
    "focus": "focus",
    "gaze": "gaze",
}


def _technical_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CanonicalEventError(f"{field_name} must be non-empty ASCII text.")
    text = value.strip()
    try:
        text.encode("ascii")
    except UnicodeEncodeError as exc:
        raise CanonicalEventError(f"{field_name} must contain ASCII characters only.") from exc
    return text


def _technical_id(value: Any, field_name: str) -> str:
    text = _technical_text(value, field_name)
    if not _TECHNICAL_ID.fullmatch(text):
        raise CanonicalEventError(f"{field_name} contains unsupported technical characters.")
    return text


def _timestamp(value: Any, field_name: str) -> datetime:
    text = _technical_text(value, field_name)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CanonicalEventError(f"{field_name} is not valid ISO-8601.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CanonicalEventError(f"{field_name} must include a timezone.")
    return parsed.astimezone(timezone.utc)


def _validate_event(raw_event: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw_event, Mapping):
        raise CanonicalEventError("canonical event must be an object.")
    missing = sorted(_REQUIRED_FIELDS - set(raw_event))
    if missing:
        raise CanonicalEventError(f"canonical event missing fields: {missing}.")
    event = dict(raw_event)
    for field_name in (
        "event_id",
        "source_app",
        "event_type",
        "channel",
        "session_id",
        "peer_id",
        "raw_hash",
    ):
        event[field_name] = _technical_text(event[field_name], field_name)
    event["event_id"] = _technical_id(event["event_id"], "event_id")
    event["session_id"] = _technical_id(event["session_id"], "session_id")
    event["peer_id"] = _technical_id(event["peer_id"], "peer_id")
    event["source_timestamp"] = _timestamp(event["source_timestamp"], "source_timestamp")
    event["received_timestamp"] = _timestamp(event["received_timestamp"], "received_timestamp")
    version = event["schema_version"]
    sequence = event["sequence"]
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise CanonicalEventError("schema_version must be a positive integer.")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        raise CanonicalEventError("sequence must be a positive integer.")
    if not isinstance(event["payload"], Mapping):
        raise CanonicalEventError("payload must be an object.")
    if not isinstance(event["provenance"], Mapping):
        raise CanonicalEventError("provenance must be an object.")
    return event


def _signal_kind(event: Mapping[str, Any]) -> str:
    event_type = str(event["event_type"]).lower()
    channel = str(event["channel"]).lower()
    if event_type == "connectivity.status":
        return "presence"
    for candidate, kind in _INTERACTION_CHANNELS.items():
        if channel == candidate or event_type.startswith(candidate + "."):
            return kind
    return "task"


def _signal_value(kind: str, event: Mapping[str, Any]) -> dict[str, Any]:
    payload = event["payload"]
    if not isinstance(payload, Mapping):
        return {}
    if kind == "presence":
        state = payload.get("state")
        return {"state": state if isinstance(state, str) else "unknown"}
    if kind == "pointer":
        return {"x": payload.get("x"), "y": payload.get("y")}
    if kind == "gaze":
        return {"x": payload.get("x"), "y": payload.get("y"), "quality": payload.get("quality")}
    if kind == "keyboard":
        shortcut = payload.get("shortcut", "")
        if not isinstance(shortcut, str):
            shortcut = ""
        try:
            shortcut.encode("ascii")
        except UnicodeEncodeError:
            shortcut = ""
        return {"count": payload.get("count", 1), "shortcut": shortcut[:80]}
    if kind == "focus":
        return {"focused": bool(payload.get("focused"))}
    return {"step": str(event["event_type"])[:120], "progress": payload.get("progress", 0.0)}


def _context(raw_context: Mapping[str, Any] | None, event: Mapping[str, Any]) -> dict[str, Any]:
    supplied = dict(raw_context or {})
    supplied_session = supplied.get("sessionId")
    if supplied_session is not None and str(supplied_session) != event["session_id"]:
        raise CanonicalEventError("context sessionId does not match event session_id.")
    supplied["sessionId"] = event["session_id"]
    supplied["participantRef"] = event["peer_id"]
    return normalize_context(supplied)


def _lineage(event: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "sourceEventId": event["event_id"],
        "sourceApp": event["source_app"],
        "eventType": event["event_type"],
        "channel": event["channel"],
        "sequence": event["sequence"],
        "sourceTimestamp": event["source_timestamp"].isoformat(),
        "receivedTimestamp": event["received_timestamp"].isoformat(),
        "rawHash": event["raw_hash"],
        "provenance": dict(event["provenance"]),
    }


class CanonicalEventBridge:
    """Convert app-independent events into consented VIZZ/PUPILA metadata."""

    def __init__(self, vizz: VizzAdapter | None = None, pupila: PupilaAdapter | None = None) -> None:
        self._vizz = vizz or VizzAdapter()
        self._pupila = pupila or PupilaAdapter()
        self._seen: dict[tuple[str, str, str], set[str]] = {}

    def ingest(
        self,
        raw_event: Mapping[str, Any],
        raw_context: Mapping[str, Any] | None = None,
        *,
        consent: bool,
    ) -> dict[str, Any]:
        if not isinstance(consent, bool):
            raise CanonicalEventError("consent must be boolean.")
        event = _validate_event(raw_event)
        context = _context(raw_context, event)
        key = (context["sessionId"], event["peer_id"], context["surfaceId"])
        seen = self._seen.setdefault(key, set())
        if event["event_id"] in seen:
            vizz_state = self._vizz.state(context, event["peer_id"])
            pupila_state = self._pupila.snapshot(context)
            return {
                "status": "duplicate",
                "eventId": event["event_id"],
                "vizzState": vizz_state,
                "pupilaState": pupila_state,
                "lineage": _lineage(event),
            }

        kind = _signal_kind(event)
        at_ms = int(event["source_timestamp"].timestamp() * 1000)
        signal = normalize_signal(
            {
                "sessionId": context["sessionId"],
                "roomId": context["roomId"],
                "surfaceId": context["surfaceId"],
                "participantRef": event["peer_id"],
                "kind": kind,
                "atMs": at_ms,
                "value": _signal_value(kind, event),
                "consent": consent,
            }
        )
        vizz_state = self._vizz.ingest(context, signal)
        pupila_state = self._pupila.ingest(context, vizz_state)
        if signal["accepted"]:
            seen.add(event["event_id"])
        return {
            "status": "accepted" if signal["accepted"] else "blocked",
            "eventId": event["event_id"],
            "signal": signal,
            "vizzState": vizz_state,
            "pupilaState": pupila_state,
            "lineage": _lineage(event),
        }


class CanonicalEventReplay:
    """Replay canonical events into one in-memory VIZZ/PUPILA bridge."""

    def __init__(self, bridge: CanonicalEventBridge | None = None) -> None:
        self.bridge = bridge or CanonicalEventBridge()

    def run(
        self,
        events: Any,
        raw_context: Mapping[str, Any] | None = None,
        *,
        consent: bool,
    ) -> dict[str, Any]:
        if isinstance(events, (str, bytes, Mapping)):
            raise CanonicalEventError("replay events must be an iterable of event objects.")
        try:
            iterator = iter(events)
        except TypeError as exc:
            raise CanonicalEventError("replay events must be iterable.") from exc

        results: list[dict[str, Any]] = []
        for raw_event in iterator:
            results.append(self.bridge.ingest(raw_event, raw_context, consent=consent))

        counts = {"accepted": 0, "blocked": 0, "duplicate": 0}
        for result in results:
            status = result["status"]
            if status in counts:
                counts[status] += 1
        final = results[-1] if results else None
        return {
            "status": "complete",
            "eventCount": len(results),
            "acceptedCount": counts["accepted"],
            "blockedCount": counts["blocked"],
            "duplicateCount": counts["duplicate"],
            "results": results,
            "finalVizzState": final["vizzState"] if final else None,
            "finalPupilaState": final["pupilaState"] if final else None,
        }


__all__ = ["CanonicalEventBridge", "CanonicalEventError", "CanonicalEventReplay"]
