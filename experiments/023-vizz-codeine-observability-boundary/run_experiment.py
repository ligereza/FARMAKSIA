"""Audit structural rejection and semantic ambiguity at the VIZZ-CODE-INE bridge."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
CASES = HERE / "cases.json"
SOURCE_SESSION = ROOT / "experiments" / "022-vizz-codeine-long-bridge" / "session.json"
VIZZ_VALIDATOR = ROOT / "experiments" / "015-vizz-session-contract" / "run_experiment.py"
BRIDGE = ROOT / "experiments" / "020-vizz-codeine-event-bridge" / "run_experiment.py"
CODEINE = ROOT / "experiments" / "016-codeine-session-state" / "run_experiment.py"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_case_spec() -> dict[str, Any]:
    document = json.loads(CASES.read_text(encoding="utf-8"))
    if document.get("schema") != "farmaxia:vizz-codeine-observability-cases:0.1":
        raise ValueError("wrong observability cases schema")
    return document


def mutate(session: dict[str, Any], mutation: str) -> dict[str, Any]:
    damaged = copy.deepcopy(session)
    events = damaged["events"]
    by_id = {event["event_id"]: event for event in events}
    if mutation == "none":
        return damaged
    if mutation == "drop_action_class":
        by_id["c07"]["payload"].pop("action_class")
        return damaged
    if mutation == "set_c07_time_backwards":
        by_id["c07"]["t_ms"] = by_id["c06"]["t_ms"] - 1
        return damaged
    if mutation == "duplicate_c07_id":
        by_id["c08"]["event_id"] = "c07"
        return damaged
    if mutation == "remove_c04":
        damaged["events"] = [event for event in events if event["event_id"] != "c04"]
        return damaged
    if mutation == "lower_c04_gain":
        by_id["c04"]["payload"]["gain"] = 0.19
        return damaged
    if mutation == "relabel_c07_as_build":
        by_id["c07"]["payload"]["action_class"] = "build"
        return damaged
    raise ValueError(f"unknown mutation: {mutation}")


def evaluate_case(
    case: dict[str, Any],
    source: dict[str, Any],
    vizz: Any,
    bridge: Any,
    codeine: Any,
    baseline_transition: dict[str, Any] | None,
) -> dict[str, Any]:
    session = mutate(source, case["mutation"])
    vizz_valid = False
    bridge_valid = False
    try:
        vizz.validate_session(session)
        vizz_valid = True
        normalized, dropped = bridge.normalize_events(session)
        bridge_valid = True
        codeine.validate_events(normalized)
        transition = codeine.derive_transition(normalized)
    except (KeyError, TypeError, ValueError) as exc:
        return {
            "id": case["id"],
            "mutation": case["mutation"],
            "classification": "rejected",
            "vizz_valid": vizz_valid,
            "bridge_valid": bridge_valid,
            "reason": str(exc),
            "transition": None,
        }

    if baseline_transition is None:
        classification = "available"
    else:
        classification = "available" if transition == baseline_transition else "ambiguous"
    return {
        "id": case["id"],
        "mutation": case["mutation"],
        "classification": classification,
        "vizz_valid": vizz_valid,
        "bridge_valid": bridge_valid,
        "dropped_vizz_fields": dropped,
        "reason": None,
        "transition": transition,
    }


def main() -> None:
    spec = load_case_spec()
    source = json.loads(SOURCE_SESSION.read_text(encoding="utf-8"))
    vizz = load_module(VIZZ_VALIDATOR, "vizz_contract_023")
    bridge = load_module(BRIDGE, "bridge_023")
    codeine = load_module(CODEINE, "codeine_023")
    cases = spec["cases"]
    baseline_case = next(case for case in cases if case["mutation"] == "none")
    baseline_result = evaluate_case(baseline_case, source, vizz, bridge, codeine, None)
    if baseline_result["transition"] is None:
        raise SystemExit("OBSERVABILITY_INVALID: baseline did not produce a transition")
    baseline_transition = baseline_result["transition"]
    results = [baseline_result]
    for case in cases:
        if case is baseline_case:
            continue
        results.append(evaluate_case(case, source, vizz, bridge, codeine, baseline_transition))
    by_id = {result["id"]: result for result in results}
    expected = {case["id"]: case["expected_classification"] for case in cases}
    all_expected = all(by_id[item]["classification"] == expected[item] for item in expected)
    counts = {name: sum(result["classification"] == name for result in results) for name in ("available", "rejected", "ambiguous")}
    print(
        json.dumps(
            {
                "experiment": "023-vizz-codeine-observability-boundary",
                "source_experiment": "022-vizz-codeine-long-bridge",
                "case_count": len(results),
                "classification_counts": counts,
                "all_expected_classifications": all_expected,
                "baseline_transition": baseline_transition,
                "cases": results,
                "human_data": False,
                "devices_started": False,
                "network_used": False,
                "raw_capture": False,
                "pharmacological_inference": False,
                "scope_limit": "synthetic structural and semantic observability boundary; no human state claim",
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
