"""Independent oracle for the CODE-INE experience-compiler fixture."""

from __future__ import annotations

from typing import Any


EXPECTED = {
    ("ready", "start"): "working",
    ("working", "failure"): "blocked",
    ("blocked", "retry_allowed"): "retrying",
    ("retrying", "success"): "verified",
    ("blocked", "retry_exhausted"): "halted",
}


def evaluate(initial_state: str, events: list[str]) -> dict[str, Any]:
    state = initial_state
    states = [state]
    transitions: list[dict[str, str]] = []
    for event in events:
        target = EXPECTED.get((state, event))
        if target is None:
            return {
                "validation": "unavailable",
                "reason": f"no independent oracle rule for {state}:{event}",
                "states": states,
                "transitions": transitions,
            }
        transitions.append({"from": state, "event": event, "to": target})
        state = target
        states.append(state)
    return {
        "validation": "verified",
        "reason": "independent state transition rules accepted the trace",
        "states": states,
        "transitions": transitions,
        "final_state": state,
    }
