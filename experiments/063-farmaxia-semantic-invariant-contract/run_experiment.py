"""Check semantic query preservation across RepresentationSpace views."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.json"


def normalized(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalized(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return sorted((normalized(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True))
    return value


def relation_records(state: dict[str, Any]) -> list[dict[str, Any]]:
    if "relations" in state:
        return state["relations"]
    return state.get("relation_records", [])


def answer_query(state: dict[str, Any], query: dict[str, Any]) -> Any:
    kind = query["kind"]
    if kind == "active_entity":
        return state.get("active_entity")
    if kind == "entity_set":
        return state.get("entity_refs") or [item["stable_ref"] for item in state.get("entities", [])]
    if kind == "unknown_set":
        unknowns = state.get("unknowns", [])
        return [item if isinstance(item, str) else item["stable_ref"] for item in unknowns]
    if kind == "alternative_set":
        return state.get("alternatives", [])
    if kind == "relation_between":
        return [
            {"stable_ref": item["stable_ref"], "from": item["from"], "to": item["to"], "kind": item["kind"]}
            for item in relation_records(state)
            if item.get("from") == query["from"] and item.get("to") == query["to"]
        ]
    if kind == "provenance":
        return [item.get("source_ref", item.get("stable_ref")) for item in relation_records(state) if item.get("stable_ref") == query["target"]]
    raise ValueError(f"unsupported query kind: {kind}")


def validate_source(source: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    entity_refs = {item.get("stable_ref") for item in source.get("entities", [])}
    relation_refs: set[str] = set()
    for relation in source.get("relations", []):
        relation_refs.add(relation.get("stable_ref"))
        if relation.get("from") not in entity_refs or relation.get("to") not in entity_refs:
            blockers.append(f"source_relation_endpoint_unknown:{relation.get('stable_ref')}")
    if len(entity_refs) != len(source.get("entities", [])):
        blockers.append("source_entity_refs_not_unique")
    if len(relation_refs) != len(source.get("relations", [])):
        blockers.append("source_relation_refs_not_unique")
    if not source.get("unknowns"):
        blockers.append("source_unknowns_missing")
    return blockers


def validate_view(view: dict[str, Any], source: dict[str, Any], queries: list[dict[str, Any]]) -> dict[str, Any]:
    blockers: list[str] = []
    source_entities = {item["stable_ref"] for item in source["entities"]}
    source_relations = {item["stable_ref"]: item for item in source["relations"]}
    source_unknowns = {item["stable_ref"] for item in source["unknowns"]}
    view_entities = set(view.get("entity_refs", []))
    if view_entities != source_entities:
        blockers.append("entity_set_not_preserved")
    if set(view.get("unknowns", [])) != source_unknowns:
        blockers.append("unknown_set_not_preserved")
    if set(view.get("alternatives", [])) != set(source.get("alternatives", [])):
        blockers.append("alternative_set_not_preserved")
    for relation in relation_records(view):
        source_relation = source_relations.get(relation.get("stable_ref"))
        if source_relation is None:
            blockers.append(f"semantic_hallucination:{relation.get('stable_ref')}")
            continue
        for key in ("from", "to", "kind"):
            if relation.get(key) != source_relation.get(key):
                blockers.append(f"relation_changed:{relation.get('stable_ref')}:{key}")
        if relation.get("source_ref") != relation.get("stable_ref"):
            blockers.append(f"relation_provenance_missing:{relation.get('stable_ref')}")
    for claim in view.get("claims", []):
        if claim.get("subject") in source_unknowns and claim.get("state") != "unknown":
            blockers.append(f"unknown_escalated:{claim.get('subject')}")
        if not claim.get("source_ref"):
            blockers.append(f"claim_provenance_missing:{claim.get('subject')}")
    source_answers = {query["id"]: normalized(answer_query(source, query)) for query in queries}
    mismatches = []
    for query in queries:
        view_answer = normalized(answer_query(view, query))
        if view_answer != source_answers[query["id"]]:
            mismatches.append(query["id"])
            blockers.append(f"query_not_preserved:{query['id']}")
    return {
        "id": view.get("id"),
        "projection": view.get("projection"),
        "status": "verified" if not blockers else "blocked",
        "blockers": blockers,
        "queries_preserved": len(queries) - len(mismatches),
        "queries_total": len(queries),
        "mismatched_queries": mismatches,
        "provenance_complete": not any("provenance" in item for item in blockers),
    }


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    source = fixture.get("source", {})
    queries = fixture.get("queries", [])
    blockers = validate_source(source)
    view_results = [validate_view(view, source, queries) for view in fixture.get("views", [])]
    for result in view_results:
        blockers.extend(f"{result['id']}:{item}" for item in result["blockers"])
    total_queries = len(queries) * max(1, len(view_results))
    preserved_queries = sum(item["queries_preserved"] for item in view_results)
    relation_count = sum(len(relation_records(view)) for view in fixture.get("views", []))
    hallucinations = sum(sum("semantic_hallucination" in item for item in result["blockers"]) for result in view_results)
    escalations = sum(sum("unknown_escalated" in item for item in result["blockers"]) for result in view_results)
    provenance_complete = sum(result["provenance_complete"] for result in view_results) / max(1, len(view_results))
    return {
        "experiment": "063-farmaxia-semantic-invariant-contract",
        "status": "SEMANTIC_INVARIANT_CONTRACT_VERIFIED" if not blockers else "BLOCKED",
        "blockers": blockers,
        "metrics": {
            "view_count": len(view_results),
            "query_count": len(queries),
            "query_preservation_rate": preserved_queries / max(1, total_queries),
            "semantic_hallucination_rate": hallucinations / max(1, relation_count),
            "unknown_escalation_rate": escalations / max(1, len(view_results)),
            "provenance_completeness": provenance_complete,
            "round_trip_loss": None,
            "critical_queries_require_exact_match": True,
        },
        "views": view_results,
        "editable": fixture.get("editable") is True,
        "execution_allowed": False,
        "external_execution": False,
        "human_data": fixture.get("human_data") is True,
        "camera_used": False,
        "network_used": False,
        "scope_limit": "query-relative semantic preservation in a synthetic fixture; no claim of human comprehension or view quality",
    }


def main() -> None:
    print(json.dumps(compile_fixture(json.loads(FIXTURE.read_text(encoding="utf-8"))), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
