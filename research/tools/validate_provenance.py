"""Validate a FARMAKSIA provenance manifest using only the standard library."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ALLOWED_AUTHORITY = {
    "human_declared_fixture",
    "human_declared_tool",
    "human_declared_control",
    "human_declared",
    "human_declared_hypothesis",
    "human_reviewed_record",
    "computed",
    "computed_plus_external_input",
    "computed_plus_declared_control",
    "experiment_defined",
}


def invalid(message: str) -> None:
    raise ValueError(message)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def validate(manifest_path: Path) -> tuple[int, int, int]:
    root = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key in ("schema", "agents", "entities", "activities", "queries", "unknowns"):
        if key not in manifest:
            invalid(f"missing top-level key: {key}")

    groups = [manifest["agents"], manifest["entities"], manifest["activities"], manifest["queries"]]
    ids = [item["id"] for group in groups for item in group]
    if len(ids) != len(set(ids)):
        invalid("duplicate identifier")
    known = set(ids)

    for entity in manifest["entities"]:
        if entity.get("authority") not in ALLOWED_AUTHORITY:
            invalid(f"unknown authority on {entity.get('id')}")
        if entity.get("path"):
            path = root / entity["path"]
            if not path.is_file():
                invalid(f"missing file for {entity['id']}: {entity['path']}")
            if entity.get("sha256") and file_hash(path) != entity["sha256"]:
                invalid(f"hash mismatch for {entity['id']}")
        for ref in entity.get("derived_from", []) + entity.get("preserves", []) + entity.get("enables", []):
            if ref not in known:
                invalid(f"unknown entity reference {ref} from {entity['id']}")

    for activity in manifest["activities"]:
        if activity.get("agent") not in known:
            invalid(f"unknown agent on {activity['id']}")
        for ref in activity.get("used", []) + activity.get("generated", []):
            if ref not in known:
                invalid(f"unknown activity reference {ref} from {activity['id']}")

    for query in manifest["queries"]:
        if query.get("authority") not in ALLOWED_AUTHORITY:
            invalid(f"unknown query authority on {query['id']}")
        for ref in query.get("required_entities", []):
            if ref not in known:
                invalid(f"unknown query entity reference {ref}")

    return len(manifest["entities"]), len(manifest["activities"]), len(manifest["queries"])


def main() -> None:
    manifest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("provenance.json")
    try:
        entities, activities, queries = validate(manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"PROVENANCE_INVALID: {exc}")
        raise SystemExit(1)
    print("PROVENANCE_VALID")
    print(f"entities={entities} activities={activities} queries={queries}")


if __name__ == "__main__":
    main()
