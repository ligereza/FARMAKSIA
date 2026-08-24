"""Verify information parity across the three VIZZ study conditions."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).parent
SOURCE = ROOT / "decision-state.json"
MANIFEST = ROOT / "conditions" / "manifest.json"


def canonical_branches(state: dict) -> list[dict]:
    return sorted(state["branches"], key=lambda branch: branch["id"])


def signature(branches: list[dict]) -> str:
    payload = json.dumps(branches, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def fail(message: str) -> None:
    raise SystemExit(f"CONDITIONS_INVALID: {message}")


def main() -> None:
    state = json.loads(SOURCE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    branches = canonical_branches(state)
    expected_signature = signature(branches)
    if manifest["data_signature"] != expected_signature:
        fail("manifest signature does not match source fixture")

    for condition in manifest["conditions"]:
        path = ROOT / "conditions" / condition["path"]
        if not path.is_file():
            fail(f"missing condition: {condition['id']}")
        content = path.read_text(encoding="utf-8")
        if content.count(expected_signature) != 1:
            fail(f"signature occurrence mismatch in {condition['id']}")
        for branch in branches:
            required = [branch["id"], branch["kind"]] + branch["evidence"]
            for value in required:
                if str(value) not in content and html.escape(str(value)) not in content:
                    fail(f"{condition['id']} does not expose {value!r} for {branch['id']}")
            for field in ("expected_gain", "cost", "uncertainty", "reuse_credit"):
                value = branch[field]
                if f"{value:.2f}" not in content and str(value) not in content:
                    fail(f"{condition['id']} does not expose {value!r} for {branch['id']}")

    print("CONDITIONS_VALID")
    print(f"conditions={len(manifest['conditions'])} branches={len(branches)} signature={expected_signature}")


if __name__ == "__main__":
    main()
