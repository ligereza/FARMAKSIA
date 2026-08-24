"""Evaluate a VIZZ decision query against several information exposures."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE_TRACE = ROOT / "experiments" / "013-vizz-perceptual-adaptation" / "trace.json"
SIGNIFICANT_GAIN = 0.2


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def focus_events(events: list[dict[str, Any]], focus_time: int, focus_window: int) -> list[dict[str, Any]]:
    return [event for event in events if abs(event["t"] - focus_time) <= focus_window]


def aggregate(events: list[dict[str, Any]], bins: int = 5) -> list[dict[str, Any]]:
    maximum = max(event["t"] for event in events)
    width = maximum / bins
    groups = []
    for index in range(bins):
        lower = index * width
        upper = maximum if index == bins - 1 else (index + 1) * width
        subset = [
            event
            for event in events
            if lower <= event["t"] <= upper and (index == bins - 1 or event["t"] < upper)
        ]
        groups.append(
            {
                "bin": index,
                "start": round(lower, 2),
                "end": round(upper, 2),
                "activity": len(subset),
                "gain": round(sum(event["gain"] for event in subset), 3),
                "errors": sum(event["errors"] for event in subset),
            }
        )
    return groups


def oracle(events: list[dict[str, Any]]) -> dict[str, Any]:
    significant = [event for event in events if event["gain"] >= SIGNIFICANT_GAIN]
    anchor = significant[-1]
    tail = [event for event in events if event["t"] > anchor["t"]]
    return {
        "significant_gain_threshold": SIGNIFICANT_GAIN,
        "anchor_event": anchor["id"],
        "tail_event_ids": [event["id"] for event in tail],
        "tail_gain": round(sum(event["gain"] for event in tail), 3),
        "tail_errors": sum(event["errors"] for event in tail),
        "low_gain_tail": bool(tail) and sum(event["gain"] for event in tail) < SIGNIFICANT_GAIN,
    }


def decision_for_events(
    events: list[dict[str, Any]],
    expected: dict[str, Any],
    fields: set[str],
    representation: str,
    *,
    aggregate_view: bool = False,
) -> dict[str, Any]:
    visible_ids = set() if aggregate_view else {event["id"] for event in events}
    anchor_visible = expected["anchor_event"] in visible_ids
    complete_tail = set(expected["tail_event_ids"]).issubset(visible_ids)
    has_required_values = {"t", "gain", "errors"}.issubset(fields)
    global_available = anchor_visible and complete_tail and has_required_values and not aggregate_view
    proxy_signal = (
        any(event["gain"] < SIGNIFICANT_GAIN and event["errors"] > 0 for event in events)
        if not aggregate_view
        else any(unit["gain"] < SIGNIFICANT_GAIN and unit["errors"] > 0 for unit in events)
    )
    return {
        "representation": representation,
        "visible_units": len(events),
        "visible_event_ids": sorted(visible_ids) if not aggregate_view else [],
        "fields": sorted(fields),
        "anchor_visible": anchor_visible,
        "complete_tail_visible": complete_tail,
        "global_tail_available": global_available,
        "proxy_repetition_signal": proxy_signal,
        "residue": {
            "missing_anchor": not anchor_visible,
            "missing_tail_events": sorted(set(expected["tail_event_ids"]) - visible_ids),
            "exact_action": "action" not in fields,
            "global_order": aggregate_view,
        },
    }


def evaluate(events: list[dict[str, Any]], trace: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    focused = focus_events(events, trace["focus_time"], trace["focus_window"])
    representations = [
        decision_for_events(
            events,
            expected,
            {"t", "phase", "action", "gain", "errors", "detail"},
            "text",
        ),
        decision_for_events(
            events,
            expected,
            {"t", "phase", "gain", "errors"},
            "timeline",
        ),
        decision_for_events(
            focused,
            expected,
            {"t", "phase", "action", "gain", "errors", "detail"},
            "focus",
        ),
        decision_for_events(
            aggregate(events),
            expected,
            {"time_bins", "activity", "gain", "errors"},
            "field",
            aggregate_view=True,
        ),
    ]
    sensitivity = []
    for window in (4, 8, 16):
        window_events = focus_events(events, trace["focus_time"], window)
        sensitivity.append(
            decision_for_events(
                window_events,
                expected,
                {"t", "phase", "action", "gain", "errors", "detail"},
                f"focus:{window}m",
            )
        )
    return {
        "experiment": "014-vizz-decision-query",
        "source_experiment": "013-vizz-perceptual-adaptation",
        "source_trace_sha256": sha256(SOURCE_TRACE),
        "event_count": len(events),
        "objective": "determine whether an exposure makes the global repetition-tail decision available",
        "decision_query": "detect entry into repetition after the last significant improvement",
        "oracle": expected,
        "representations": representations,
        "focus_window_sensitivity": sensitivity,
        "human_data": False,
        "scope_limit": "synthetic trace; decision availability only, not human detection, comfort, or efficacy",
    }


def main() -> None:
    trace = json.loads(SOURCE_TRACE.read_text(encoding="utf-8"))
    events = trace["events"]
    times = [event["t"] for event in events]
    if times != sorted(times):
        raise SystemExit("VIZZ_INVALID: source trace is not chronological")
    if len({event["id"] for event in events}) != len(events):
        raise SystemExit("VIZZ_INVALID: duplicate event id")
    if not any(event["gain"] >= SIGNIFICANT_GAIN for event in events):
        raise SystemExit("VIZZ_INVALID: trace has no significant improvement anchor")
    print(json.dumps(evaluate(events, trace, oracle(events)), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
