"""Verify the counterbalanced VIZZ pilot before human use."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).parent
SOURCE = ROOT / "trial_sets.json"
PILOT = ROOT / "pilot.html"


def fail(message: str) -> None:
    raise SystemExit(f"BALANCED_PILOT_INVALID: {message}")


def signature(branches: list[dict]) -> str:
    payload = json.dumps(branches, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def main() -> None:
    state = json.loads(SOURCE.read_text(encoding="utf-8"))
    pilot = PILOT.read_text(encoding="utf-8")
    sets = state.get("sets", [])
    if len(sets) != 3:
        fail("expected exactly three trial sets")
    set_ids = [item.get("id") for item in sets]
    if len(set_ids) != len(set(set_ids)) or any(not item for item in set_ids):
        fail("trial set ids must be unique")
    signatures = {item["id"]: signature(item["branches"]) for item in sets}
    if len(set(signatures.values())) != 3:
        fail("trial sets must differ")
    branch_ids = [branch["id"] for branch in sets[0]["branches"]]
    for item in sets[1:]:
        if [branch["id"] for branch in item["branches"]] != branch_ids:
            fail("trial sets must share branch ids in the same order")
    for token in ("farmaxia:vizz-pilot:0.2", "set_id", "assignmentTemplates", "setSignatures", "role=\"button\"", "aria-pressed", "event.key === 'Enter'", "event.key === ' '", ":focus-visible"):
        if token not in pilot:
            fail(f"required token missing: {token}")
    for forbidden in ("correct_action", "fetch(", "XMLHttpRequest", "navigator.sendBeacon"):
        if forbidden in pilot:
            fail(f"forbidden token present: {forbidden}")
    for value in signatures.values():
        if pilot.count(value) < 1:
            fail("set signature missing from pilot")

    scripts = re.findall(r"<script>(.*?)</script>", pilot, flags=re.DOTALL)
    if len(scripts) != 1:
        fail("expected exactly one inline script")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(scripts[0])
        script_path = Path(handle.name)
    try:
        checked = subprocess.run(["node", "--check", str(script_path)], capture_output=True, text=True)
    finally:
        script_path.unlink(missing_ok=True)
    if checked.returncode != 0:
        fail(f"JavaScript syntax: {checked.stderr.strip()}")
    print("BALANCED_PILOT_VALID")
    print(f"sets={len(sets)} signatures={len(signatures)}")


if __name__ == "__main__":
    main()
