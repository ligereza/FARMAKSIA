"""Add a declared objective signal to the CODE-INE transition boundary."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
CASES = HERE / "cases.json"
SOURCE_SESSION = ROOT / "experiments" / "022-vizz-codeine-long-bridge" / "session.json"
BRIDGE = ROOT / "experiments" / "020-vizz-codeine-event-bridge" / "run_experiment.py"
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
    session = json.loads(SOURCE_SESSION.read_text(encoding="utf-8"))
    if cases.get("schema") != "farmaxia:codeine-objective-signal-cases:0.1":
        raise ValueError("wrong objective signal cases schema")
    return cases, session


def transition_summary(transition: dict[str, Any]) -> dict[str, Any]:
    return {
        "last_significant_improvement": transition["last_significant_improvement"],
        "repetition_entry": transition["repetition_entry"],
        "tail_event_ids": transition["tail_event_ids"],
    }


def validate_scores(scores: dict[str, Any] | None, event_ids: list[str]) -> tuple[bool, str | None]:
    if scores is None:
        return False, "objective_signal_missing"
    if set(scores) != set(event_ids):
        return False, "objective_signal_incomplete"
    if any(not isinstance(value, (int, float)) or not 0 <= value <= 1 for value in scores.values()):
        raise ValueError("objective score must be between zero and one")
    return True, None


def derive_objective_state(
    scores: dict[str, float],
    events: list[dict[str, Any]],
    anchor_id: str,
    tolerance: float,
) -> dict[str, Any]:
    anchor_score = float(scores[anchor_id])
    tail = events[[event["event_id"] for event in events].index(anchor_id) + 1 :]
    declines = [event for event in tail if scores[event["event_id"]] < anchor_score - tolerance]
    if not declines:
        drift = "stable"
    elif scores[tail[-1]["event_id"]] >= anchor_score - tolerance:
        drift = "recovered"
    else:
        drift = "regressed"
    return {
        "signal_status": "available",
        "anchor_event": anchor_id,
        "anchor_score": anchor_score,
        "minimum_tail_score": min(scores[event["event_id"]] for event in tail),
        "first_decline_event": None if not declines else declines[0]["event_id"],
        "tolerance": tolerance,
        "drift": drift,
    }


def evaluate_profile(
    profile: dict[str, Any],
    normalized: list[dict[str, Any]],
    baseline_transition: dict[str, Any],
    anchor_id: str,
    tolerance: float,
) -> dict[str, Any]:
    scores = profile["objective_scores"]
    classification = "available"
    reason = None
    objective_state: dict[str, Any] | None = None
    try:
        valid, reason = validate_scores(scores, [event["event_id"] for event in normalized])
        if not valid:
            classification = "unavailable"
        else:
            objective_state = derive_objective_state(scores, normalized, anchor_id, tolerance)
    except ValueError as exc:
        classification = "rejected"
        reason = str(exc)
    return {
        "id": profile["id"],
        "classification": classification,
        "reason": reason,
        "base_transition": baseline_transition,
        "objective_state": objective_state,
        "objective_signal_declared": scores is not None,
        "human_data": False,
        "pharmacological_inference": False,
    }


def main() -> None:
    cases, session = load_documents()
    bridge = load_module(BRIDGE, "bridge_026")
    codeine = load_module(CODEINE, "codeine_026")
    normalized, dropped = bridge.normalize_events(session)
    codeine.validate_events(normalized)
    baseline_transition = transition_summary(codeine.derive_transition(normalized))
    results = [
        evaluate_profile(
            profile,
            normalized,
            baseline_transition,
            baseline_transition["last_significant_improvement"],
            cases["drift_tolerance"],
        )
        for profile in cases["profiles"]
    ]
    by_id = {result["id"]: result for result in results}
    expected = {profile["id"]: (profile["expected_classification"], profile["expected_drift"]) for profile in cases["profiles"]}
    all_expected = all(
        (
            by_id[item]["classification"],
            "unavailable" if by_id[item]["objective_state"] is None and by_id[item]["classification"] == "unavailable" else
            "rejected" if by_id[item]["classification"] == "rejected" else
            by_id[item]["objective_state"]["drift"],
        ) == expected[item]
        for item in expected
    )
    counts = {name: sum(result["classification"] == name for result in results) for name in ("available", "unavailable", "rejected")}
    drift_values = [
        result["objective_state"]["drift"]
        if result["objective_state"] is not None
        else result["classification"]
        for result in results
    ]
    drift_counts = {name: drift_values.count(name) for name in ("stable", "regressed", "recovered", "unavailable", "rejected")}
    print(
        json.dumps(
            {
                "experiment": "026-codeine-objective-signal",
                "source_experiment": "022-vizz-codeine-long-bridge",
                "case_count": len(results),
                "classification_counts": counts,
                "drift_status_counts": drift_counts,
                "all_expected_classifications": all_expected,
                "baseline_transition": baseline_transition,
                "dropped_vizz_fields": dropped,
                "cases": results,
                "human_data": False,
                "devices_started": False,
                "network_used": False,
                "raw_capture": False,
                "pharmacological_inference": False,
                "neurochemical_inference": False,
                "scope_limit": "declared objective signal and synthetic transition; no human state or neurotransmitter claim",
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
