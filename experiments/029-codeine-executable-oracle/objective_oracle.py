"""Independent executable acceptance oracle for the CODE-INE fixture."""

from __future__ import annotations

from typing import Any


def evaluate_events(events: list[dict[str, Any]], spec: dict[str, Any]) -> dict[str, Any]:
    required_ids = spec["required_event_ids"]
    event_ids = [event.get("event_id") for event in events]
    if event_ids != required_ids:
        return {
            "validation": "incomplete",
            "reason": "required event ids are missing or reordered",
            "acceptance": {},
            "anchor_accepted": None,
            "drift": None,
        }
    required_fields = {"event_id", "action_class", "gain", "errors"}
    if any(set(event) != required_fields for event in events):
        return {
            "validation": "rejected",
            "reason": "event fields do not match the executable specification",
            "acceptance": {},
            "anchor_accepted": None,
            "drift": None,
        }
    if any(not isinstance(event["gain"], (int, float)) or isinstance(event["gain"], bool) for event in events):
        return {
            "validation": "rejected",
            "reason": "event gain is not numeric",
            "acceptance": {},
            "anchor_accepted": None,
            "drift": None,
        }
    if any(not isinstance(event["errors"], int) or isinstance(event["errors"], bool) for event in events):
        return {
            "validation": "rejected",
            "reason": "event errors is not an integer",
            "acceptance": {},
            "anchor_accepted": None,
            "drift": None,
        }

    anchor_id = spec["anchor_event_id"]
    anchor = next(event for event in events if event["event_id"] == anchor_id)
    anchor_rule = spec["anchor"]
    anchor_accepted = (
        anchor["action_class"] == anchor_rule["action_class"]
        and anchor["gain"] >= anchor_rule["min_gain"]
        and anchor["errors"] <= anchor_rule["max_errors"]
    )
    if not anchor_accepted:
        return {
            "validation": "rejected",
            "reason": "anchor does not satisfy executable acceptance rule",
            "acceptance": {event["event_id"]: False for event in events},
            "anchor_accepted": False,
            "drift": None,
        }

    anchor_index = event_ids.index(anchor_id)
    tail = events[anchor_index + 1 :]
    tail_rule = spec["tail"]
    acceptance = {event["event_id"]: False for event in events[:anchor_index]}
    acceptance[anchor_id] = True
    for event in tail:
        acceptance[event["event_id"]] = (
            event["action_class"] in tail_rule["allowed_action_classes"]
            and event["errors"] <= tail_rule["max_errors"]
        )
    declines = [event for event in tail if not acceptance[event["event_id"]]]
    if not declines:
        drift = "stable"
    elif acceptance[tail[-1]["event_id"]]:
        drift = "recovered"
    else:
        drift = "regressed"
    return {
        "validation": "complete",
        "reason": None,
        "acceptance": acceptance,
        "anchor_accepted": True,
        "drift": drift,
    }
