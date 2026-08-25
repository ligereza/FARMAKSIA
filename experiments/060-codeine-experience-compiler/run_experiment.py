"""Compile a declared intention into a verified CODE-INE experience plan.

The experiment is deterministic and local. It does not launch applications,
execute generated source, use a camera or infer a human mental state. The
"sensation" layer is a bounded representation policy: focus, disclosure,
tempo, motion and reversible controls.
"""

from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.json"
ORACLE_PATH = HERE / "objective_oracle.py"
ALLOWED_RELATIONS = {"equivalent", "analogous", "different", "unknown"}
ALLOWED_PROFILES = {"guided", "technical", "fast", "quiet"}
ALLOWED_TEMPO = {"deliberate", "normal", "fast"}
ALLOWED_DENSITY = {"compact", "balanced", "full"}
ALLOWED_MOTION = {"reduced", "trace", "full"}


def load_oracle() -> Any:
    spec = importlib.util.spec_from_file_location("codeine_060_oracle", ORACLE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load independent oracle")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_fixture(fixture: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    intent = fixture.get("intent", {})
    task = fixture.get("task", {})
    analogy = fixture.get("analogy", {})
    preferences = intent.get("declared_preferences", {})
    budget = intent.get("complexity_budget", {})
    if intent.get("entry_profile") not in ALLOWED_PROFILES:
        blockers.append("invalid_entry_profile")
    if preferences.get("tempo") not in ALLOWED_TEMPO:
        blockers.append("invalid_declared_tempo")
    if preferences.get("density") not in ALLOWED_DENSITY:
        blockers.append("invalid_declared_density")
    if preferences.get("motion") not in ALLOWED_MOTION:
        blockers.append("invalid_declared_motion")
    if budget.get("max_active_concepts", 0) < 1:
        blockers.append("invalid_complexity_budget")
    if budget.get("max_disclosure_layers", 0) < 1:
        blockers.append("invalid_disclosure_budget")

    states = task.get("states", [])
    if not task.get("initial_state") or task["initial_state"] not in states:
        blockers.append("invalid_initial_state")
    if not task.get("trace"):
        blockers.append("missing_task_trace")
    if len(task.get("expected_states", [])) != len(task.get("trace", [])) + 1:
        blockers.append("expected_state_trace_length_mismatch")

    source_ids = {item.get("id") for item in analogy.get("source_concepts", [])}
    target_ids = {item.get("id") for item in analogy.get("target_concepts", [])}
    for mapping in analogy.get("mappings", []):
        if mapping.get("source") not in source_ids:
            blockers.append(f"unknown_source_concept:{mapping.get('source')}")
        if mapping.get("target") not in target_ids:
            blockers.append(f"unknown_target_concept:{mapping.get('target')}")
        if mapping.get("relation") not in ALLOWED_RELATIONS:
            blockers.append(f"invalid_relation:{mapping.get('relation')}")
        if mapping.get("relation") != "equivalent" and not mapping.get("residue"):
            blockers.append(f"missing_residue:{mapping.get('source')}:{mapping.get('target')}")
    return blockers


def compile_semantic_map(fixture: dict[str, Any]) -> dict[str, Any]:
    mappings = []
    residue = []
    for mapping in fixture["analogy"]["mappings"]:
        item = {
            "source": mapping["source"],
            "target": mapping["target"],
            "relation": mapping["relation"],
            "preserves": list(mapping.get("preserves", [])),
            "residue": list(mapping.get("residue", [])),
        }
        mappings.append(item)
        if item["relation"] != "equivalent":
            residue.append(
                {
                    "source": item["source"],
                    "target": item["target"],
                    "relation": item["relation"],
                    "why_not_equivalent": item["residue"],
                }
            )
    return {
        "kind": "contrastive_semantic_map",
        "mappings": mappings,
        "residue": residue,
        "unknown_count": sum(item["relation"] == "unknown" for item in mappings),
    }


def compile_machine(fixture: dict[str, Any]) -> dict[str, Any]:
    task = fixture["task"]
    transition_table: dict[str, dict[str, dict[str, str]]] = {}
    for transition in task["transitions"]:
        transition_table.setdefault(transition["from"], {})[transition["event"]] = {
            "to": transition["to"],
            "observable": transition["observable"],
            "postcondition": transition["postcondition"],
            "id": transition["id"],
        }
    code_outline = [
        "state = initial_state",
        "for event in declared_events:",
        "    transition = transition_table[state][event]",
        "    emit(transition.observable)",
        "    state = transition.to",
        "return state",
    ]
    return {
        "artifact_kind": "declarative_state_machine",
        "initial_state": task["initial_state"],
        "states": list(task["states"]),
        "transition_table": transition_table,
        "code_outline": code_outline,
        "execution_policy": "dry_run_only",
    }


def simulate(machine: dict[str, Any], events: list[str]) -> dict[str, Any]:
    state = machine["initial_state"]
    states = [state]
    observations: list[str] = []
    for event in events:
        transition = machine["transition_table"].get(state, {}).get(event)
        if transition is None:
            return {
                "status": "UNAVAILABLE",
                "reason": f"no compiled transition for {state}:{event}",
                "states": states,
                "observations": observations,
            }
        observations.append(transition["observable"])
        state = transition["to"]
        states.append(state)
    return {"status": "SIMULATED", "states": states, "observations": observations, "final_state": state}


def compile_representation_plan(fixture: dict[str, Any], simulation: dict[str, Any]) -> dict[str, Any]:
    intent = fixture["intent"]
    prefs = intent["declared_preferences"]
    profile = intent["entry_profile"]
    if profile == "technical":
        layers = ["signal", "structure", "detail"]
    elif profile == "fast":
        layers = ["signal", "structure"]
    else:
        layers = ["signal", "structure"]
    if profile == "quiet":
        layers = ["signal"]
    state_count = max(1, len(simulation.get("states", [])) - 1)
    active_concepts = min(intent["complexity_budget"]["max_active_concepts"], 2)
    return {
        "kind": "representation_plan",
        "focus": "active_transition",
        "entry_profile": profile,
        "disclosure_layers": layers[: intent["complexity_budget"]["max_disclosure_layers"]],
        "active_concepts_limit": active_concepts,
        "semantic_tokens": {
            "relation": "shared_shape_and_label",
            "analogy": "paired_source_target",
            "residue": "visible_boundary",
            "unknown": "explicit_unavailable",
            "verified": "stable_anchor",
        },
        "tempo_policy": prefs["tempo"],
        "motion_policy": prefs["motion"],
        "intensity_policy": {
            "basis": "state_and_uncertainty",
            "max_attention_weight": 0.72,
            "periodic_flashing": False,
            "no_physiological_claim": True,
        },
        "friction_policy": {
            "source": "declared_interaction_only",
            "on_stuck": "pause_preserve_context_show_one_next_action",
            "never_infer": ["intoxication", "diagnosis", "neurochemistry", "emotion"],
        },
        "controls": ["preview", "accept", "revert", "reduce_motion", "show_full"],
        "state_count": state_count,
        "reversible": True,
        "camera": False,
        "network": False,
    }


def validate_representation_plan(plan: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not plan.get("reversible"):
        blockers.append("representation_not_reversible")
    if not set(["preview", "accept", "revert"]).issubset(plan.get("controls", [])):
        blockers.append("missing_user_control")
    if plan.get("intensity_policy", {}).get("periodic_flashing"):
        blockers.append("periodic_flashing_not_allowed")
    if plan.get("intensity_policy", {}).get("max_attention_weight", 1) > 0.72:
        blockers.append("attention_weight_exceeds_cap")
    if plan.get("friction_policy", {}).get("source") != "declared_interaction_only":
        blockers.append("implicit_friction_inference")
    return blockers


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    blockers = validate_fixture(fixture)
    if blockers:
        return {"status": "BLOCKED", "blockers": blockers}
    machine = compile_machine(fixture)
    simulation = simulate(machine, fixture["task"]["trace"])
    oracle = load_oracle()
    oracle_result = oracle.evaluate(fixture["task"]["initial_state"], fixture["task"]["trace"])
    plan = compile_representation_plan(fixture, simulation)
    plan_blockers = validate_representation_plan(plan)
    if simulation["status"] != "SIMULATED":
        blockers.append("compiled_machine_unavailable")
    if oracle_result["validation"] != "verified":
        blockers.append("independent_oracle_unavailable")
    if simulation.get("states") != oracle_result.get("states"):
        blockers.append("compiled_machine_oracle_conflict")
    if plan_blockers:
        blockers.extend(plan_blockers)
    status = "COMPILED_VERIFIED_WITH_RESIDUE" if not blockers else "BLOCKED"
    semantic_map = compile_semantic_map(fixture)
    return {
        "status": status,
        "blockers": blockers,
        "intent": fixture["intent"],
        "semantic_map": semantic_map,
        "machine": machine,
        "simulation": simulation,
        "oracle": oracle_result,
        "representation_plan": plan,
        "execution_allowed": False,
        "human_data": False,
        "camera_used": False,
        "network_used": False,
        "arbitrary_code_executed": False,
        "physiological_inference": False,
        "scope_limit": "declarative compilation and synthetic trace verification; no human comprehension claim",
    }


def main() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    result = compile_fixture(fixture)
    result["experiment"] = "060-codeine-experience-compiler"
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
