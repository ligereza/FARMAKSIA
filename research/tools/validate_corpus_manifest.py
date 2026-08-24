"""Validate the provenance and authority fields of a FARMAKSIA corpus manifest."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlparse


ALLOWED_STATUS = {"candidate", "accepted", "rejected"}
ALLOWED_AUTHORITY = {"self_created", "public_license", "permission_documented", "research_only"}
REQUIRED_ENTRY_FIELDS = {
    "id",
    "status",
    "format",
    "source_uri",
    "license_uri",
    "license_verified",
    "authority",
    "sha256",
    "declared_query",
    "representations",
    "residue",
}


def fail(message: str) -> None:
    raise ValueError(message)


def is_uri(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate(manifest_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "farmaxia:corpus-manifest:0.1":
        fail("unsupported schema")
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        fail("entries must be a list")
    ids = [entry.get("id") for entry in entries]
    if any(not isinstance(identifier, str) or not identifier for identifier in ids):
        fail("every entry needs a non-empty id")
    if len(ids) != len(set(ids)):
        fail("duplicate entry id")

    for entry in entries:
        missing = REQUIRED_ENTRY_FIELDS - set(entry)
        if missing:
            fail(f"{entry.get('id')}: missing fields {sorted(missing)}")
        if entry["status"] not in ALLOWED_STATUS:
            fail(f"{entry['id']}: invalid status")
        if entry["authority"] not in ALLOWED_AUTHORITY:
            fail(f"{entry['id']}: invalid authority")
        if not is_uri(entry["source_uri"]):
            fail(f"{entry['id']}: source_uri must be an https/http URI")
        if not is_uri(entry["license_uri"]):
            fail(f"{entry['id']}: license_uri must be an https/http URI")
        if not isinstance(entry["license_verified"], bool):
            fail(f"{entry['id']}: license_verified must be boolean")
        if entry["status"] == "accepted" and not entry["license_verified"]:
            fail(f"{entry['id']}: accepted entries require verified license")
        if not isinstance(entry["sha256"], str) or len(entry["sha256"]) != 64 or any(char not in "0123456789abcdefABCDEF" for char in entry["sha256"]):
            fail(f"{entry['id']}: sha256 must be 64 hexadecimal characters")
        for field in ("representations", "residue"):
            if not isinstance(entry[field], list) or not entry[field] or any(not isinstance(value, str) or not value for value in entry[field]):
                fail(f"{entry['id']}: {field} must be a non-empty string list")
        if not isinstance(entry["declared_query"], str) or not entry["declared_query"].strip():
            fail(f"{entry['id']}: declared_query must be non-empty")
        local_path = entry.get("local_path")
        if local_path is not None:
            path = manifest_path.parent / local_path
            if not path.is_file():
                fail(f"{entry['id']}: local_path does not exist")
            actual = hashlib.sha256(path.read_bytes()).hexdigest().upper()
            if actual != entry["sha256"].upper():
                fail(f"{entry['id']}: local_path hash mismatch")

    return len(entries)


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("research/corpus/manifest.json")
    try:
        count = validate(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"CORPUS_INVALID: {exc}")
    print("CORPUS_VALID")
    print(f"entries={count}")


if __name__ == "__main__":
    main()
