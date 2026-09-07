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


class ProvenanceInvalid(ValueError):
    """Every defect found in one manifest, not only the first one.

    Reporting a single defect per run understates how far a manifest has
    drifted: refreshing one stale hash only uncovers the next one. The message
    of a single-defect failure is unchanged, so a caller that records
    `str(exc)` keeps the output it had before.
    """

    def __init__(self, defects: list[str]) -> None:
        super().__init__("; ".join(defects))
        self.defects = list(defects)


def invalid(message: str) -> None:
    raise ProvenanceInvalid([message])


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def validate(manifest_path: Path) -> tuple[int, int, int]:
    root = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    missing = [
        key
        for key in ("schema", "agents", "entities", "activities", "queries", "unknowns")
        if key not in manifest
    ]
    if missing:
        raise ProvenanceInvalid([f"missing top-level key: {key}" for key in missing])

    groups = {
        "agents": manifest["agents"],
        "entities": manifest["entities"],
        "activities": manifest["activities"],
        "queries": manifest["queries"],
    }
    ids: list[str] = []
    unidentified: list[str] = []
    for group_name, group in groups.items():
        for position, item in enumerate(group):
            identifier = item.get("id") if isinstance(item, dict) else None
            if not isinstance(identifier, str) or not identifier.strip():
                unidentified.append(f"missing id on {group_name}[{position}]")
                continue
            ids.append(identifier)
    if unidentified:
        raise ProvenanceInvalid(unidentified)

    defects: list[str] = []
    if len(ids) != len(set(ids)):
        defects.append("duplicate identifier")
    known = set(ids)

    for entity in manifest["entities"]:
        if entity.get("authority") not in ALLOWED_AUTHORITY:
            defects.append(f"unknown authority on {entity.get('id')}")
        if entity.get("path"):
            path = root / entity["path"]
            if not path.is_file():
                defects.append(f"missing file for {entity['id']}: {entity['path']}")
            elif entity.get("sha256") and file_hash(path) != entity["sha256"]:
                defects.append(f"hash mismatch for {entity['id']}")
        for ref in entity.get("derived_from", []) + entity.get("preserves", []) + entity.get("enables", []):
            if ref not in known:
                defects.append(f"unknown entity reference {ref} from {entity['id']}")

    for activity in manifest["activities"]:
        if activity.get("agent") not in known:
            defects.append(f"unknown agent on {activity['id']}")
        for ref in activity.get("used", []) + activity.get("generated", []):
            if ref not in known:
                defects.append(f"unknown activity reference {ref} from {activity['id']}")

    for query in manifest["queries"]:
        if query.get("authority") not in ALLOWED_AUTHORITY:
            defects.append(f"unknown query authority on {query['id']}")
        for ref in query.get("required_entities", []):
            if ref not in known:
                defects.append(f"unknown query entity reference {ref}")

    if defects:
        raise ProvenanceInvalid(defects)
    return len(manifest["entities"]), len(manifest["activities"]), len(manifest["queries"])


def main() -> None:
    manifest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("provenance.json")
    try:
        entities, activities, queries = validate(manifest)
    except ProvenanceInvalid as exc:
        for defect in exc.defects:
            print(f"PROVENANCE_INVALID: {defect}")
        raise SystemExit(1)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"PROVENANCE_INVALID: {exc}")
        raise SystemExit(1)
    print("PROVENANCE_VALID")
    print(f"entities={entities} activities={activities} queries={queries}")


if __name__ == "__main__":
    main()
