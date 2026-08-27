"""Test watermark handling, late events and causal-pending replay."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def event_fingerprint(event: dict[str, Any]) -> str:
    comparable = {key: value for key, value in event.items() if key not in {"delivery_id", "observed_at"}}
    encoded = json.dumps(comparable, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def event_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [message for message in messages if message.get("kind") == "event"]


def validate_fixture(fixture: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    source = fixture.get("source_of_truth", {})
    policy = fixture.get("policy", {})
    for key, expected in {
        "late_event_policy": "append_and_replay",
        "watermark_must_be_monotone": True,
        "causal_parent_required": True,
        "unknown_on_missing_causal_parent": True,
        "conflicts_are_not_success": True,
        "network_allowed": False,
        "human_data": False,
    }.items():
        if policy.get(key) != expected:
            blockers.append(f"policy_invalid:{key}")
    if source.get("surface") != "gitlab" or not source.get("project_id") or not isinstance(source.get("current_version"), int):
        blockers.append("source_identity_invalid")
    known_entities = set(source.get("entities", []))
    messages = fixture.get("messages", [])
    if not messages:
        blockers.append("messages_missing")
    watermarks = []
    ids = set()
    for message in messages:
        message_id = message.get("message_id")
        if not message_id:
            blockers.append("message_id_missing")
        if message.get("kind") == "watermark":
            if not isinstance(message.get("watermark"), int) or not isinstance(message.get("observed_at"), int):
                blockers.append(f"watermark_contract_invalid:{message_id}")
            else:
                watermarks.append(message["watermark"])
            continue
        if message.get("kind") != "event":
            blockers.append(f"message_kind_invalid:{message_id}")
            continue
        event_id = message_id
        if event_id in ids and event_fingerprint(message) not in {event_fingerprint(item) for item in messages if item.get("message_id") == event_id}:
            blockers.append(f"duplicate_event_conflict:{event_id}")
        ids.add(event_id)
        if message.get("source") != source.get("surface") or message.get("project_id") != source.get("project_id"):
            blockers.append(f"event_source_identity_invalid:{event_id}")
        if message.get("entity_ref") not in known_entities:
            blockers.append(f"event_entity_unknown:{event_id}")
        if message.get("event_type") != "set" or not message.get("root_id") or not message.get("field"):
            blockers.append(f"event_contract_invalid:{event_id}")
        if not isinstance(message.get("source_version"), int) or not isinstance(message.get("event_time"), int) or not isinstance(message.get("observed_at"), int):
            blockers.append(f"event_temporal_authority_invalid:{event_id}")
        elif message["source_version"] > source.get("current_version", -1):
            blockers.append(f"source_version_ahead:{event_id}")
        if "value" not in message.get("payload", {}):
            blockers.append(f"event_value_missing:{event_id}")
        if not isinstance(message.get("parents"), list) or not isinstance(message.get("supersedes"), list):
            blockers.append(f"causal_fields_invalid:{event_id}")
    if watermarks != sorted(watermarks):
        blockers.append("watermark_not_monotone")
    event_ids = {message.get("message_id") for message in event_messages(messages)}
    for event in event_messages(messages):
        missing_parents = [parent for parent in event.get("parents", []) if parent not in event_ids]
        if missing_parents and event.get("expected_status") != "UNKNOWN":
            blockers.append(f"causal_parent_not_in_fixture:{event.get('message_id')}")
        missing_superseded = [target for target in event.get("supersedes", []) if target not in event_ids]
        if missing_superseded:
            blockers.append(f"superseded_event_not_in_fixture:{event.get('message_id')}")
    expected = fixture.get("expected_projection", [])
    expected_keys = [(item.get("entity_ref"), item.get("field")) for item in expected]
    if not expected or len(expected_keys) != len(set(expected_keys)):
        blockers.append("expected_projection_invalid")
    return sorted(set(blockers))


def deduplicate(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, list[str]]:
    unique: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    duplicates = 0
    conflicts: list[str] = []
    for event in events:
        event_id = event["message_id"]
        fingerprint = event_fingerprint(event)
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
    by_id = {event["message_id"]: event for event in unique}
    superseded_ids = {target for event in unique for target in event.get("supersedes", [])}
    history = []
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    unknowns = []
    for event in sorted(unique, key=lambda item: item["message_id"]):
        missing_parents = [parent for parent in event.get("parents", []) if parent not in by_id]
        if missing_parents:
            status = "UNKNOWN"
            reason = "causal_parent_not_observed"
            unknowns.append({
                "entity_ref": event["entity_ref"],
                "field": event["field"],
                "status": "UNKNOWN",
                "value": None,
                "source_version": event.get("source_version"),
                "source_refs": [event["message_id"]],
                "conflicting_values": [],
                "reason": reason,
            })
        elif event["message_id"] in superseded_ids:
            status = "SUPERSEDED"
            reason = "replaced_by_newer_source_observation"
        else:
            status = "ACTIVE"
            reason = None
            groups.setdefault((event["entity_ref"], event["field"]), []).append(event)
        history.append({
            "event_id": event["message_id"],
            "entity_ref": event["entity_ref"],
            "field": event["field"],
            "source_version": event.get("source_version"),
            "event_time": event.get("event_time"),
            "observed_at": event.get("observed_at"),
            "status": status,
            "reason": reason,
        })

    projection = []
    for entity_ref, field in sorted(groups):
        candidates = groups[(entity_ref, field)]
        by_version: dict[int, list[dict[str, Any]]] = {}
        for event in candidates:
            by_version.setdefault(event["source_version"], []).append(event)
        newest_version = max(by_version)
        newest = by_version[newest_version]
        values = sorted({json.dumps(event["payload"]["value"], sort_keys=True) for event in newest})
        refs = sorted(event["message_id"] for event in newest)
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
    projection.extend(unknowns)
    projection.sort(key=lambda item: (item["entity_ref"], item["field"]))
    return {
        "unique_events": len(unique),
        "duplicate_events": duplicate_count,
        "duplicate_conflicts": sorted(duplicate_conflicts),
        "event_ids": sorted(by_id),
        "superseded_ids": sorted(superseded_ids),
        "history": history,
        "projection": projection,
        "unknowns": unknowns,
    }


def projection_signature(result: dict[str, Any]) -> str:
    return json.dumps(result["projection"], sort_keys=True, separators=(",", ":"))


def projection_item(result: dict[str, Any], entity_ref: str, field: str) -> dict[str, Any] | None:
    return next((item for item in result["projection"] if item["entity_ref"] == entity_ref and item["field"] == field), None)


def expected_matches(projection: list[dict[str, Any]], expected: list[dict[str, Any]]) -> bool:
    actual = [{key: item.get(key) for key in ("entity_ref", "field", "status", "value")} for item in projection]
    wanted = [{key: item.get(key) for key in ("entity_ref", "field", "status", "value")} for item in expected]
    return actual == sorted(wanted, key=lambda item: (item["entity_ref"], item["field"]))


def process_stream(messages: list[dict[str, Any]]) -> dict[str, Any]:
    accepted: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    current_watermark: int | None = None
    late_ids: list[str] = []
    pending_ids: set[str] = set()
    resolved_pending_ids: set[str] = set()
    snapshots = []
    duplicate_count = 0
    for message in messages:
        if message.get("kind") == "watermark":
            current_watermark = message["watermark"]
            replayed = replay(accepted)
            snapshots.append({
                "message_id": message["message_id"],
                "kind": "watermark",
                "watermark": current_watermark,
                "late": False,
                "duplicate": False,
                "pipeline_status": (projection_item(replayed, "gitlab:proj-alpha:pipeline:pipe-3", "status") or {}).get("value"),
                "deployment_status": (projection_item(replayed, "gitlab:proj-alpha:deployment:deploy-9", "status") or {}).get("status"),
                "review_status": (projection_item(replayed, "gitlab:proj-alpha:review_note:note-1", "state") or {}).get("value"),
                "causal_pending_ids": sorted(pending_ids),
            })
            continue
        event_id = message["message_id"]
        if event_id in seen_ids:
            duplicate_count += 1
            snapshots.append({
                "message_id": event_id,
                "kind": "event",
                "watermark": current_watermark,
                "late": current_watermark is not None and message["event_time"] < current_watermark,
                "duplicate": True,
                "pipeline_status": None,
                "deployment_status": None,
                "review_status": None,
                "causal_pending_ids": sorted(pending_ids),
            })
            continue
        seen_ids.add(event_id)
        late = current_watermark is not None and message["event_time"] < current_watermark
        if late:
            late_ids.append(event_id)
        accepted.append(message)
        replayed = replay(accepted)
        current_pending = {item["event_id"] for item in replayed["history"] if item["status"] == "UNKNOWN" and item["reason"] == "causal_parent_not_observed"}
        resolved_pending_ids.update(pending_ids - current_pending)
        pending_ids = current_pending
        snapshots.append({
            "message_id": event_id,
            "kind": "event",
            "watermark": current_watermark,
            "event_time": message["event_time"],
            "late": late,
            "duplicate": False,
            "replay_triggered": late,
            "pipeline_status": (projection_item(replayed, "gitlab:proj-alpha:pipeline:pipe-3", "status") or {}).get("value"),
            "deployment_status": (projection_item(replayed, "gitlab:proj-alpha:deployment:deploy-9", "status") or {}).get("status"),
            "review_status": (projection_item(replayed, "gitlab:proj-alpha:review_note:note-1", "state") or {}).get("value"),
            "causal_pending_ids": sorted(pending_ids),
        })
    return {
        "accepted_events": accepted,
        "unique_event_count": len(accepted),
        "duplicate_event_count": duplicate_count,
        "late_event_ids": sorted(late_ids),
        "snapshots": snapshots,
        "pending_causal_ids": sorted(pending_ids),
        "resolved_pending_ids": sorted(resolved_pending_ids),
        "final_watermark": current_watermark,
    }


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    blockers = validate_fixture(fixture)
    if blockers:
        return {
            "experiment": "067-farmaxia-watermark-late-event-replay",
            "status": "BLOCKED",
            "blockers": blockers,
            "safety": {"network_used": False, "external_execution": False, "human_data": False, "camera_used": False, "source_write_attempted": False},
        }
    messages = fixture["messages"]
    stream = process_stream(messages)
    final = replay(stream["accepted_events"])
    _, _, duplicate_conflicts = deduplicate(event_messages(messages))
    if duplicate_conflicts:
        blockers.append("conflicting_duplicate_delivery")
    signatures = [
        projection_signature(replay(stream["accepted_events"])),
        projection_signature(replay(list(reversed(stream["accepted_events"]))),),
        projection_signature(replay(sorted(stream["accepted_events"], key=lambda item: (item["event_time"], item["message_id"]))),),
    ]
    if stream["late_event_ids"] and not any(snapshot.get("replay_triggered") for snapshot in stream["snapshots"]):
        blockers.append("late_event_replay_not_triggered")
    if len(set(signatures)) != 1:
        blockers.append("batch_replay_order_changed_projection")
    if not expected_matches(final["projection"], fixture.get("expected_projection", [])):
        blockers.append("projection_expectation_mismatch")
    before_late = next((snapshot for snapshot in stream["snapshots"] if snapshot["message_id"] == "wm-300"), None)
    after_late = next((snapshot for snapshot in stream["snapshots"] if snapshot["message_id"] == "ev-pipeline-failed-correction"), None)
    if not before_late or before_late.get("pipeline_status") != "success":
        blockers.append("pre_late_provisional_state_missing")
    if not after_late or after_late.get("pipeline_status") != "failed":
        blockers.append("late_correction_did_not_reopen_projection")
    history = {item["event_id"]: item for item in final["history"]}
    if history.get("ev-pipeline-success", {}).get("status") != "SUPERSEDED":
        blockers.append("supersession_history_not_preserved")
    if "ev-review-child" not in stream["resolved_pending_ids"]:
        blockers.append("causal_pending_event_not_resolved")
    deployment = projection_item(final, "gitlab:proj-alpha:deployment:deploy-9", "status")
    if not deployment or deployment.get("status") != "CONFLICT" or deployment.get("value") is not None:
        blockers.append("late_conflict_not_exposed")
    approval = projection_item(final, "gitlab:proj-alpha:merge_request:mr-7:approval", "approved")
    if not approval or approval.get("status") != "UNKNOWN":
        blockers.append("missing_causal_authority_not_unknown")
    status = "WATERMARK_LATE_REPLAY_VERIFIED" if not blockers else "BLOCKED"
    return {
        "experiment": "067-farmaxia-watermark-late-event-replay",
        "status": status,
        "blockers": sorted(set(blockers)),
        "stream": {
            "raw_message_count": len(messages),
            "watermark_count": sum(1 for message in messages if message.get("kind") == "watermark"),
            "raw_event_count": len(event_messages(messages)),
            "unique_event_count": stream["unique_event_count"],
            "duplicate_event_count": stream["duplicate_event_count"],
            "late_event_ids": stream["late_event_ids"],
            "late_event_count": len(stream["late_event_ids"]),
            "final_watermark": stream["final_watermark"],
            "watermark_monotone": [message["watermark"] for message in messages if message.get("kind") == "watermark"] == sorted(message["watermark"] for message in messages if message.get("kind") == "watermark"),
            "late_policy": fixture["policy"]["late_event_policy"],
            "snapshots": stream["snapshots"],
        },
        "causal": {
            "pending_resolved_ids": stream["resolved_pending_ids"],
            "unresolved_ids": stream["pending_causal_ids"],
            "final_unknowns": final["unknowns"],
        },
        "replay": {
            "batch_permutation_count": len(signatures),
            "all_batch_projection_signatures_equal": len(set(signatures)) == 1,
            "final_projection_equals_batch_replay": projection_signature(final) == signatures[0],
            "projection": final["projection"],
            "history": final["history"],
            "superseded_event_ids": final["superseded_ids"],
        },
        "safety": {"network_used": False, "external_execution": False, "human_data": False, "camera_used": False, "source_write_attempted": False},
        "scope_limit": "synthetic finite stream; no claim of distributed consensus, exactly-once delivery or production watermark semantics",
    }


def main() -> None:
    print(json.dumps(compile_fixture(load_json(FIXTURE)), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
