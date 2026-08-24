"""Compare CODE-INE scores with an executable acceptance oracle under mutations."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
CASES = HERE / "cases.json"
SPEC = HERE / "oracle_spec.json"
ORACLE = HERE / "objective_oracle.py"
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


def load_documents() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    oracle_spec = json.loads(SPEC.read_text(encoding="utf-8"))
    session = json.loads(SOURCE_SESSION.read_text(encoding="utf-8"))
    if cases.get("schema") != "farmaxia:codeine-executable-oracle-cases:0.1":
        raise ValueError("wrong executable oracle cases schema")
    if oracle_spec.get("schema") != "farmaxia:codeine-executable-oracle-spec:0.1":
        raise ValueError("wrong executable oracle spec schema")
    return cases, oracle_spec, session


def transition_summary(transition: dict[str, Any]) -> dict[str, Any]:
    return {
        "last_significant_improvement": transition["last_significant_improvement"],
        "repetition_entry": transition["repetition_entry"],
        "tail_event_ids": transition["tail_event_ids"],
    }


def oracle_projection(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Project the bridge envelope into the executable oracle contract."""
    return [
        {
            "event_id": event["event_id"],
            "action_class": event["action_class"],
            "gain": event["gain"],
            "errors": event["errors"],
        }
        for event in events
    ]


def validate_scores(scores: dict[str, Any], event_ids: list[str]) -> None:
    if set(scores) != set(event_ids):
        raise ValueError("objective score signal is incomplete")
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1 for value in scores.values()):
        raise ValueError("objective score must be between zero and one")


def score_drift(scores: dict[str, float], events: list[dict[str, Any]], anchor_id: str, tolerance: float) -> str:
    event_ids = [event["event_id"] for event in events]
    anchor_index = event_ids.index(anchor_id)
    anchor_score = float(scores[anchor_id])
    tail = events[anchor_index + 1 :]
    declines = [event for event in tail if scores[event["event_id"]] < anchor_score - tolerance]
    if not declines:
        return "stable"
    return "recovered" if scores[tail[-1]["event_id"]] >= anchor_score - tolerance else "regressed"


def mutate_events(events: list[dict[str, Any]], mutation: str) -> list[dict[str, Any]]:
    mutated = copy.deepcopy(events)
    by_id = {event["event_id"]: event for event in mutated}
    if mutation == "none":
        return mutated
    if mutation == "tail_failure_sustained":
        for event_id in ("c06", "c07", "c08"):
            by_id[event_id]["errors"] = 2
        return mutated
    if mutation == "tail_failure_then_recover":
        by_id["c06"]["errors"] = 2
        return mutated
    if mutation == "wrong_tail_action":
        by_id["c07"]["action_class"] = "build"
        return mutated
    if mutation == "remove_repetition_event":
        return [event for event in mutated if event["event_id"] != "c07"]
    if mutation == "anchor_gain_low":
        by_id["c04"]["gain"] = 0.19
        return mutated
    raise ValueError(f"unknown mutation: {mutation}")


def rejected_oracle(reason: str) -> dict[str, Any]:
    return {"validation": "rejected", "reason": reason, "acceptance": {}, "anchor_accepted": None, "drift": None}


def evaluate_profile(profile: dict[str, Any], source_events: list[dict[str, Any]], oracle_spec: dict[str, Any], oracle: Any, tolerance: float) -> dict[str, Any]:
    event_ids = [event["event_id"] for event in source_events]
    declared_drift: str | None = None
    oracle_result: dict[str, Any]
    status = "verified"
    reason = None
    verified_drift: str | None = None
    mutated_events: list[dict[str, Any]] = []
    try:
        validate_scores(profile["objective_scores"], event_ids)
        mutated_events = mutate_events(source_events, profile["mutation"])
        declared_drift = score_drift(profile["objective_scores"], mutated_events, oracle_spec["anchor_event_id"], tolerance)
        oracle_result = oracle.evaluate_events(mutated_events, oracle_spec)
        if oracle_result["validation"] == "incomplete":
            status, reason = "unavailable", oracle_result["reason"]
        elif oracle_result["validation"] == "rejected":
            status, reason = "rejected", oracle_result["reason"]
        elif oracle_result["drift"] != declared_drift:
            status, reason = "conflict", "declared score and executable oracle disagree"
        else:
            verified_drift = oracle_result["drift"]
    except (KeyError, ValueError) as exc:
        status, reason = "rejected", str(exc)
        oracle_result = rejected_oracle(str(exc))
    return {
        "id": profile["id"],
        "mutation": profile["mutation"],
        "evidence_status": status,
        "reason": reason,
        "declared_drift": declared_drift,
        "oracle_validation": oracle_result["validation"],
        "oracle_drift": oracle_result["drift"],
        "verified_drift": verified_drift,
        "oracle_acceptance": oracle_result["acceptance"],
        "mutated_event_ids": [event["event_id"] for event in mutated_events],
        "human_data": False,
        "pharmacological_inference": False,
        "neurochemical_inference": False,
    }


def main() -> None:
    cases, oracle_spec, session = load_documents()
    bridge = load_module(BRIDGE, "bridge_029")
    codeine = load_module(CODEINE, "codeine_029")
    oracle = load_module(ORACLE, "oracle_029")
    normalized, dropped = bridge.normalize_events(session)
    codeine.validate_events(normalized)
    baseline = transition_summary(codeine.derive_transition(normalized))
    oracle_events = oracle_projection(normalized)
    results = [evaluate_profile(profile, oracle_events, oracle_spec, oracle, cases["drift_tolerance"]) for profile in cases["profiles"]]
    by_id = {result["id"]: result for result in results}
    expected = {
        profile["id"]: (profile["expected_evidence_status"], profile["expected_verified_drift"])
        for profile in cases["profiles"]
    }
    all_expected = all((by_id[item]["evidence_status"], by_id[item]["verified_drift"]) == expected[item] for item in expected)
    names = ("verified", "conflict", "unavailable", "rejected")
    counts = {name: sum(result["evidence_status"] == name for result in results) for name in names}
    print(
        json.dumps(
            {
                "experiment": "029-codeine-executable-oracle",
                "source_experiment": "022-vizz-codeine-long-bridge",
                "case_count": len(results),
                "evidence_status_counts": counts,
                "all_expected_classifications": all_expected,
                "baseline_transition": baseline,
                "dropped_vizz_fields": dropped,
                "oracle_implementation": "objective_oracle.py",
                "oracle_reads_objective_scores": False,
                "cases": results,
                "human_data": False,
                "devices_started": False,
                "network_used": False,
                "raw_capture": False,
                "pharmacological_inference": False,
                "neurochemical_inference": False,
                "scope_limit": "synthetic executable task specification and declared-score comparison; no human state claim",
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
