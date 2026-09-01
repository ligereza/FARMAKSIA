"""Small, deterministic contracts adapted from the extracted ZIGO core.

The module intentionally stores interaction metadata, not screen frames,
keystroke text, credentials or raw gaze/video samples.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any


SCHEMA_VERSION = 1
ALLOWED_SIGNAL_KINDS = {"pointer", "keyboard", "focus", "gaze", "task", "presence"}
OPAQUE_REF = re.compile(r"^[A-Za-z0-9._:-]{1,120}$")


def stable(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: stable(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [stable(item) for item in value]
    return value


def stable_json(value: Any) -> str:
    return json.dumps(stable(value), ensure_ascii=True, separators=(",", ":"), allow_nan=False)


def sha256(value: Any) -> str:
    payload = value if isinstance(value, str) else stable_json(value)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def deterministic_id(prefix: str, value: Any) -> str:
    return f"{prefix}-{sha256(value)[7:23]}"


def clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return low
    return max(low, min(high, number)) if math.isfinite(number) else low


def _opaque(value: Any, fallback: str) -> str:
    candidate = str(value or fallback).strip()
    return candidate if OPAQUE_REF.fullmatch(candidate) else fallback


def _number(value: Any, fallback: float | None = None) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    return number if math.isfinite(number) else fallback


def normalize_context(raw: dict[str, Any] | None = None) -> dict[str, Any]:
    """Normalize host context without requiring a specific application."""

    source = raw if isinstance(raw, dict) else {}
    unknown = dict(source.get("unknown") or {})
    viewport = source.get("viewport") if isinstance(source.get("viewport"), dict) else {}
    context = {
        "schemaVersion": SCHEMA_VERSION,
        "contextId": _opaque(source.get("contextId"), "context-unknown"),
        "sessionId": _opaque(source.get("sessionId"), "session-unknown"),
        "roomId": _opaque(source.get("roomId"), "room-local"),
        "surfaceId": _opaque(source.get("surfaceId"), "surface-unknown"),
        "host": str(source.get("host") or "unknown")[:80],
        "task": str(source.get("task") or "unspecified")[:240],
        "viewport": {
            "width": _number(viewport.get("width")),
            "height": _number(viewport.get("height")),
            "unit": str(viewport.get("unit") or "px")[:16],
        },
        "capabilities": sorted({str(item)[:80] for item in source.get("capabilities", []) if item}),
        "unknown": unknown,
        "privacy": {
            "mode": "metadata-only",
            "raw_frames": False,
            "raw_keystrokes": False,
            "credentials": False,
        },
    }
    context["contextHash"] = sha256({key: value for key, value in context.items() if key != "contextHash"})
    return context


def _sanitize_value(kind: str, raw: Any) -> dict[str, Any]:
    """Keep only bounded, non-content signal features."""

    source = raw if isinstance(raw, dict) else {}
    if kind == "pointer":
        return {"x": clamp(source.get("x")), "y": clamp(source.get("y"))}
    if kind == "gaze":
        return {
            "x": clamp(source.get("x")),
            "y": clamp(source.get("y")),
            "quality": clamp(source.get("quality")),
        }
    if kind == "keyboard":
        shortcut = str(source.get("shortcut") or "")[:80]
        return {"count": max(1, min(20, int(_number(source.get("count"), 1) or 1))), "shortcut": shortcut}
    if kind == "focus":
        return {"focused": bool(source.get("focused"))}
    if kind == "task":
        return {"step": str(source.get("step") or "")[:120], "progress": clamp(source.get("progress"))}
    if kind == "presence":
        return {"state": str(source.get("state") or "present")[:32]}
    return {}


def normalize_signal(raw: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create an auditable signal envelope; consent is required per event."""

    source = raw if isinstance(raw, dict) else {}
    kind = str(source.get("kind") or "").strip().lower()
    session_id = _opaque(source.get("sessionId"), "session-unknown")
    participant_ref = _opaque(source.get("participantRef"), "participant-local")
    surface_id = _opaque(source.get("surfaceId"), "surface-unknown")
    base = {
        "schemaVersion": SCHEMA_VERSION,
        "sessionId": session_id,
        "roomId": _opaque(source.get("roomId"), "room-local"),
        "participantRef": participant_ref,
        "surfaceId": surface_id,
        "kind": kind if kind in ALLOWED_SIGNAL_KINDS else "unknown",
        "atMs": int(_number(source.get("atMs"), 0) or 0),
        "consent": source.get("consent") is True,
        "privacy": {"rawPersisted": False, "contentPersisted": False},
    }
    if not base["consent"]:
        base.update({"accepted": False, "status": "blocked", "reason": "consent-required", "value": {}})
    elif kind not in ALLOWED_SIGNAL_KINDS:
        base.update({"accepted": False, "status": "blocked", "reason": "unsupported-signal-kind", "value": {}})
    else:
        base.update({"accepted": True, "status": "accepted", "value": _sanitize_value(kind, source.get("value"))})
    base["eventId"] = deterministic_id("signal", {key: value for key, value in base.items() if key != "eventId"})
    return base


def append_audit_event(events: list[dict[str, Any]], event_type: str, payload: dict[str, Any], timestamp: int | None = None) -> dict[str, Any]:
    sequence = len(events)
    previous_hash = events[-1]["eventHash"] if events else None
    unsigned = {
        "schemaVersion": SCHEMA_VERSION,
        "sequence": sequence,
        "eventId": deterministic_id("event", {"sequence": sequence, "type": event_type, "payload": payload, "previousHash": previous_hash}),
        "type": str(event_type),
        "payload": stable(payload),
        "timestamp": timestamp,
        "previousHash": previous_hash,
    }
    event = {**unsigned, "eventHash": sha256(unsigned)}
    events.append(event)
    return event


def verify_audit_chain(events: list[dict[str, Any]]) -> dict[str, Any]:
    previous_hash = None
    for sequence, event in enumerate(events):
        if event.get("sequence") != sequence or event.get("previousHash") != previous_hash:
            return {"valid": False, "sequence": sequence, "reason": "sequence-or-link-mismatch"}
        unsigned = {key: value for key, value in event.items() if key != "eventHash"}
        if event.get("eventHash") != sha256(unsigned):
            return {"valid": False, "sequence": sequence, "reason": "hash-mismatch"}
        previous_hash = event["eventHash"]
    return {"valid": True, "count": len(events), "head": previous_hash}
