"""Independent oracle for progressive intent formalization."""

from __future__ import annotations

from typing import Any


EXPECTED_MATURITY = ["emergent", "emergent", "provisional", "provisional", "committed"]
EXPECTED_VERIFIABILITY = ["open", "open", "constrained", "constrained", "verifiable"]
EXPECTED_TRACE = ["offer", "offer", "offer", "offer", "inspect", "compare", "select", "edit", "commit_intent", "preview", "authorize", "dry_run", "verify"]


def evaluate(
    history: list[dict[str, Any]],
    trajectory: list[dict[str, Any]],
    action_contract: dict[str, Any],
) -> dict[str, Any]:
    maturity = [item.get("maturity") for item in history]
    verifiability = [item.get("outcome_verifiability") for item in history]
    event_types = [item.get("type") for item in trajectory]
    blockers: list[str] = []
    if maturity != EXPECTED_MATURITY:
        blockers.append("intent_maturity_sequence_conflict")
    if verifiability != EXPECTED_VERIFIABILITY:
        blockers.append("outcome_verifiability_sequence_conflict")
    if event_types != EXPECTED_TRACE:
        blockers.append("trajectory_sequence_conflict")
    commit_index = event_types.index("commit_intent") if "commit_intent" in event_types else -1
    if commit_index >= 0 and any(item in {"preview", "authorize", "dry_run", "verify"} for item in event_types[:commit_index]):
        blockers.append("commitment_happened_after_execution")
    required_contract = {
        "preconditions",
        "expected_postconditions",
        "forbidden_postconditions",
        "verification_method",
        "risk_class",
        "reversibility",
        "authorized",
    }
    if not required_contract.issubset(action_contract):
        blockers.append("action_contract_incomplete")
    if action_contract.get("risk_class") != "reversible":
        blockers.append("unexpected_action_risk")
    if action_contract.get("authorized") is not True:
        blockers.append("action_not_authorized")
    return {
        "validation": "verified" if not blockers else "rejected",
        "blockers": blockers,
        "maturity": maturity,
        "verifiability": verifiability,
        "event_types": event_types,
        "final_state": "verified" if not blockers else "unknown",
    }
