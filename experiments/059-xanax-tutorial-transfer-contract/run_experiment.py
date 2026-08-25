"""Validate X-ANA-X tutorial and cross-application bridge contracts.

This is a local, deterministic contract experiment. It intentionally does not
download sources, launch applications, execute commands, or collect human data.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).parent
SOURCE_CARDS = HERE / "source_cards.json"


REQUIRED_SOURCE_FIELDS = {
    "source_id",
    "uri",
    "retrieved_at",
    "source_kind",
    "application",
    "application_version",
    "locale",
    "license",
    "prerequisites",
    "concepts",
    "steps",
}
REQUIRED_STEP_FIELDS = {
    "id",
    "preconditions",
    "action_family",
    "action",
    "expected_observation",
    "postconditions",
    "evidence",
}


def source_status(card: dict[str, Any]) -> dict[str, Any]:
    missing_source = sorted(REQUIRED_SOURCE_FIELDS - set(card))
    missing_steps: dict[str, list[str]] = {}
    for step in card.get("steps", []):
        missing = sorted(REQUIRED_STEP_FIELDS - set(step))
        if missing:
            missing_steps[step.get("id", "unknown-step")] = missing
    status = "SOURCE_INVALID" if missing_source or missing_steps or not card.get("steps") else "TEACHING_DRAFT"
    return {
        "source_id": card.get("source_id"),
        "status": status,
        "missing_source_fields": missing_source,
        "missing_step_fields": missing_steps,
        "automation_blockers": [
            "live_application_state",
            "app_adapter",
            "postcondition_verifier",
        ],
    }


def dry_run_status(card: dict[str, Any], adapter: str | None = None) -> dict[str, Any]:
    status = source_status(card)
    blockers: list[str] = []
    if status["missing_source_fields"] or status["missing_step_fields"]:
        blockers.append("invalid_source_contract")
    if not card.get("steps"):
        blockers.append("no_tutorial_steps")
    for step in card.get("steps", []):
        if not step.get("postconditions"):
            blockers.append(f"missing_postcondition:{step.get('id', 'unknown-step')}")
        if not step.get("evidence"):
            blockers.append(f"missing_evidence:{step.get('id', 'unknown-step')}")
    if adapter is None:
        blockers.append("missing_app_adapter")
    return {
        "source_id": card.get("source_id"),
        "status": "DRY_RUN_READY" if not blockers else "DRY_RUN_BLOCKED",
        "blockers": blockers,
    }


def bridge_status(
    from_card: dict[str, Any],
    to_card: dict[str, Any],
    bridge: dict[str, Any] | None,
) -> dict[str, Any]:
    if bridge is None:
        return {
            "status": "BRIDGE_BLOCKED",
            "blockers": ["missing_bridge_contract"],
            "from_application": from_card["application"],
            "to_application": to_card["application"],
        }
    required = {
        "from_application",
        "from_state",
        "artifact_or_transform",
        "assumptions",
        "to_application",
        "to_state",
        "verifier",
        "residue",
    }
    missing = sorted(required - set(bridge))
    mismatches = []
    if bridge.get("from_application") != from_card.get("application"):
        mismatches.append("from_application_mismatch")
    if bridge.get("to_application") != to_card.get("application"):
        mismatches.append("to_application_mismatch")
    blockers = [f"missing_bridge_field:{field}" for field in missing] + mismatches
    return {
        "status": "BRIDGE_READY" if not blockers else "BRIDGE_BLOCKED",
        "blockers": blockers,
        "from_application": from_card["application"],
        "to_application": to_card["application"],
        "artifact_or_transform": bridge.get("artifact_or_transform"),
    }


def compose(
    from_card: dict[str, Any],
    to_card: dict[str, Any],
    bridge: dict[str, Any] | None,
) -> dict[str, Any]:
    from_run = dry_run_status(from_card, adapter="maya-native-python")
    to_run = dry_run_status(to_card, adapter="blender-native-python")
    bridge_run = bridge_status(from_card, to_card, bridge)
    ready = (
        from_run["status"] == "DRY_RUN_READY"
        and to_run["status"] == "DRY_RUN_READY"
        and bridge_run["status"] == "BRIDGE_READY"
    )
    return {
        "status": "COMPOSABLE_DRY_RUN" if ready else "COMPOSITION_BLOCKED",
        "concept_relation": "analogous",
        "from": from_card["application"],
        "to": to_card["application"],
        "from_dry_run": from_run,
        "to_dry_run": to_run,
        "bridge": bridge_run,
        "execution_allowed": False,
        "reason": "a real application adapter and opt-in execution gate are outside this local experiment",
    }


def main() -> None:
    cards = json.loads(SOURCE_CARDS.read_text(encoding="utf-8"))
    maya = cards["maya"]
    blender = cards["blender"]
    incomplete = cards["incomplete"]
    bridge = cards["maya_to_blender_bridge"]

    result = {
        "experiment": "059-xanax-tutorial-transfer-contract",
        "source_cards": {
            "maya": source_status(maya),
            "blender": source_status(blender),
            "incomplete": source_status(incomplete),
        },
        "document_only": {
            "status": source_status(maya)["status"],
            "automation_ready": False,
            "reason": "documents describe concepts and steps but do not prove live UI state",
        },
        "composed_with_bridge": compose(maya, blender, bridge),
        "composed_without_bridge": compose(maya, blender, None),
        "human_data": False,
        "network_used": False,
        "applications_started": False,
        "commands_executed": False,
        "arbitrary_corpus": False,
        "scope_limit": "declarative source cards and state contracts only; no comprehension or app-execution claim",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
