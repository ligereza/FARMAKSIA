"""Adapt the local CloudEvents envelope into the existing cross-app contract."""

from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIXTURE = HERE / "fixture.json"
CLOUD_FIXTURE = ROOT / "experiments/068-farmaxia-cloudevents-envelope/fixture.json"
BRIDGE_RUNNER = ROOT / "experiments/065-farmaxia-cross-application-evidence/run_experiment.py"
CLOUD_RUNNER = ROOT / "experiments/068-farmaxia-cloudevents-envelope/run_experiment.py"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def envelope_to_bridge_fixture(envelope_fixture: dict[str, Any], adapter_fixture: dict[str, Any]) -> dict[str, Any]:
    project_id = adapter_fixture["source_of_truth"]["project"]["id"]
    events = []
    for event in envelope_fixture.get("events", []):
        data = event.get("data", {})
        if not isinstance(data, dict):
            continue
        events.append({
            "event_id": event.get("id"),
            "delivery_id": event.get("farmaxia-delivery-id", f"adapted-{event.get('id')}"),
            "source": envelope_fixture["source_of_truth"]["surface"],
            "project_id": data.get("project_id"),
            "entity_type": data.get("entity_type"),
            "entity_id": data.get("entity_id"),
            "source_version": event.get("farmaxia-source-version"),
            "occurred_at": data.get("occurred_at"),
            "payload": data.get("payload", {}),
        })
    return {
        "schema": "farmaxia:cross-application-evidence:0.1",
        "source_of_truth": {
            "surface": adapter_fixture["source_of_truth"]["surface"],
            "instance_id": "gitlab-lab",
            "project": deepcopy(adapter_fixture["source_of_truth"]["project"]),
            "entities": deepcopy(adapter_fixture["source_of_truth"]["entities"]),
        },
        "events": events,
        "mattermost_surface": deepcopy(adapter_fixture["mattermost_surface"]),
        "representation_claims": deepcopy(adapter_fixture["representation_claims"]),
        "action": deepcopy(adapter_fixture["action"]),
        "policy": deepcopy(adapter_fixture["policy"]),
    }


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    cloud_runner = load_module("farmaxia_cloud_events_068", CLOUD_RUNNER)
    bridge_runner = load_module("farmaxia_bridge_065", BRIDGE_RUNNER)
    envelope_fixture = load_json(CLOUD_FIXTURE)
    envelope_result = cloud_runner.compile_fixture(envelope_fixture)
    blockers: list[str] = []
    declared_input = fixture.get("adapter", {}).get("input_envelope")
    expected_input = "experiments/068-farmaxia-cloudevents-envelope/fixture.json"
    if declared_input != expected_input:
        blockers.append("input_envelope_declaration_mismatch")
    if envelope_result["status"] != "CLOUDEVENTS_ENVELOPE_VERIFIED":
        blockers.append("input_envelope_not_verified")

    expected_event_ids = set(fixture.get("adapter", {}).get("required_event_ids", []))
    actual_event_ids = {
        event.get("id")
        for event in envelope_fixture.get("events", [])
        if event.get("id")
    }
    if not expected_event_ids.issubset(actual_event_ids):
        blockers.append("required_input_event_missing")

    bridge_fixture = envelope_to_bridge_fixture(envelope_fixture, fixture)
    bridge_result = bridge_runner.compile_fixture(bridge_fixture)
    if bridge_result["status"] != "CROSS_APPLICATION_EVIDENCE_VERIFIED":
        blockers.append("mapped_bridge_contract_not_verified")
    if bridge_result["ingestion"]["canonical_order"] != fixture["expected"]["canonical_order"]:
        blockers.append("adapter_changed_canonical_order")
    if bridge_result["action_proposal"]["status"] != fixture["expected"]["action_status"]:
        blockers.append("adapter_changed_action_safety")

    mapped_ids = [event["event_id"] for event in bridge_result["ingestion"]["normalized_events"]]
    if mapped_ids != fixture["expected"]["canonical_order"]:
        blockers.append("adapter_lost_event_identity")
    if not bridge_result["semantic_model"]["identity_is_project_qualified"]:
        blockers.append("adapter_lost_project_identity")
    if not bridge_result["semantic_model"]["representation"]["source_refs"]:
        blockers.append("adapter_lost_provenance")

    status = "CROSS_APPLICATION_CLOUDEVENTS_ADAPTER_VERIFIED" if not blockers else "BLOCKED"
    return {
        "experiment": "069-farmaxia-cloudevents-cross-application-adapter",
        "status": status,
        "blockers": sorted(set(blockers)),
        "input_envelope": {
            "status": envelope_result["status"],
            "raw_event_count": envelope_result["envelope"]["raw_event_count"],
            "unique_event_count": envelope_result["envelope"]["unique_event_count"],
            "duplicate_event_count": envelope_result["envelope"]["duplicate_event_count"],
            "canonical_order": envelope_result["envelope"]["canonical_order"],
            "original_envelopes_retained": envelope_result["envelope"]["original_envelopes_retained"],
        },
        "adapter": {
            "mapping": fixture["adapter"]["mapping"],
            "destination": fixture["adapter"]["destination_surface"],
            "normalized_event_ids": mapped_ids,
            "source_identity_preserved": bridge_result["semantic_model"]["identity_is_project_qualified"],
            "provenance_preserved": bool(bridge_result["semantic_model"]["representation"]["source_refs"]),
        },
        "bridge": {
            "status": bridge_result["status"],
            "action_status": bridge_result["action_proposal"]["status"],
            "verification": bridge_result["independent_verification"],
        },
        "safety": {
            "network_used": False,
            "external_execution": False,
            "human_data": False,
            "camera_used": False,
            "source_write_attempted": False,
        },
        "scope_limit": "local synthetic CloudEvents adapter; reuses 065 compiler and does not claim live API interoperability",
    }


def main() -> None:
    print(json.dumps(compile_fixture(load_json(FIXTURE)), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
