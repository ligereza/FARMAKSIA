"""Measure which queries remain available in each VIZZ representation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
TRACE = ROOT / "trace.json"


def focus_events(events: list[dict[str, Any]], focus_time: int, focus_window: int) -> list[dict[str, Any]]:
    return [event for event in events if abs(event["t"] - focus_time) <= focus_window]


def aggregate(events: list[dict[str, Any]], bins: int = 5) -> list[dict[str, Any]]:
    maximum = max(event["t"] for event in events)
    width = maximum / bins
    groups = []
    for index in range(bins):
        lower = index * width
        upper = maximum if index == bins - 1 else (index + 1) * width
        subset = [event for event in events if lower <= event["t"] <= upper and (index == bins - 1 or event["t"] < upper)]
        groups.append({
            "bin": index,
            "start": round(lower, 2),
            "end": round(upper, 2),
            "activity": len(subset),
            "gain": round(sum(event["gain"] for event in subset), 3),
            "errors": sum(event["errors"] for event in subset),
        })
    return groups


def state_signal(events: list[dict[str, Any]]) -> dict[str, Any]:
    significant = [event for event in events if event["gain"] >= 0.2]
    last_significant = significant[-1] if significant else None
    tail = [event for event in events if last_significant is not None and event["t"] > last_significant["t"]]
    return {
        "last_significant_gain_event": None if last_significant is None else last_significant["id"],
        "tail_events_after_last_significant_gain": len(tail),
        "tail_gain": round(sum(event["gain"] for event in tail), 3),
        "tail_errors": sum(event["errors"] for event in tail),
        "low_gain_tail": bool(tail) and sum(event["gain"] for event in tail) < 0.2,
    }


def representation_results(events: list[dict[str, Any]], trace: dict[str, Any]) -> list[dict[str, Any]]:
    focused = focus_events(events, trace["focus_time"], trace["focus_window"])
    definitions = {
        "text": {
            "visible": events,
            "fields": ["t", "phase", "action", "gain", "errors", "detail"],
            "queries": {"exact_action": True, "full_sequence": True, "state_signal": True},
        },
        "timeline": {
            "visible": events,
            "fields": ["t", "phase", "gain", "errors"],
            "queries": {"exact_action": False, "full_sequence": True, "state_signal": True},
        },
        "focus": {
            "visible": focused,
            "fields": ["t", "phase", "action", "gain", "errors", "detail"],
            "queries": {"exact_action": True, "full_sequence": False, "state_signal": len(focused) >= 3},
        },
        "field": {
            "visible": aggregate(events),
            "fields": ["time_bins", "activity", "gain", "errors"],
            "queries": {"exact_action": False, "full_sequence": False, "state_signal": True},
        },
    }
    results = []
    for name, definition in definitions.items():
        visible = definition["visible"]
        results.append({
            "representation": name,
            "visible_units": len(visible),
            "event_coverage": round(len(visible) / len(events), 3) if name != "field" else 1.0,
            "fields": definition["fields"],
            "queries": definition["queries"],
            "state_signal": state_signal(focused if name == "focus" else events) if definition["queries"]["state_signal"] else None,
            "residue": {
                "exact_action": not definition["queries"]["exact_action"],
                "full_sequence": not definition["queries"]["full_sequence"],
                "global_context": name == "focus",
            },
        })
    return results


def main() -> None:
    trace = json.loads(TRACE.read_text(encoding="utf-8"))
    events = trace["events"]
    if [event["t"] for event in events] != sorted(event["t"] for event in events):
        raise SystemExit("VIZZ_INVALID: trace is not chronological")
    if len({event["id"] for event in events}) != len(events):
        raise SystemExit("VIZZ_INVALID: duplicate event id")
    result = {
        "experiment": "013-vizz-perceptual-adaptation",
        "event_count": len(events),
        "objective": trace["objective"],
        "representations": representation_results(events, trace),
        "human_data": False,
        "scope_limit": "synthetic trace; exposure and query availability only, not human comfort or comprehension",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
