"""Measure a minimal CODE-INE session-state transition without human data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


TRACE = Path(__file__).with_name("trace.json")
SIGNIFICANT_GAIN = 0.2


def validate_events(events: list[dict[str, Any]]) -> None:
    if not events or [event["t_ms"] for event in events] != sorted(event["t_ms"] for event in events):
        raise ValueError("trace is empty or not chronological")
    if len({event["event_id"] for event in events}) != len(events):
        raise ValueError("trace has duplicate event ids")
    for event in events:
        if set(event) != {"event_id", "t_ms", "action_class", "gain", "errors"}:
            raise ValueError("trace event fields are not closed")
        if not isinstance(event["t_ms"], int) or event["t_ms"] < 0:
            raise ValueError("event time is invalid")
        if not isinstance(event["action_class"], str) or not event["action_class"]:
            raise ValueError("action class is invalid")
        if not 0 <= event["gain"] <= 1 or not isinstance(event["errors"], int) or event["errors"] < 0:
            raise ValueError("gain or errors are invalid")


def derive_transition(events: list[dict[str, Any]]) -> dict[str, Any]:
    significant = [event for event in events if event["gain"] >= SIGNIFICANT_GAIN]
    anchor = significant[-1] if significant else None
    tail = [event for event in events if anchor and event["t_ms"] > anchor["t_ms"]]
    seen: set[str] = set()
    repetition_ids: list[str] = []
    for event in tail:
        action_class = event["action_class"]
        if action_class in seen:
            repetition_ids.append(event["event_id"])
        seen.add(action_class)
    return {
        "activity_event_count": len(events),
        "improvement_event_ids": [event["event_id"] for event in significant],
        "last_significant_improvement": None if anchor is None else anchor["event_id"],
        "tail_event_ids": [event["event_id"] for event in tail],
        "tail_gain": round(sum(event["gain"] for event in tail), 3),
        "tail_errors": sum(event["errors"] for event in tail),
        "repetition_event_ids": repetition_ids,
        "repetition_entry": repetition_ids[0] if repetition_ids else None,
        "repetition_available": bool(repetition_ids),
        "drift": "unavailable_without_objective_signal",
    }


def activity_only_view(events: list[dict[str, Any]]) -> dict[str, Any]:
    significant = [event for event in events if event["gain"] >= SIGNIFICANT_GAIN]
    anchor_time = significant[-1]["t_ms"] if significant else None
    tail = [event for event in events if anchor_time is not None and event["t_ms"] > anchor_time]
    return {
        "fields": ["t_ms", "gain", "errors"],
        "low_gain_tail_proxy": bool(tail) and sum(event["gain"] for event in tail) < SIGNIFICANT_GAIN,
        "repetition_entry": "unavailable_without_action_class",
        "drift": "unavailable_without_objective_signal",
    }


def main() -> None:
    document = json.loads(TRACE.read_text(encoding="utf-8"))
    if document.get("schema") != "farmaxia:codeine-session-trace:0.1":
        raise SystemExit("CODEINE_INVALID: wrong trace schema")
    events = document["events"]
    try:
        validate_events(events)
    except ValueError as exc:
        raise SystemExit(f"CODEINE_INVALID: {exc}") from exc
    transition = derive_transition(events)
    print(
        json.dumps(
            {
                "experiment": "016-codeine-session-state",
                "objective": document["objective"],
                "event_count": len(events),
                "transition": transition,
                "activity_only_view": activity_only_view(events),
                "human_data": False,
                "pharmacological_inference": False,
                "scope_limit": "synthetic task-event trace; state availability only, not human state or drug effect",
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
