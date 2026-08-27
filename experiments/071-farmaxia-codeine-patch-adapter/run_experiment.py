"""Reuse the shared CloudEvents kernel for a synthetic CODE-INE patch flow."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1] / "research" / "tools"
sys.path.insert(0, str(TOOLS))

from cloudevents_contract import compile_envelope, load_json  # noqa: E402


FIXTURE = HERE / "fixture.json"


def record_by_ref(fixture: dict[str, Any], reference: str) -> dict[str, Any]:
    return next(
        (
            record
            for record in fixture.get("source_of_truth", {}).get("records", [])
            if record.get("entity_ref") == reference
        ),
        {},
    )


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    source = fixture.get("source_of_truth", {})
    adapter = fixture.get("adapter", {})
    workspace = fixture.get("workspace", {})
    patch = fixture.get("patch", {})
    action = fixture.get("action", {})
    cloud_result = compile_envelope(fixture)
    blockers = list(cloud_result["blockers"])

    replay_permutations = [
        fixture.get("events", []),
        list(reversed(fixture.get("events", []))),
        sorted(
            fixture.get("events", []),
            key=lambda event: (event.get("farmaxia-observed-at", -1), event.get("id", "")),
        ),
    ]
    replay_signatures = []
    for permutation in replay_permutations:
        replay_result = compile_envelope({**fixture, "events": permutation})
        if replay_result["status"] != "CLOUDEVENTS_ENVELOPE_VERIFIED":
            blockers.append("replay_permutation_not_verified")
        replay_signatures.append(
            json.dumps(replay_result["envelope"]["canonical_order"], separators=(",", ":"))
        )
    replay_order_invariant = len(set(replay_signatures)) == 1
    if not replay_order_invariant:
        blockers.append("replay_order_changed_projection")

    if adapter.get("source_surface") != source.get("surface"):
        blockers.append("adapter_source_surface_mismatch")
    if adapter.get("destination_surface") != "editor-workspace":
        blockers.append("adapter_destination_surface_invalid")
    if workspace.get("dry_run_only") is not True:
        blockers.append("workspace_dry_run_policy_missing")

    actual_event_ids = {event.get("id") for event in fixture.get("events", []) if event.get("id")}
    required_event_ids = set(adapter.get("required_event_ids", []))
    if not required_event_ids.issubset(actual_event_ids):
        blockers.append("required_input_event_missing")

    known_refs = set(source.get("entity_refs", []))
    source_refs = []
    for claim in fixture.get("representation_claims", []):
        refs = claim.get("source_refs", [])
        if not claim.get("claim_id") or not claim.get("text") or not refs:
            blockers.append(f"representation_claim_incomplete:{claim.get('claim_id')}")
        for reference in refs:
            source_refs.append(reference)
            if reference not in known_refs:
                blockers.append(f"representation_source_ref_invalid:{claim.get('claim_id')}")

    required_patch_fields = {"patch_id", "target_ref", "base_sha256", "candidate_sha256", "operation", "semantic_intent"}
    for field in sorted(required_patch_fields - set(patch)):
        blockers.append(f"patch_field_missing:{field}")
    target_record = record_by_ref(fixture, patch.get("target_ref", ""))
    if patch.get("target_ref") not in known_refs or not target_record:
        blockers.append("patch_target_unknown")
    if patch.get("base_sha256") != target_record.get("sha256"):
        blockers.append("patch_base_sha_mismatch")
    if patch.get("code_execution") is not False:
        blockers.append("arbitrary_code_execution_enabled")

    if not action.get("action_id") or action.get("operation") != "preview_code_patch":
        blockers.append("action_contract_invalid")
    if action.get("dry_run") is not True:
        blockers.append("external_execution_enabled")
    if action.get("requires_confirmation") is not True:
        blockers.append("confirmation_requirement_missing")
    if action.get("target_workspace_id") != workspace.get("workspace_id"):
        blockers.append("action_target_workspace_mismatch")
    for precondition in action.get("preconditions", []):
        reference = precondition.get("entity_ref")
        record = record_by_ref(fixture, reference or "")
        if not reference or not record:
            blockers.append("action_precondition_entity_unknown")
        if precondition.get("source_version") != record.get("source_version"):
            blockers.append("action_precondition_version_not_current")
        if precondition.get("status") != record.get("status"):
            blockers.append("action_precondition_status_mismatch")

    change_ref = "code-host:farmaksia-core:change:change-17"
    check_ref = "code-host:farmaksia-core:check:contract-suite"
    change = record_by_ref(fixture, change_ref)
    check = record_by_ref(fixture, check_ref)
    verification = [
        {
            "query": "code.change.change-17.status",
            "expected": "review",
            "actual": change.get("status"),
            "status": "VERIFIED" if change.get("status") == "review" else "REFUTED",
        },
        {
            "query": "code.check.contract-suite.status",
            "expected": "passed",
            "actual": check.get("status"),
            "status": "VERIFIED" if check.get("status") == "passed" else "REFUTED",
        },
        {
            "query": "editor.workspace.permission.preview",
            "expected": True,
            "actual": "preview" in workspace.get("permissions", []),
            "status": "VERIFIED" if "preview" in workspace.get("permissions", []) else "REFUTED",
        },
        {
            "query": "patch.code_execution",
            "expected": False,
            "actual": patch.get("code_execution"),
            "status": "VERIFIED" if patch.get("code_execution") is False else "REFUTED",
        },
    ]
    if any(item["status"] != "VERIFIED" for item in verification):
        blockers.append("independent_code_oracle_failed")
    if not source_refs:
        blockers.append("representation_provenance_missing")

    status = "CODEINE_CLOUDEVENTS_ADAPTER_VERIFIED" if not blockers else "BLOCKED"
    return {
        "experiment": "071-farmaxia-codeine-patch-adapter",
        "status": status,
        "blockers": sorted(set(blockers)),
        "input_envelope": {
            "status": cloud_result["status"],
            "raw_event_count": cloud_result["envelope"]["raw_event_count"],
            "unique_event_count": cloud_result["envelope"]["unique_event_count"],
            "duplicate_event_count": cloud_result["envelope"]["duplicate_event_count"],
            "canonical_order": cloud_result["envelope"]["canonical_order"],
            "original_envelopes_retained": cloud_result["envelope"]["original_envelopes_retained"],
        },
        "replay": {
            "permutation_count": len(replay_permutations),
            "all_canonical_signatures_equal": replay_order_invariant,
            "canonical_order": cloud_result["envelope"]["canonical_order"],
        },
        "adapter": {
            "source": source.get("surface"),
            "destination": adapter.get("destination_surface"),
            "mapping": adapter.get("mapping", {}),
            "source_refs": sorted(set(source_refs)),
            "same_shared_cloudevents_kernel": True,
        },
        "patch": {
            "patch_id": patch.get("patch_id"),
            "target_ref": patch.get("target_ref"),
            "base_sha256": patch.get("base_sha256"),
            "code_execution": patch.get("code_execution"),
        },
        "action": {
            "operation": action.get("operation"),
            "status": "DRY_RUN_ONLY" if action.get("dry_run") else "BLOCKED",
            "requires_confirmation": action.get("requires_confirmation"),
            "target_workspace_id": action.get("target_workspace_id"),
        },
        "independent_verification": {
            "independent_source": "synthetic_code_host_source_store",
            "not_verified_from_representation": True,
            "checks": verification,
        },
        "safety": {
            "network_used": False,
            "external_execution": False,
            "human_data": False,
            "camera_used": False,
            "source_write_attempted": False,
            "arbitrary_code_executed": False,
        },
        "scope_limit": "local synthetic CODE-INE patch adapter; no code execution, live API or repository write claim",
    }


def main() -> None:
    print(json.dumps(compile_fixture(load_json(FIXTURE)), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
