"""Measure synthetic VIZZ coverage under a delayed gaze-contingent renderer."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
CASES = HERE / "cases.json"
TRACE = HERE / "trace.json"
CODEINE = ROOT / "experiments" / "016-codeine-session-state" / "run_experiment.py"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_documents() -> tuple[dict[str, Any], dict[str, Any]]:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    trace = json.loads(TRACE.read_text(encoding="utf-8"))
    if cases.get("schema") != "farmaxia:vizz-latency-coverage-cases:0.1":
        raise ValueError("wrong latency cases schema")
    if trace.get("schema") != "farmaxia:vizz-latency-trace:0.1":
        raise ValueError("wrong latency trace schema")
    return cases, trace


def validate_trace(trace: dict[str, Any]) -> None:
    events = trace["events"]
    samples = trace["gaze_samples"]
    if not events or [item["t_ms"] for item in events] != sorted(item["t_ms"] for item in events):
        raise ValueError("events are empty or not chronological")
    if len({item["event_id"] for item in events}) != len(events):
        raise ValueError("event ids are duplicated")
    if [item["t_ms"] for item in samples] != sorted(item["t_ms"] for item in samples):
        raise ValueError("gaze samples are not chronological")
    if any(not isinstance(item["x"], (int, float)) for item in samples):
        raise ValueError("gaze coordinate is not numeric")


def latest_sample(samples: list[dict[str, Any]], target_time: int) -> dict[str, Any] | None:
    eligible = [sample for sample in samples if sample["t_ms"] <= target_time]
    return eligible[-1] if eligible else None


def codeine_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": event["event_id"],
        "t_ms": event["t_ms"],
        "action_class": event["action_class"],
        "gain": event["gain"],
        "errors": event["errors"],
    }


def baseline_transition(events: list[dict[str, Any]], codeine: Any) -> dict[str, Any]:
    normalized = [codeine_event(event) for event in events]
    codeine.validate_events(normalized)
    return codeine.derive_transition(normalized)


def expose(
    events: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    latency_ms: int,
    focus_radius: int,
) -> tuple[list[dict[str, Any]], list[str], list[dict[str, Any]]]:
    visible: list[dict[str, Any]] = []
    hidden: list[str] = []
    render_trace: list[dict[str, Any]] = []
    for event in events:
        sample = latest_sample(samples, event["t_ms"] - latency_ms)
        is_visible = sample is not None and abs(sample["x"] - event["region_x"]) <= focus_radius
        if is_visible:
            visible.append(event)
        else:
            hidden.append(event["event_id"])
        render_trace.append(
            {
                "event_id": event["event_id"],
                "target_time": event["t_ms"] - latency_ms,
                "render_sample_time": None if sample is None else sample["t_ms"],
                "render_x": None if sample is None else sample["x"],
                "visible": is_visible,
            }
        )
    return visible, hidden, render_trace


def evaluate(
    profile: dict[str, Any],
    events: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    focus_radius: int,
    expected_transition: dict[str, Any],
    codeine: Any,
) -> dict[str, Any]:
    visible, hidden, render_trace = expose(events, samples, profile["latency_ms"], focus_radius)
    complete_coverage = not hidden
    transition = None
    decision_available = False
    if complete_coverage:
        transition = baseline_transition(visible, codeine)
        decision_available = transition == expected_transition
    classification = "available" if decision_available else "unavailable"
    return {
        "id": profile["id"],
        "latency_ms": profile["latency_ms"],
        "focus_radius": focus_radius,
        "classification": classification,
        "complete_coverage": complete_coverage,
        "visible_event_ids": [event["event_id"] for event in visible],
        "hidden_event_ids": hidden,
        "decision_available": decision_available,
        "transition": transition,
        "render_trace": render_trace,
    }


def main() -> None:
    cases, trace = load_documents()
    validate_trace(trace)
    codeine = load_module(CODEINE, "codeine_024")
    events = trace["events"]
    samples = trace["gaze_samples"]
    expected_transition = baseline_transition(events, codeine)
    results = [
        evaluate(profile, events, samples, cases["focus_radius"], expected_transition, codeine)
        for profile in cases["latencies"]
    ]
    by_id = {result["id"]: result for result in results}
    expected = {profile["id"]: profile["expected_classification"] for profile in cases["latencies"]}
    all_expected = all(by_id[item]["classification"] == expected[item] for item in expected)
    counts = {name: sum(result["classification"] == name for result in results) for name in ("available", "unavailable")}
    print(
        json.dumps(
            {
                "experiment": "024-vizz-latency-coverage-boundary",
                "source": "synthetic gaze samples and task events",
                "case_count": len(results),
                "classification_counts": counts,
                "all_expected_classifications": all_expected,
                "baseline_transition": expected_transition,
                "cases": results,
                "human_data": False,
                "devices_started": False,
                "network_used": False,
                "raw_capture": False,
                "pharmacological_inference": False,
                "scope_limit": "synthetic renderer coverage under declared latency; no human visual or gaze claim",
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
