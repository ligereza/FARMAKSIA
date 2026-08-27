"""Compile and independently verify a synthetic GitLab–Mattermost bridge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fingerprint_event(event: dict[str, Any]) -> str:
    comparable = {
        key: value
        for key, value in event.items()
        if key not in {"delivery_id", "duplicate_of"}
    }
    encoded = json.dumps(comparable, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def entity_ref(project_id: str, entity_type: str, entity_id: str) -> str:
    return f"gitlab:{project_id}:{entity_type}:{entity_id}"


def validate_fixture(fixture: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    policy = fixture.get("policy", {})
    required_policy = {
        "network_allowed": False,
        "human_data": False,
        "require_project_qualified_identity": True,
        "require_source_provenance": True,
        "require_independent_verifier": True,
        "require_explicit_confirmation": True,
        "unknown_on_conflict": True,
    }
    for key, expected in required_policy.items():
        if policy.get(key) is not expected:
            blockers.append(f"policy_invalid:{key}")
    if policy.get("mode") != "local_read_only_dry_run":
        blockers.append("execution_mode_not_local_dry_run")

    source = fixture.get("source_of_truth", {})
    if source.get("surface") != "gitlab":
        blockers.append("source_of_truth_not_gitlab")
    project = source.get("project", {})
    project_id = project.get("id")
    if not project_id or not project.get("path") or not isinstance(project.get("version"), int):
        blockers.append("source_project_identity_incomplete")
    entities = source.get("entities", [])
    entity_keys = [(item.get("type"), item.get("id")) for item in entities]
    if not entities or any(not item.get("type") or not item.get("id") for item in entities):
        blockers.append("source_entities_incomplete")
    if len(entity_keys) != len(set(entity_keys)):
        blockers.append("source_entity_ids_not_unique")
    source_keys = set(entity_keys)
    for item in entities:
        if item.get("source_version", -1) > project.get("version", -1):
            blockers.append(f"source_entity_version_ahead:{item.get('id')}")

    raw_events = fixture.get("events", [])
    if not raw_events:
        blockers.append("events_missing")
    event_ids = [event.get("event_id") for event in raw_events]
    if any(not event_id for event_id in event_ids):
        blockers.append("event_identity_missing")
    seen_fingerprints: dict[str, str] = {}
    for event in raw_events:
        if event.get("source") != "gitlab":
            blockers.append(f"event_source_invalid:{event.get('event_id')}")
        if event.get("project_id") != project_id:
            blockers.append(f"event_project_identity_invalid:{event.get('event_id')}")
        if (event.get("entity_type"), event.get("entity_id")) not in source_keys:
            blockers.append(f"event_entity_unknown:{event.get('event_id')}")
        if not isinstance(event.get("occurred_at"), int):
            blockers.append(f"event_timestamp_invalid:{event.get('event_id')}")
        event_id = event.get("event_id")
        if event_id:
            fingerprint = fingerprint_event(event)
            previous = seen_fingerprints.setdefault(event_id, fingerprint)
            if previous != fingerprint:
                blockers.append(f"duplicate_event_conflict:{event_id}")

    mattermost = fixture.get("mattermost_surface", {})
    if not mattermost.get("instance_id") or not mattermost.get("team_id") or not mattermost.get("channel_id"):
        blockers.append("mattermost_surface_identity_incomplete")
    if "post" not in mattermost.get("permissions", []):
        blockers.append("mattermost_post_permission_missing")

    action = fixture.get("action", {})
    if not action.get("action_id") or action.get("operation") != "post_contextual_notification":
        blockers.append("action_contract_invalid")
    if action.get("dry_run") is not True:
        blockers.append("external_execution_enabled")
    if action.get("requires_confirmation") is not True:
        blockers.append("confirmation_requirement_missing")
    if action.get("target_channel_id") != mattermost.get("channel_id"):
        blockers.append("action_target_channel_mismatch")
    for precondition in action.get("preconditions", []):
        if precondition.get("project_id") != project_id:
            blockers.append("action_precondition_project_missing")
        key = (precondition.get("entity_type"), precondition.get("entity_id"))
        if key not in source_keys:
            blockers.append("action_precondition_entity_unknown")
        if precondition.get("source_version") != project.get("version"):
            blockers.append("action_precondition_version_not_current")
    if action.get("claimed_outcome") not in {None, "DRY_RUN_ONLY"}:
        blockers.append("claimed_success_without_observation")

    valid_refs = {entity_ref(project_id, item[0], item[1]) for item in source_keys}
    for claim in fixture.get("representation_claims", []):
        refs = claim.get("source_refs", [])
        if not claim.get("claim_id") or not claim.get("text") or not refs:
            blockers.append(f"representation_claim_incomplete:{claim.get('claim_id')}")
        for ref in refs:
            base_ref = ref.split("#event:", 1)[0]
            if base_ref not in valid_refs:
                blockers.append(f"representation_source_ref_invalid:{claim.get('claim_id')}")
    return sorted(set(blockers))


def deduplicate_events(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, list[str]]:
    unique: list[dict[str, Any]] = []
    fingerprints: dict[str, str] = {}
    duplicates = 0
    conflicts: list[str] = []
    for event in events:
        event_id = event.get("event_id")
        fingerprint = fingerprint_event(event)
        if event_id in fingerprints:
            duplicates += 1
            if fingerprints[event_id] != fingerprint:
                conflicts.append(event_id)
            continue
        fingerprints[event_id] = fingerprint
        unique.append(event)
    return unique, duplicates, conflicts


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    blockers = validate_fixture(fixture)
    source = fixture.get("source_of_truth", {})
    project = source.get("project", {})
    raw_events = fixture.get("events", [])
    unique_events, duplicate_count, conflict_ids = deduplicate_events(raw_events)
    canonical_events = sorted(unique_events, key=lambda event: (event["occurred_at"], event["event_id"]))
    raw_order = [event.get("event_id") for event in raw_events]
    canonical_order = [event.get("event_id") for event in canonical_events]
    out_of_order = [event.get("occurred_at") for event in raw_events] != sorted(event.get("occurred_at") for event in raw_events) if raw_events else False
    if conflict_ids:
        blockers.append("duplicate_event_conflict_detected")

    normalized_events = [
        {
            "event_id": event["event_id"],
            "source": event["source"],
            "entity_ref": entity_ref(project["id"], event["entity_type"], event["entity_id"]),
            "source_version": event["source_version"],
            "occurred_at": event["occurred_at"],
            "event_kind": event["payload"].get("kind", event["entity_type"]),
        }
        for event in canonical_events
    ]
    source_refs = sorted({ref for claim in fixture.get("representation_claims", []) for ref in claim.get("source_refs", [])})
    representation = {
        "kind": "contextual_review_map",
        "claims": fixture.get("representation_claims", []),
        "source_refs": source_refs,
        "unknowns": [
            "No se ha publicado ningún mensaje porque la acción está en dry-run.",
            "La aprobación de la merge request no está determinada por una pregunta de revisión.",
        ],
        "editable": False,
    }
    action = fixture.get("action", {})
    action_proposal = {
        "action_id": action.get("action_id"),
        "operation": action.get("operation"),
        "target": {
            "surface": "mattermost",
            "team_id": fixture.get("mattermost_surface", {}).get("team_id"),
            "channel_id": action.get("target_channel_id"),
        },
        "preconditions": action.get("preconditions", []),
        "dry_run": action.get("dry_run"),
        "requires_confirmation": action.get("requires_confirmation"),
        "status": "DRY_RUN_ONLY" if action.get("dry_run") else "BLOCKED",
    }
    source_entities = {(item.get("type"), item.get("id")): item for item in source.get("entities", [])}
    checks = []
    for entity_type, entity_id, field, expected in [
        ("merge_request", "mr-7", "state", "opened"),
        ("pipeline", "pipe-3", "status", "failed"),
    ]:
        actual = source_entities.get((entity_type, entity_id), {}).get(field)
        checks.append({
            "query": f"gitlab.{entity_type}.{entity_id}.{field}",
            "expected": expected,
            "actual": actual,
            "status": "VERIFIED" if actual == expected else "REFUTED",
        })
    checks.append({
        "query": "mattermost.channel.permission.post",
        "expected": True,
        "actual": "post" in fixture.get("mattermost_surface", {}).get("permissions", []),
        "status": "VERIFIED" if "post" in fixture.get("mattermost_surface", {}).get("permissions", []) else "REFUTED",
    })
    checks.append({
        "query": "action.external_effect",
        "expected": "not_executed_by_policy",
        "actual": "not_executed_by_policy" if action.get("dry_run") else "unknown",
        "status": "VERIFIED" if action.get("dry_run") else "REFUTED",
    })
    if any(check["status"] != "VERIFIED" for check in checks):
        blockers.append("independent_verification_failed")
    status = "CROSS_APPLICATION_EVIDENCE_VERIFIED" if not blockers else "BLOCKED"
    return {
        "experiment": "065-farmaxia-cross-application-evidence",
        "status": status,
        "blockers": sorted(set(blockers)),
        "ingestion": {
            "raw_event_count": len(raw_events),
            "unique_event_count": len(unique_events),
            "duplicate_event_count": duplicate_count,
            "out_of_order_input": out_of_order,
            "raw_order": raw_order,
            "canonical_order": canonical_order,
            "normalized_events": normalized_events,
        },
        "semantic_model": {
            "source_of_truth": "gitlab",
            "project_ref": f"gitlab:{project.get('id')}",
            "identity_is_project_qualified": all("project_id" in event for event in raw_events),
            "representation": representation,
        },
        "action_proposal": action_proposal,
        "independent_verification": {
            "independent_source": "synthetic_gitlab_source_store",
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
        "scope_limit": "synthetic read-only bridge; no claim of production interoperability or human comprehension",
    }


def main() -> None:
    print(json.dumps(compile_fixture(load_json(FIXTURE)), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
