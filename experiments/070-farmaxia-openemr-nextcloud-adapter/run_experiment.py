"""Reuse the shared CloudEvents kernel for a synthetic institutional document flow."""

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
    destination = fixture.get("nextcloud_surface", {})
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
            json.dumps(
                replay_result["envelope"]["canonical_order"],
                separators=(",", ":"),
            )
        )
    replay_order_invariant = len(set(replay_signatures)) == 1
    if not replay_order_invariant:
        blockers.append("replay_order_changed_projection")

    if adapter.get("source_surface") != source.get("surface"):
        blockers.append("adapter_source_surface_mismatch")
    if adapter.get("destination_surface") != "nextcloud":
        blockers.append("adapter_destination_surface_invalid")
    if destination.get("dry_run_only") is not True:
        blockers.append("destination_dry_run_policy_missing")

    events = fixture.get("events", [])
    actual_event_ids = {event.get("id") for event in events if event.get("id")}
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

    action = fixture.get("action", {})
    if not action.get("action_id") or action.get("operation") != "create_document_index_entry":
        blockers.append("action_contract_invalid")
    if action.get("dry_run") is not True:
        blockers.append("external_execution_enabled")
    if action.get("requires_confirmation") is not True:
        blockers.append("confirmation_requirement_missing")
    if action.get("target_folder_id") != destination.get("folder_id"):
        blockers.append("action_target_folder_mismatch")
    for precondition in action.get("preconditions", []):
        reference = precondition.get("entity_ref")
        record = record_by_ref(fixture, reference or "")
        if not reference or not record:
            blockers.append("action_precondition_entity_unknown")
        if precondition.get("source_version") != record.get("source_version"):
            blockers.append("action_precondition_version_not_current")
        if precondition.get("status") != record.get("status"):
            blockers.append("action_precondition_status_mismatch")

    care_plan_ref = "openemr:synthetic-clinic:care_plan:plan-demo-001"
    document_ref = "openemr:synthetic-clinic:document:doc-demo-001"
    patient_ref = "openemr:synthetic-clinic:patient:patient-demo-001"
    care_plan = record_by_ref(fixture, care_plan_ref)
    document = record_by_ref(fixture, document_ref)
    patient = record_by_ref(fixture, patient_ref)
    checks = [
        {
            "query": "openemr.care_plan.plan-demo-001.status",
            "expected": "published",
            "actual": care_plan.get("status"),
            "status": "VERIFIED" if care_plan.get("status") == "published" else "REFUTED",
        },
        {
            "query": "openemr.document.doc-demo-001.status",
            "expected": "ready",
            "actual": document.get("status"),
            "status": "VERIFIED" if document.get("status") == "ready" else "REFUTED",
        },
        {
            "query": "nextcloud.folder.permission.write",
            "expected": True,
            "actual": "write" in destination.get("permissions", []),
            "status": "VERIFIED" if "write" in destination.get("permissions", []) else "REFUTED",
        },
        {
            "query": "action.external_effect",
            "expected": "not_executed_by_policy",
            "actual": "not_executed_by_policy" if action.get("dry_run") else "unknown",
            "status": "VERIFIED" if action.get("dry_run") else "REFUTED",
        },
    ]
    if any(check["status"] != "VERIFIED" for check in checks):
        blockers.append("independent_verification_failed")
    if not patient.get("synthetic"):
        blockers.append("human_data_boundary_missing")
    if not source_refs:
        blockers.append("representation_provenance_missing")

    status = "DOCUMENTAL_CLOUDEVENTS_ADAPTER_VERIFIED" if not blockers else "BLOCKED"
    return {
        "experiment": "070-farmaxia-openemr-nextcloud-adapter",
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
            "required_event_ids": sorted(required_event_ids),
            "source_refs": sorted(set(source_refs)),
            "same_shared_cloudevents_kernel": True,
        },
        "action": {
            "operation": action.get("operation"),
            "status": "DRY_RUN_ONLY" if action.get("dry_run") else "BLOCKED",
            "requires_confirmation": action.get("requires_confirmation"),
            "target_folder_id": action.get("target_folder_id"),
        },
        "independent_verification": {
            "independent_source": "synthetic_openemr_source_store",
            "not_verified_from_representation": True,
            "checks": checks,
        },
        "safety": {
            "network_used": False,
            "external_execution": False,
            "human_data": False,
            "camera_used": False,
            "source_write_attempted": False,
        },
        "scope_limit": "local synthetic OpenEMR–Nextcloud adapter; no clinical data and no live API interoperability claim",
    }


def main() -> None:
    print(json.dumps(compile_fixture(load_json(FIXTURE)), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
