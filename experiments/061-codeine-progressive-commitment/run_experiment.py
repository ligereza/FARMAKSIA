"""Test progressive formalization and commitment-aware representation.

This is a local deterministic fixture. It supports open-ended representation
without executing actions, then requires an explicit contract for a final
reversible dry-run. It never collects human data or executes generated code.
"""

from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.json"
ORACLE = HERE / "objective_oracle.py"
MATURITY = {"emergent", "provisional", "committed"}
VERIFIABILITY = {"open", "constrained", "verifiable"}
RISKS = {"representational", "reversible", "consequential"}
REQUIRED_PLAN_FIELDS = {"id", "kind", "description", "preserves", "sensory_policy"}


def load_oracle() -> Any:
    spec = importlib.util.spec_from_file_location("codeine_061_oracle", ORACLE)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load progressive commitment oracle")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pointer_tokens(path: str) -> list[str]:
    if not path.startswith("/"):
        raise ValueError("JSON Patch path must start with /")
    return [token.replace("~1", "/").replace("~0", "~") for token in path[1:].split("/")]


def apply_patch(document: dict[str, Any], operations: list[dict[str, Any]]) -> dict[str, Any]:
    result = deepcopy(document)
    for operation in operations:
        op = operation.get("op")
        tokens = pointer_tokens(operation.get("path", ""))
        if not tokens:
            raise ValueError("root patch is not supported")
        parent: Any = result
        for token in tokens[:-1]:
            if isinstance(parent, list):
                parent = parent[int(token)]
            else:
                if token not in parent:
                    raise KeyError(f"missing patch parent: {token}")
                parent = parent[token]
        key = tokens[-1]
        if isinstance(parent, list):
            if op == "add" and key == "-":
                parent.append(deepcopy(operation["value"]))
            elif op == "add":
                parent.insert(int(key), deepcopy(operation["value"]))
            elif op == "replace":
                parent[int(key)] = deepcopy(operation["value"])
            elif op == "remove":
                del parent[int(key)]
            else:
                raise ValueError(f"unsupported patch operation: {op}")
        else:
            if op in {"add", "replace"}:
                parent[key] = deepcopy(operation["value"])
            elif op == "remove":
                del parent[key]
            else:
                raise ValueError(f"unsupported patch operation: {op}")
    return result


def build_history(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    history = [deepcopy(fixture["base_intent"])]
    for revision in fixture["intent_revisions"]:
        history.append(apply_patch(history[-1], revision["patch"]))
    return history


def validate_history(history: list[dict[str, Any]]) -> list[str]:
    blockers: list[str] = []
    if not history:
        return ["missing_intent_history"]
    for index, intent in enumerate(history, start=1):
        if intent.get("revision") != index:
            blockers.append(f"revision_sequence_conflict:{index}")
        if intent.get("maturity") not in MATURITY:
            blockers.append(f"invalid_maturity:{index}")
        if intent.get("outcome_verifiability") not in VERIFIABILITY:
            blockers.append(f"invalid_verifiability:{index}")
        if intent.get("action_risk") not in RISKS:
            blockers.append(f"invalid_action_risk:{index}")
        if intent.get("provenance") != "user_declared":
            blockers.append(f"missing_intent_provenance:{index}")
    return blockers


def validate_representation_space(plans: list[dict[str, Any]]) -> list[str]:
    blockers: list[str] = []
    ids = set()
    for plan in plans:
        missing = sorted(REQUIRED_PLAN_FIELDS - set(plan))
        blockers.extend(f"plan_missing:{plan.get('id', 'unknown')}:{field}" for field in missing)
        plan_id = plan.get("id")
        if plan_id in ids:
            blockers.append(f"duplicate_plan:{plan_id}")
        ids.add(plan_id)
        sensory = plan.get("sensory_policy", {})
        if sensory.get("motion") not in {"reduced", "trace", "full"}:
            blockers.append(f"invalid_plan_motion:{plan_id}")
        if not plan.get("preserves"):
            blockers.append(f"plan_loses_source:{plan_id}")
    if len(plans) < 2:
        blockers.append("representation_space_has_no_alternatives")
    return blockers


def representation_policy(intent: dict[str, Any]) -> dict[str, Any]:
    maturity = intent["maturity"]
    if maturity == "emergent":
        allowed = ["represent", "suggest", "compare", "branch"]
        focus = "possibility_field"
    elif maturity == "provisional":
        allowed = ["represent", "suggest", "compare", "branch", "preview", "build_draft"]
        focus = "selected_relation"
    else:
        allowed = ["represent", "suggest", "compare", "branch", "preview", "build", "dry_run", "execute_if_authorized", "verify"]
        focus = "action_contract"
    return {
        "maturity": maturity,
        "outcome_verifiability": intent["outcome_verifiability"],
        "action_risk": intent["action_risk"],
        "allowed_operations": allowed,
        "focus": focus,
        "commitment_required_for_execution": True,
        "reversible": True,
        "alternatives_visible": True,
        "unknowns_visible": True,
        "tempo": intent["declared_preferences"]["tempo"],
        "motion": intent["declared_preferences"]["motion"],
        "density": intent["declared_preferences"]["density"],
    }


def validate_trajectory(trajectory: list[dict[str, Any]], plans: list[dict[str, Any]], history: list[dict[str, Any]]) -> list[str]:
    blockers: list[str] = []
    plan_ids = {plan["id"] for plan in plans}
    revision_by_number = {intent["revision"]: intent for intent in history}
    committed_at = next((intent["revision"] for intent in history if intent["maturity"] == "committed"), None)
    for event in trajectory:
        at_revision = event.get("at_revision")
        if at_revision not in revision_by_number:
            blockers.append(f"trajectory_revision_unknown:{at_revision}")
        if event.get("plan_id") and event["plan_id"] not in plan_ids:
            blockers.append(f"trajectory_plan_unknown:{event['plan_id']}")
        for plan_id in event.get("plan_ids", []):
            if plan_id not in plan_ids:
                blockers.append(f"trajectory_plan_unknown:{plan_id}")
        if event.get("type") in {"preview", "authorize", "dry_run", "verify"} and (committed_at is None or at_revision < committed_at):
            blockers.append(f"execution_before_commitment:{event.get('type')}")
    return blockers


def validate_action_contract(contract: dict[str, Any], final_intent: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    required = {"id", "operation", "preconditions", "expected_postconditions", "forbidden_postconditions", "verification_method", "risk_class", "reversibility", "authorized"}
    blockers.extend(f"action_contract_missing:{field}" for field in sorted(required - set(contract)))
    if final_intent["maturity"] != "committed":
        blockers.append("action_requires_committed_intent")
    if final_intent["outcome_verifiability"] != "verifiable":
        blockers.append("action_requires_verifiable_outcome")
    if contract.get("risk_class") not in RISKS:
        blockers.append("invalid_action_contract_risk")
    if contract.get("risk_class") == "consequential" and contract.get("authorized") is not True:
        blockers.append("consequential_action_not_authorized")
    if not contract.get("expected_postconditions") or not contract.get("verification_method"):
        blockers.append("action_has_no_independent_verification")
    return blockers


def annotate_representation_space(plans: list[dict[str, Any]], trajectory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = {event["plan_id"] for event in trajectory if event.get("type") == "select" and event.get("plan_id")}
    annotated = []
    for plan in plans:
        item = deepcopy(plan)
        item["context_status"] = "selected_in_context" if item["id"] in selected else "not_selected_in_context"
        annotated.append(item)
    return annotated


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    history = build_history(fixture)
    blockers = validate_history(history)
    blockers.extend(validate_representation_space(fixture.get("representation_space", [])))
    blockers.extend(validate_trajectory(fixture.get("trajectory", []), fixture.get("representation_space", []), history))
    blockers.extend(validate_action_contract(fixture.get("action_contract", {}), history[-1]))
    policies = [representation_policy(intent) for intent in history]
    annotated_plans = annotate_representation_space(fixture.get("representation_space", []), fixture.get("trajectory", []))
    oracle = load_oracle()
    oracle_result = oracle.evaluate(history, fixture.get("trajectory", []), fixture.get("action_contract", {}))
    if oracle_result["validation"] != "verified":
        blockers.append("independent_oracle_rejected")
    status = "PROGRESSIVE_COMMITMENT_VERIFIED" if not blockers else "BLOCKED"
    committed_revision = next((intent["revision"] for intent in history if intent["maturity"] == "committed"), len(history) + 1)
    commitment_attempts = [event for event in fixture["trajectory"] if event.get("type") in {"commit_intent", "preview", "dry_run", "verify"}]
    premature_attempts = [event for event in commitment_attempts if event.get("at_revision", 0) < committed_revision]
    return {
        "status": status,
        "blockers": blockers,
        "intent_history": history,
        "representation_space": annotated_plans,
        "policies": policies,
        "trajectory": fixture["trajectory"],
        "action_contract": fixture["action_contract"],
        "oracle": oracle_result,
        "metrics": {
            "intent_revision_count": len(history),
            "alternatives_offered_before_commitment": sum(event["type"] == "offer" for event in fixture["trajectory"] if event.get("at_revision", 0) < committed_revision),
            "premature_commitment_rate_fixture": len(premature_attempts) / max(1, len(commitment_attempts)),
            "plans_not_selected_are_not_wrong": all(plan["context_status"] in {"selected_in_context", "not_selected_in_context"} for plan in annotated_plans),
            "branches_preserved": len(fixture["representation_space"]),
        },
        "execution_allowed": False,
        "human_data": False,
        "camera_used": False,
        "network_used": False,
        "arbitrary_code_executed": False,
        "psychological_inference": False,
        "scope_limit": "synthetic progressive-formalization trace; no human comprehension or creative-quality claim",
    }


def main() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    result = compile_fixture(fixture)
    result["experiment"] = "061-codeine-progressive-commitment"
    # Keep the subprocess contract portable across Windows console code pages.
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
