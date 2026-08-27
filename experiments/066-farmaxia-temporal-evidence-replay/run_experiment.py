"""Replay temporal evidence without making arrival order the source of truth."""

from __future__ import annotations

import hashlib
import itertools
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fingerprint_event(event: dict[str, Any]) -> str:
    comparable = {key: value for key, value in event.items() if key not in {"delivery_id", "duplicate_of"}}
    encoded = json.dumps(comparable, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_fixture(fixture: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    source = fixture.get("source_of_truth", {})
    policy = fixture.get("policy", {})
    for key, expected in {
        "order_invariant_replay": True,
        "retractions_keep_history": True,
        "unknown_on_missing_temporal_authority": True,
        "conflicts_are_not_success": True,
        "network_allowed": False,
        "human_data": False,
    }.items():
        if policy.get(key) is not expected:
            blockers.append(f"policy_invalid:{key}")
    if source.get("surface") != "gitlab" or not source.get("project_id") or not isinstance(source.get("current_version"), int):
        blockers.append("source_identity_invalid")
    known_entities = set(source.get("entities", []))
    events = fixture.get("events", [])
    if not events:
        blockers.append("events_missing")
    event_ids = {event.get("event_id") for event in events}
    if None in event_ids:
        blockers.append("event_id_missing")
    for event in events:
        event_id = event.get("event_id")
        if event.get("source") != source.get("surface") or event.get("project_id") != source.get("project_id"):
            blockers.append(f"event_source_identity_invalid:{event_id}")
        if event.get("entity_ref") not in known_entities:
            blockers.append(f"event_entity_unknown:{event_id}")
        if event.get("kind") not in {"set", "retract", "observation"}:
            blockers.append(f"event_kind_invalid:{event_id}")
        if not event.get("root_id") or not event.get("field") or not isinstance(event.get("observed_at"), int):
            blockers.append(f"event_contract_incomplete:{event_id}")
        if event.get("kind") in {"set", "retract"}:
            if not isinstance(event.get("source_version"), int) or not isinstance(event.get("valid_time"), int):
                blockers.append(f"temporal_authority_missing:{event_id}")
            elif event["source_version"] > source.get("current_version", -1):
                blockers.append(f"source_version_ahead:{event_id}")
        if event.get("kind") == "set" and "value" not in event.get("payload", {}):
            blockers.append(f"set_value_missing:{event_id}")
        if event.get("kind") == "retract":
            if not event.get("revokes"):
                blockers.append(f"retraction_target_missing:{event_id}")
            elif any(target not in event_ids for target in event.get("revokes", [])):
                blockers.append(f"retraction_target_unknown:{event_id}")
    expected_projection = fixture.get("expected_projection", [])
    if not expected_projection or len({(item.get("entity_ref"), item.get("field")) for item in expected_projection}) != len(expected_projection):
        blockers.append("expected_projection_invalid")
    return sorted(set(blockers))


def deduplicate(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, list[str]]:
    unique: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    duplicates = 0
    conflicts: list[str] = []
    for event in events:
        event_id = event.get("event_id")
        fingerprint = fingerprint_event(event)
        if event_id in seen:
            duplicates += 1
            if seen[event_id] != fingerprint:
                conflicts.append(event_id)
            continue
        seen[event_id] = fingerprint
        unique.append(event)
    return unique, duplicates, conflicts


def replay(events: list[dict[str, Any]]) -> dict[str, Any]:
    unique, duplicate_count, duplicate_conflicts = deduplicate(events)
    by_id = {event["event_id"]: event for event in unique}
    revoked_ids = {
        target
        for event in unique
        if event.get("kind") == "retract"
        for target in event.get("revokes", [])
    }
    history = []
    for event in sorted(unique, key=lambda item: item["event_id"]):
        if event.get("kind") == "observation":
            status = "UNKNOWN"
            reason = "missing_source_version_or_valid_time"
        elif event.get("kind") == "retract":
            status = "RETRACTION"
            reason = event.get("payload", {}).get("reason", "source_retraction")
        elif event["event_id"] in revoked_ids:
            status = "RETRACTED"
            reason = "revoked_by_retraction_event"
        else:
            status = "ACTIVE"
            reason = None
        history.append({
            "event_id": event["event_id"],
            "root_id": event["root_id"],
            "entity_ref": event["entity_ref"],
            "field": event["field"],
            "source_version": event.get("source_version"),
            "valid_time": event.get("valid_time"),
            "observed_at": event["observed_at"],
            "status": status,
            "reason": reason,
        })

    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for event in unique:
        if event.get("kind") != "set" or event["event_id"] in revoked_ids:
            continue
        groups.setdefault((event["entity_ref"], event["field"]), []).append(event)

    projection = []
    for key in sorted(groups):
        entity_ref, field = key
        candidates = groups[key]
        by_version: dict[int, list[dict[str, Any]]] = {}
        for event in candidates:
            by_version.setdefault(event["source_version"], []).append(event)
        newest_version = max(by_version)
        newest = by_version[newest_version]
        values = sorted({json.dumps(event["payload"]["value"], sort_keys=True) for event in newest})
        refs = sorted(event["event_id"] for event in newest)
        if len(values) > 1:
            projection.append({
                "entity_ref": entity_ref,
                "field": field,
                "status": "CONFLICT",
                "value": None,
                "source_version": newest_version,
                "source_refs": refs,
                "conflicting_values": [json.loads(value) for value in values],
            })
        else:
            projection.append({
                "entity_ref": entity_ref,
                "field": field,
                "status": "SUPPORTED",
                "value": json.loads(values[0]),
                "source_version": newest_version,
                "source_refs": refs,
                "conflicting_values": [],
            })
    unknowns = [item for item in history if item["status"] == "UNKNOWN"]
    for item in unknowns:
        projection.append({
            "entity_ref": item["entity_ref"],
            "field": item["field"],
            "status": "UNKNOWN",
            "value": None,
            "source_version": None,
            "source_refs": [item["event_id"]],
            "conflicting_values": [],
        })
    projection.sort(key=lambda item: (item["entity_ref"], item["field"]))
    return {
        "unique_events": len(unique),
        "duplicate_events": duplicate_count,
        "duplicate_conflicts": sorted(duplicate_conflicts),
        "history": history,
        "projection": projection,
        "unknowns": unknowns,
        "retractions": [item for item in history if item["status"] == "RETRACTION"],
        "revoked_event_ids": sorted(revoked_ids),
        "event_ids": sorted(by_id),
    }


def projection_signature(result: dict[str, Any]) -> str:
    return json.dumps(result["projection"], sort_keys=True, separators=(",", ":"))


def expected_matches(projection: list[dict[str, Any]], expected: list[dict[str, Any]]) -> bool:
    actual = [
        {key: item.get(key) for key in ("entity_ref", "field", "status", "value")}
        for item in projection
    ]
    return actual == sorted(expected, key=lambda item: (item["entity_ref"], item["field"]))


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    blockers = validate_fixture(fixture)
    events = fixture.get("events", [])
    base = replay(events)
    if base["duplicate_conflicts"]:
        blockers.append("conflicting_duplicate_delivery")
    permutations = [events, list(reversed(events)), sorted(events, key=lambda item: (item.get("observed_at", -1), item.get("event_id", "")))]
    replay_results = [replay(permutation) for permutation in permutations]
    signatures = [projection_signature(result) for result in replay_results]
    if len(set(signatures)) != 1:
        blockers.append("replay_order_changed_projection")
    if not expected_matches(base["projection"], fixture.get("expected_projection", [])):
        blockers.append("projection_expectation_mismatch")
    expected_retracted = "ev-pipeline-failed"
    history_by_event = {item["event_id"]: item for item in base["history"]}
    if history_by_event.get(expected_retracted, {}).get("status") != "RETRACTED":
        blockers.append("retraction_history_not_preserved")
    if not any(item["status"] == "CONFLICT" for item in base["projection"]):
        blockers.append("conflict_not_exposed")
    if any(item["status"] == "CONFLICT" and item.get("value") is not None for item in base["projection"]):
        blockers.append("conflict_collapsed_to_value")
    if not base["unknowns"]:
        blockers.append("unknown_boundary_not_exposed")
    status = "TEMPORAL_REPLAY_VERIFIED" if not blockers else "BLOCKED"
    return {
        "experiment": "066-farmaxia-temporal-evidence-replay",
        "status": status,
        "blockers": sorted(set(blockers)),
        "ledger": {
            "raw_event_count": len(events),
            "unique_event_count": base["unique_events"],
            "duplicate_event_count": base["duplicate_events"],
            "duplicate_conflict_ids": base["duplicate_conflicts"],
            "out_of_order_input": [event.get("observed_at") for event in events] != sorted(event.get("observed_at") for event in events) if events else False,
            "append_only": True,
            "retractions_preserve_history": history_by_event.get(expected_retracted, {}).get("status") == "RETRACTED",
        },
        "replay": {
            "permutation_count": len(permutations),
            "all_projection_signatures_equal": len(set(signatures)) == 1,
            "projection": base["projection"],
            "history": base["history"],
            "retractions": base["retractions"],
            "unknowns": base["unknowns"],
            "revoked_event_ids": base["revoked_event_ids"],
        },
        "safety": {
            "network_used": False,
            "external_execution": False,
            "human_data": False,
            "camera_used": False,
            "source_write_attempted": False,
        },
        "scope_limit": "synthetic batch replay; no claim of distributed consensus or production event-stream guarantees",
    }


def main() -> None:
    print(json.dumps(compile_fixture(load_json(FIXTURE)), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
