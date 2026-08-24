"""Validate the local, PROV-inspired provenance manifest for Experiment 001."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).parent
MANIFEST = ROOT / "provenance.json"
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


def fail(message: str) -> None:
    raise SystemExit(f"PROVENANCE_INVALID: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest().upper()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for key in ("schema", "agents", "entities", "activities", "queries", "unknowns"):
        if key not in manifest:
            fail(f"missing top-level key: {key}")

    groups = [manifest["agents"], manifest["entities"], manifest["activities"], manifest["queries"]]
    ids = [item["id"] for group in groups for item in group]
    if len(ids) != len(set(ids)):
        fail("duplicate identifier")
    known = set(ids)

    for entity in manifest["entities"]:
        if entity.get("authority") not in ALLOWED_AUTHORITY:
            fail(f"unknown authority on {entity.get('id')}")
        path = entity.get("path")
        if path:
            file_path = ROOT / path
            if not file_path.is_file():
                fail(f"missing file for {entity['id']}: {path}")
            expected = entity.get("sha256")
            if expected and sha256(file_path) != expected:
                fail(f"hash mismatch for {entity['id']}")
        for ref in entity.get("derived_from", []) + entity.get("preserves", []) + entity.get("enables", []):
            if ref not in known:
                fail(f"unknown entity reference {ref} from {entity['id']}")

    for activity in manifest["activities"]:
        if activity.get("agent") not in known:
            fail(f"unknown agent on {activity['id']}")
        for ref in activity.get("used", []) + activity.get("generated", []):
            if ref not in known:
                fail(f"unknown activity reference {ref} from {activity['id']}")

    for query in manifest["queries"]:
        if query.get("authority") not in ALLOWED_AUTHORITY:
            fail(f"unknown query authority on {query['id']}")
        for ref in query.get("required_entities", []):
            if ref not in known:
                fail(f"unknown query entity reference {ref}")

    print("PROVENANCE_VALID")
    print(f"entities={len(manifest['entities'])} activities={len(manifest['activities'])} queries={len(manifest['queries'])}")


if __name__ == "__main__":
    main()
