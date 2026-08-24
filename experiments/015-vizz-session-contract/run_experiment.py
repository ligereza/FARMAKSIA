"""Validate the privacy and consent boundary for VIZZ session events."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CASES = Path(__file__).with_name("cases.json")
SESSION_SCHEMA = "farmaxia:vizz-session:0.1"
ALLOWED_KINDS = {"objective", "action", "outcome", "pause", "display_condition"}
ALLOWED_PAYLOAD = {
    "objective_id",
    "phase",
    "action_class",
    "gain",
    "errors",
    "display_condition",
}
ALLOWED_ACTION_CLASSES = {"goal", "search", "build", "test", "verify", "maintain", "pause"}
ALLOWED_PHASES = {"goal", "search", "build", "verify", "maintain", "pause"}
ALLOWED_DISPLAY_CONDITIONS = {"day", "evening", "night"}
FORBIDDEN_KEYS = {
    "audio",
    "camera",
    "coordinates",
    "file",
    "frame",
    "gaze",
    "keyboard",
    "key",
    "microphone",
    "screenshot",
    "screen",
    "text",
    "url",
    "video",
    "webcam",
}


def invalid(message: str) -> None:
    raise ValueError(message)


def validate_session(session: dict[str, Any]) -> int:
    if session.get("schema") != SESSION_SCHEMA:
        invalid("wrong session schema")
    for key in ("consent", "capture", "events"):
        if key not in session:
            invalid(f"missing session key: {key}")
    consent = session["consent"]
    capture = session["capture"]
    events = session["events"]
    if set(consent) != {"granted", "scope", "raw_capture"}:
        invalid("consent fields are not closed")
    if set(capture) != {"enabled", "source"}:
        invalid("capture fields are not closed")
    if not isinstance(consent["granted"], bool) or not isinstance(consent["raw_capture"], bool):
        invalid("consent flags must be boolean")
    if not isinstance(capture["enabled"], bool) or capture["source"] != "manual_event_adapter":
        invalid("capture source or flag is not allowed")
    if not isinstance(events, list) or len(events) > 1000:
        invalid("events must be a bounded list")

    if not capture["enabled"]:
        if consent != {"granted": False, "scope": "none", "raw_capture": False} or events:
            invalid("disabled capture must be empty and unconsented")
    elif consent != {"granted": True, "scope": "task_events_only", "raw_capture": False}:
        invalid("capture requires explicit task-event consent without raw capture")

    seen: set[str] = set()
    previous_time = -1
    for event in events:
        if set(event) != {"event_id", "t_ms", "kind", "payload"}:
            invalid("event fields are not closed")
        event_id = event["event_id"]
        if not isinstance(event_id, str) or not event_id or event_id in seen:
            invalid("event id is empty or duplicated")
        seen.add(event_id)
        if not isinstance(event["t_ms"], int) or event["t_ms"] < 0 or event["t_ms"] < previous_time:
            invalid("event time is not monotonic and non-negative")
        previous_time = event["t_ms"]
        if event["kind"] not in ALLOWED_KINDS or not isinstance(event["payload"], dict):
            invalid("event kind or payload is not allowed")
        payload = event["payload"]
        forbidden = FORBIDDEN_KEYS.intersection(payload)
        if forbidden:
            invalid(f"forbidden payload field: {sorted(forbidden)[0]}")
        if not set(payload).issubset(ALLOWED_PAYLOAD):
            invalid("payload contains an undeclared field")
        if "objective_id" in payload and not isinstance(payload["objective_id"], str):
            invalid("objective_id must be abstract text")
        if "phase" in payload and payload["phase"] not in ALLOWED_PHASES:
            invalid("phase is not allowed")
        if "action_class" in payload and payload["action_class"] not in ALLOWED_ACTION_CLASSES:
            invalid("action class is not allowed")
        if "gain" in payload and (not isinstance(payload["gain"], (int, float)) or not 0 <= payload["gain"] <= 1):
            invalid("gain must be between zero and one")
        if "errors" in payload and (not isinstance(payload["errors"], int) or payload["errors"] < 0):
            invalid("errors must be a non-negative integer")
        if "display_condition" in payload and payload["display_condition"] not in ALLOWED_DISPLAY_CONDITIONS:
            invalid("display condition is not allowed")
    return len(events)


def main() -> None:
    document = json.loads(CASES.read_text(encoding="utf-8"))
    if document.get("schema") != "farmaxia:vizz-session-cases:0.1":
        raise SystemExit("VIZZ_INVALID: wrong cases schema")
    results = []
    for case in document["cases"]:
        try:
            event_count = validate_session(case["session"])
        except ValueError as exc:
            results.append({"case": case["id"], "valid": False, "reason": str(exc)})
        else:
            results.append({"case": case["id"], "valid": True, "event_count": event_count})
    print(
        json.dumps(
            {
                "experiment": "015-vizz-session-contract",
                "cases": results,
                "accepted_cases": sum(item["valid"] for item in results),
                "human_data": False,
                "devices_started": False,
                "network_used": False,
                "raw_capture": False,
                "scope_limit": "synthetic envelope validation only; no session was collected",
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
