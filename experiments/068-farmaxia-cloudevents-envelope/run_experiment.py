"""Validate a CloudEvents envelope and map it to the FARMAKSIA event contract."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.json"
REQUIRED_ATTRIBUTES = {"specversion", "id", "source", "type"}
REQUIRED_FARMAXIA_EXTENSIONS = {
    "farmaxia-entity-ref",
    "farmaxia-source-version",
    "farmaxia-observed-at",
    "farmaxia-root-id",
}
EXTENSION_NAME = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def event_identity(event: dict[str, Any]) -> tuple[str, str]:
    return event.get("source", ""), event.get("id", "")


def event_fingerprint(event: dict[str, Any]) -> str:
    comparable = {
        key: value
        for key, value in event.items()
        if key not in {"farmaxia-delivery-id", "farmaxia-observed-at"}
    }
    encoded = json.dumps(comparable, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def entity_ref(project_id: str, entity_type: str, entity_id: str) -> str:
    return f"gitlab:{project_id}:{entity_type}:{entity_id}"


def subject_for(entity_type: str, entity_id: str, project_id: str) -> str:
    plural = {
        "merge_request": "merge_requests",
        "pipeline": "pipelines",
    }.get(entity_type, f"{entity_type}s")
    return f"projects/{project_id}/{plural}/{entity_id}"


def parse_event_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def validate_fixture(fixture: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    policy = fixture.get("policy", {})
    for key, expected in {
        "cloud_events_specversion": "1.0",
        "identity_is_source_plus_id": True,
        "preserve_original_envelope": True,
        "preserve_farmaxia_extensions": True,
        "network_allowed": False,
        "human_data": False,
        "external_execution": False,
    }.items():
        if policy.get(key) != expected:
            blockers.append(f"policy_invalid:{key}")

    source = fixture.get("source_of_truth", {})
    project_id = source.get("project_id")
    source_uri = source.get("source_uri")
    parsed_source = urlparse(source_uri or "")
    if source.get("surface") != "gitlab" or not project_id:
        blockers.append("source_identity_incomplete")
    if not parsed_source.scheme or not parsed_source.netloc:
        blockers.append("source_uri_not_absolute")
    if not isinstance(source.get("current_version"), int):
        blockers.append("source_version_authority_missing")

    known_entities = set(source.get("entities", []))
    events = fixture.get("events", [])
    if not events:
        blockers.append("events_missing")
    seen_fingerprints: dict[tuple[str, str], str] = {}
    for index, event in enumerate(events):
        label = event.get("id") or f"index-{index}"
        missing = sorted(REQUIRED_ATTRIBUTES - set(event))
        blockers.extend(f"cloud_event_required_missing:{label}:{key}" for key in missing)
        if event.get("specversion") != "1.0":
            blockers.append(f"cloud_event_specversion_invalid:{label}")
        if not isinstance(event.get("id"), str) or not event.get("id"):
            blockers.append(f"cloud_event_id_invalid:{label}")
        event_source = event.get("source")
        parsed_event_source = urlparse(event_source or "")
        if not parsed_event_source.scheme or not parsed_event_source.netloc:
            blockers.append(f"cloud_event_source_invalid:{label}")
        if event_source != source_uri:
            blockers.append(f"cloud_event_source_mismatch:{label}")
        if not isinstance(event.get("type"), str) or not event.get("type"):
            blockers.append(f"cloud_event_type_invalid:{label}")
        if parse_event_time(event.get("time")) is None:
            blockers.append(f"cloud_event_time_invalid:{label}")
        if event.get("datacontenttype") != "application/json":
            blockers.append(f"cloud_event_content_type_invalid:{label}")
        extensions = {
            key: value
            for key, value in event.items()
            if key not in REQUIRED_ATTRIBUTES
            and key not in {"subject", "time", "datacontenttype", "data"}
        }
        for key in extensions:
            if not EXTENSION_NAME.fullmatch(key):
                blockers.append(f"cloud_event_extension_name_invalid:{label}:{key}")
            if not key.startswith("farmaxia-"):
                blockers.append(f"foreign_extension_not_namespaced:{label}:{key}")
        missing_extensions = sorted(REQUIRED_FARMAXIA_EXTENSIONS - set(extensions))
        blockers.extend(f"farmaxia_extension_missing:{label}:{key}" for key in missing_extensions)

        data = event.get("data")
        if not isinstance(data, dict):
            blockers.append(f"cloud_event_data_invalid:{label}")
            continue
        if data.get("event_id") != event.get("id"):
            blockers.append(f"internal_event_id_mismatch:{label}")
        data_project = data.get("project_id")
        entity_type = data.get("entity_type")
        entity_id = data.get("entity_id")
        expected_ref = entity_ref(data_project or "", entity_type or "", entity_id or "")
        if data_project != project_id or expected_ref not in known_entities:
            blockers.append(f"internal_entity_identity_invalid:{label}")
        if event.get("farmaxia-entity-ref") != expected_ref:
            blockers.append(f"farmaxia_entity_ref_mismatch:{label}")
        if event.get("subject") != subject_for(entity_type or "", entity_id or "", project_id or ""):
            blockers.append(f"cloud_event_subject_mismatch:{label}")
        if not isinstance(data.get("occurred_at"), int):
            blockers.append(f"internal_event_time_missing:{label}")
        if not isinstance(event.get("farmaxia-source-version"), int):
            blockers.append(f"farmaxia_source_version_invalid:{label}")
        elif event["farmaxia-source-version"] > source.get("current_version", -1):
            blockers.append(f"farmaxia_source_version_ahead:{label}")
        if not isinstance(event.get("farmaxia-observed-at"), int):
            blockers.append(f"farmaxia_observed_at_invalid:{label}")
        if not isinstance(event.get("farmaxia-root-id"), str) or not event.get("farmaxia-root-id"):
            blockers.append(f"farmaxia_root_id_invalid:{label}")

        identity = event_identity(event)
        fingerprint = event_fingerprint(event)
        previous = seen_fingerprints.setdefault(identity, fingerprint)
        if previous != fingerprint:
            blockers.append(f"duplicate_identity_conflict:{label}")

    return sorted(set(blockers))


def deduplicate(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, list[str]]:
    unique: list[dict[str, Any]] = []
    seen: dict[tuple[str, str], str] = {}
    duplicates = 0
    conflicts: list[str] = []
    for event in events:
        identity = event_identity(event)
        fingerprint = event_fingerprint(event)
        if identity in seen:
            duplicates += 1
            if seen[identity] != fingerprint:
                conflicts.append(event.get("id", ""))
            continue
        seen[identity] = fingerprint
        unique.append(event)
    return unique, duplicates, sorted(set(conflicts))


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    blockers = validate_fixture(fixture)
    source = fixture.get("source_of_truth", {})
    raw_events = fixture.get("events", [])
    unique_events, duplicate_count, duplicate_conflicts = deduplicate(raw_events)
    canonical_events = sorted(
        unique_events,
        key=lambda event: (event.get("time", ""), event.get("id", "")),
    )
    raw_order = [event.get("id") for event in raw_events]
    canonical_order = [event.get("id") for event in canonical_events]
    if duplicate_conflicts:
        blockers.append("conflicting_duplicate_identity_detected")
    if canonical_order != fixture.get("expected_canonical_order"):
        blockers.append("canonical_order_mismatch")

    normalized_events = []
    for event in canonical_events:
        data = event.get("data", {})
        normalized_events.append({
            "event_id": event.get("id"),
            "source": source.get("surface"),
            "entity_ref": event.get("farmaxia-entity-ref"),
            "source_version": event.get("farmaxia-source-version"),
            "occurred_at": data.get("occurred_at") if isinstance(data, dict) else None,
            "event_kind": data.get("event_kind") if isinstance(data, dict) else None,
            "original_envelope_preserved": True,
        })
    status = "CLOUDEVENTS_ENVELOPE_VERIFIED" if not blockers else "BLOCKED"
    return {
        "experiment": "068-farmaxia-cloudevents-envelope",
        "status": status,
        "blockers": sorted(set(blockers)),
        "envelope": {
            "specversion": "1.0",
            "raw_event_count": len(raw_events),
            "unique_event_count": len(unique_events),
            "duplicate_event_count": duplicate_count,
            "duplicate_conflict_ids": duplicate_conflicts,
            "identity_rule": "source_plus_id",
            "out_of_order_input": raw_order != canonical_order,
            "raw_order": raw_order,
            "canonical_order": canonical_order,
            "normalized_events": normalized_events,
            "original_envelopes_retained": True,
        },
        "compatibility": {
            "maps_to_farmaxia_event_contract": not any(
                blocker.startswith("internal_") or blocker.startswith("farmaxia_")
                for blocker in blockers
            ),
            "source_identity_preserved": all(
                event.get("source") == source.get("source_uri") for event in raw_events
            ),
            "provenance_extensions_preserved": all(
                REQUIRED_FARMAXIA_EXTENSIONS.issubset(event)
                for event in raw_events
            ),
        },
        "safety": {
            "network_used": False,
            "external_execution": False,
            "human_data": False,
            "camera_used": False,
            "source_write_attempted": False,
        },
        "scope_limit": "local synthetic envelope validation; no broker, network, signature, schema registry or production interoperability claim",
    }


def main() -> None:
    print(json.dumps(compile_fixture(load_json(FIXTURE)), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
