"""Map an IRIS editorial composition into a FARMAKSIA representation result.

This is deliberately a semantic adapter: IRIS remains responsible for
composition and its independent verifier; FARMAKSIA receives identity,
ordering, constraints, provenance and the declared solver status.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


ALLOWED_STATUS = {"OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNKNOWN"}
ALLOWED_KINDS = {"work", "record", "context"}


def adapt(plan: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    if plan.get("schemaVersion") != "iris.composition/1":
        blockers.append("composition_schema_invalid")
    status = plan.get("status")
    if status not in ALLOWED_STATUS:
        blockers.append("solver_status_invalid")
    if plan.get("objective", {}).get("aesthetic") is True:
        blockers.append("aesthetic_optimality_not_admitted")

    items = plan.get("items")
    selected_ids = plan.get("selectedIds")
    if not isinstance(items, list) or not isinstance(selected_ids, list):
        blockers.append("composition_items_or_selection_missing")
        items = items if isinstance(items, list) else []
        selected_ids = selected_ids if isinstance(selected_ids, list) else []

    by_id: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not item.get("id"):
            blockers.append("item_identity_missing")
            continue
        item_id = item["id"]
        if item_id in by_id:
            blockers.append(f"duplicate_item:{item_id}")
        by_id[item_id] = item
        if not item.get("sourceId"):
            blockers.append(f"item_source_missing:{item_id}")
        if item.get("kind") not in ALLOWED_KINDS:
            blockers.append(f"item_kind_invalid:{item_id}")

    if len(selected_ids) != len(set(selected_ids)):
        blockers.append("selected_order_contains_duplicates")
    for item_id in selected_ids:
        if item_id not in by_id:
            blockers.append(f"selected_item_missing:{item_id}")
    verification = plan.get("verification", {})
    if verification.get("independent") is not True or verification.get("passed") is not True:
        blockers.append("independent_verification_missing")
    if plan.get("authorialOrder") != selected_ids:
        blockers.append("authorial_order_mismatch")

    ordered = []
    for position, item_id in enumerate(selected_ids, start=1):
        item = by_id.get(item_id, {})
        ordered.append({
            "position": position,
            "id": item_id,
            "sourceId": item.get("sourceId"),
            "kind": item.get("kind"),
            "mediaType": item.get("mediaType"),
            "selected": True,
        })

    result = {
        "kind": "iris.editorial.composition",
        "status": status if status in ALLOWED_STATUS else "UNKNOWN",
        "identity": {
            "projectId": plan.get("projectId"),
            "workId": plan.get("workId"),
            "recordIds": [item.get("sourceId") for item in items if item.get("kind") == "record"],
            "contextIds": [item.get("sourceId") for item in items if item.get("kind") == "context"],
        },
        "ordering": {"mode": "authorial", "items": ordered},
        "constraints": deepcopy(plan.get("constraints", {})),
        "preferences": deepcopy(plan.get("preferences", {})),
        "alternatives": deepcopy(plan.get("alternatives", [])),
        "objective": deepcopy(plan.get("objective", {})),
        "verification": deepcopy(verification),
        "provenance": {
            "source": "iris",
            "sourceVersion": plan.get("sourceVersion"),
            "compositionId": plan.get("compositionId"),
            "fixture": "synthetic",
        },
    }
    result["blockers"] = sorted(set(blockers))
    result["admitted"] = not result["blockers"]
    return result

