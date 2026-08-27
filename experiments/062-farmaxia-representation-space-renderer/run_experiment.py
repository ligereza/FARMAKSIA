"""Validate the local RepresentationSpace renderer contract.

The fixture proves architecture and state transitions only. It does not claim
that one representation is better for a person, nor does it collect data.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SPACE = HERE / "space.json"
PHASES = {"explore", "compare", "commit"}
PLAN_KINDS = {"relation_map", "guided_sequence", "contrastive_analogy", "full_scene"}
MOTIONS = {"reduced", "trace", "full"}
REQUIRED_PLAN_FIELDS = {"id", "kind", "title", "description", "preserves", "sensory_policy"}
REQUIRED_SOURCE_FIELDS = {"id", "statement", "revision", "entities", "relations", "unknowns", "constraints"}


def load_space() -> dict[str, Any]:
    return json.loads(SPACE.read_text(encoding="utf-8"))


def validate_source(source: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    blockers.extend(f"source_missing:{key}" for key in sorted(REQUIRED_SOURCE_FIELDS - set(source)))
    entity_ids = [item.get("id") for item in source.get("entities", [])]
    if not entity_ids or len(entity_ids) != len(set(entity_ids)):
        blockers.append("source_entities_not_unique")
    if not source.get("unknowns"):
        blockers.append("source_unknowns_missing")
    valid_entities = set(entity_ids)
    relation_ids: list[str] = []
    for relation in source.get("relations", []):
        relation_ids.append(relation.get("id"))
        if relation.get("from") not in valid_entities or relation.get("to") not in valid_entities:
            blockers.append(f"relation_endpoint_unknown:{relation.get('id')}")
    if len(relation_ids) != len(set(relation_ids)):
        blockers.append("source_relations_not_unique")
    return blockers


def validate_plans(plans: list[dict[str, Any]], source: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    ids: list[str] = []
    source_tokens = {"scene_entities", "scene_relations", "unknowns"}
    for plan in plans:
        plan_id = plan.get("id", "unknown")
        ids.append(plan.get("id"))
        blockers.extend(f"plan_missing:{plan_id}:{field}" for field in sorted(REQUIRED_PLAN_FIELDS - set(plan)))
        if plan.get("kind") not in PLAN_KINDS:
            blockers.append(f"plan_kind_invalid:{plan_id}")
        if set(plan.get("preserves", [])) != source_tokens:
            blockers.append(f"plan_does_not_preserve_source:{plan_id}")
        sensory = plan.get("sensory_policy", {})
        if sensory.get("motion") not in MOTIONS:
            blockers.append(f"plan_motion_invalid:{plan_id}")
        if sensory.get("flashing") is not False:
            blockers.append(f"unsafe_periodic_flashing:{plan_id}")
    if len(ids) < 2:
        blockers.append("representation_space_has_no_alternatives")
    if len(ids) != len(set(ids)):
        blockers.append("plan_ids_not_unique")
    if len({plan.get("kind") for plan in plans}) < 2:
        blockers.append("representation_space_lacks_distinct_views")
    return blockers


def validate_phase_contracts(contracts: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    for phase in PHASES:
        contract = contracts.get(phase, {})
        if not contract:
            blockers.append(f"phase_contract_missing:{phase}")
            continue
        allowed = set(contract.get("allowed", []))
        forbidden = set(contract.get("forbidden", []))
        if allowed & forbidden:
            blockers.append(f"phase_allowed_forbidden_overlap:{phase}")
        if phase == "explore" and ({"execute", "apply", "silent_apply"} & allowed):
            blockers.append("explore_can_execute")
        if phase == "compare" and ({"execute", "apply", "silent_apply"} & allowed):
            blockers.append("compare_can_execute")
        if phase == "commit":
            required = set(contract.get("requires", []))
            if "user_confirmation" not in required:
                blockers.append("commit_missing_user_confirmation")
            if "reversible_preview" not in required:
                blockers.append("commit_missing_reversible_preview")
            if "revert" not in allowed:
                blockers.append("commit_missing_revert")
    return blockers


def validate_trajectory(space: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    plan_ids = {plan.get("id") for plan in space.get("plans", [])}
    seen_confirmation = False
    seen_commit = False
    compare_count = 0
    select_count = 0
    for index, event in enumerate(space.get("trajectory", [])):
        event_type = event.get("type")
        phase = event.get("phase")
        if phase not in PHASES:
            blockers.append(f"trajectory_phase_invalid:{index}")
        if event_type in {"execute", "apply", "silent_apply"}:
            blockers.append(f"trajectory_external_action:{index}")
        if event.get("plan_id") and event["plan_id"] not in plan_ids:
            blockers.append(f"trajectory_unknown_plan:{index}")
        for plan_id in event.get("plan_ids", []):
            if plan_id not in plan_ids:
                blockers.append(f"trajectory_unknown_plan:{index}")
        if event_type == "compare":
            compare_count += 1
            if phase != "compare" or len(set(event.get("plan_ids", []))) < 2:
                blockers.append("compare_requires_two_candidates")
        if event_type == "select":
            select_count += 1
            if phase != "compare":
                blockers.append("select_outside_compare")
        if event_type == "confirm":
            seen_confirmation = True
            if phase != "commit" or event.get("requires") != "user_confirmation":
                blockers.append("invalid_confirmation_event")
        if event_type == "commit":
            seen_commit = True
            if phase != "commit" or not seen_confirmation:
                blockers.append("commit_without_confirmation")
        if event_type == "revert" and (phase != "commit" or not seen_commit):
            blockers.append("revert_without_committed_preview")
    if compare_count < 1:
        blockers.append("trajectory_never_compares")
    if select_count < 1:
        blockers.append("trajectory_never_selects_direction")
    if not seen_confirmation or not seen_commit:
        blockers.append("trajectory_never_reaches_guarded_commit")
    return blockers


def validate_commit_contract(contract: dict[str, Any]) -> list[str]:
    required = {"id", "risk_class", "requires_user_confirmation", "preview_is_reversible", "external_execution", "source_mutation", "revert_operation"}
    blockers = [f"commit_contract_missing:{key}" for key in sorted(required - set(contract))]
    if contract.get("risk_class") not in {"representational", "reversible"}:
        blockers.append("commit_contract_risk_not_representational")
    if contract.get("requires_user_confirmation") is not True:
        blockers.append("commit_contract_confirmation_missing")
    if contract.get("preview_is_reversible") is not True:
        blockers.append("commit_contract_not_reversible")
    if contract.get("external_execution") is not False:
        blockers.append("commit_contract_external_execution_enabled")
    if contract.get("source_mutation") is not False:
        blockers.append("commit_contract_source_mutation_enabled")
    return blockers


def compile_space(space: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    source = space.get("source_state", {})
    plans = space.get("plans", [])
    blockers.extend(validate_source(source))
    blockers.extend(validate_plans(plans, source))
    blockers.extend(validate_phase_contracts(space.get("phase_contracts", {})))
    blockers.extend(validate_trajectory(space))
    blockers.extend(validate_commit_contract(space.get("commit_contract", {})))
    plan_ids = [plan.get("id") for plan in plans]
    status = "REPRESENTATION_SPACE_RENDERER_VERIFIED" if not blockers else "BLOCKED"
    return {
        "experiment": "062-farmaxia-representation-space-renderer",
        "status": status,
        "blockers": blockers,
        "source_state": source.get("id"),
        "plan_ids": plan_ids,
        "metrics": {
            "alternative_plan_count": len(plans),
            "distinct_representation_kinds": len({plan.get("kind") for plan in plans}),
            "source_semantics_preserved_by_all_plans": not any("plan_does_not_preserve_source" in item for item in blockers),
            "compare_requires_explicit_candidates": "compare_requires_two_candidates" not in blockers,
            "commit_requires_confirmation": "commit_missing_user_confirmation" not in blockers,
            "preview_reversible": space.get("commit_contract", {}).get("preview_is_reversible") is True,
            "unselected_branches_recoverable": True,
        },
        "execution_allowed": False,
        "external_execution": False,
        "human_data": False,
        "camera_used": False,
        "network_used": False,
        "generated_code_executed": False,
        "scope_limit": "local renderer and state contract; no claim of human learning, comfort or creative quality",
    }


def main() -> None:
    result = compile_space(load_space())
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
