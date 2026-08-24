"""Compare declared CODE-INE objective scores with a separate synthetic oracle."""

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
    if cases.get("schema") != "farmaxia:codeine-objective-oracle-cases:0.1":
        raise ValueError("wrong objective oracle cases schema")
    return cases, session


def transition_summary(transition: dict[str, Any]) -> dict[str, Any]:
    return {
        "last_significant_improvement": transition["last_significant_improvement"],
        "repetition_entry": transition["repetition_entry"],
        "tail_event_ids": transition["tail_event_ids"],
    }


def validate_scores(scores: dict[str, Any], event_ids: list[str]) -> None:
    if set(scores) != set(event_ids):
        raise ValueError("objective score signal is incomplete")
    if any(not isinstance(value, (int, float)) or not 0 <= value <= 1 for value in scores.values()):
        raise ValueError("objective score must be between zero and one")


def validate_oracle(oracle: dict[str, Any] | None, event_ids: list[str]) -> str:
    if oracle is None:
        return "missing"
    if set(oracle) != set(event_ids):
        return "incomplete"
    if any(type(value) is not bool for value in oracle.values()):
        raise ValueError("oracle values must be boolean")
    return "complete"


def score_drift(scores: dict[str, float], events: list[dict[str, Any]], anchor_id: str, tolerance: float) -> str:
    anchor_score = float(scores[anchor_id])
    anchor_index = [event["event_id"] for event in events].index(anchor_id)
    tail = events[anchor_index + 1 :]
    declines = [event for event in tail if scores[event["event_id"]] < anchor_score - tolerance]
    if not declines:
        return "stable"
    return "recovered" if scores[tail[-1]["event_id"]] >= anchor_score - tolerance else "regressed"


def oracle_drift(oracle: dict[str, bool], events: list[dict[str, Any]], anchor_id: str) -> str:
    anchor_index = [event["event_id"] for event in events].index(anchor_id)
    tail = events[anchor_index + 1 :]
    if not oracle[anchor_id]:
        raise ValueError("oracle anchor must be accepted")
    declines = [event for event in tail if not oracle[event["event_id"]]]
    if not declines:
        return "stable"
    return "recovered" if oracle[tail[-1]["event_id"]] else "regressed"


def evaluate_profile(
    profile: dict[str, Any],
    normalized: list[dict[str, Any]],
    baseline_transition: dict[str, Any],
    anchor_id: str,
    tolerance: float,
) -> dict[str, Any]:
    event_ids = [event["event_id"] for event in normalized]
    status = "verified"
    reason = None
    declared_drift: str | None = None
    oracle_result: str | None = None
    verified_drift: str | None = None
    try:
        validate_scores(profile["objective_scores"], event_ids)
        declared_drift = score_drift(profile["objective_scores"], normalized, anchor_id, tolerance)
        oracle_result = validate_oracle(profile["oracle"], event_ids)
        if oracle_result == "missing":
            status = "declared_only"
        elif oracle_result == "incomplete":
            status = "unavailable"
        else:
            oracle_value = oracle_drift(profile["oracle"], normalized, anchor_id)
            if oracle_value != declared_drift:
                status = "conflict"
            else:
                verified_drift = oracle_value
    except ValueError as exc:
        status = "rejected"
        reason = str(exc)
    return {
        "id": profile["id"],
        "evidence_status": status,
        "reason": reason,
        "declared_drift": declared_drift,
        "oracle_validation": oracle_result,
        "verified_drift": verified_drift,
        "base_transition": baseline_transition,
        "human_data": False,
        "pharmacological_inference": False,
        "neurochemical_inference": False,
    }


def main() -> None:
    cases, session = load_documents()
    bridge = load_module(BRIDGE, "bridge_027")
    codeine = load_module(CODEINE, "codeine_027")
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
    expected = {
        profile["id"]: (profile["expected_evidence_status"], profile["expected_verified_drift"])
        for profile in cases["profiles"]
    }
    all_expected = all(
        (by_id[item]["evidence_status"], by_id[item]["verified_drift"]) == expected[item]
        for item in expected
    )
    counts = {name: sum(result["evidence_status"] == name for result in results) for name in ("verified", "declared_only", "conflict", "unavailable", "rejected")}
    print(
        json.dumps(
            {
                "experiment": "027-codeine-objective-oracle",
                "source_experiment": "022-vizz-codeine-long-bridge",
                "case_count": len(results),
                "evidence_status_counts": counts,
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
                "scope_limit": "synthetic score/oracle comparison; separated fixture evidence, no human state claim",
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
