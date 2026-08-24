"""Verify the offline VIZZ pilot instrument before human use."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).parent
SOURCE = ROOT / "decision-state.json"
PILOT = ROOT / "pilot.html"


def fail(message: str) -> None:
    raise SystemExit(f"PILOT_INVALID: {message}")


def main() -> None:
    state = json.loads(SOURCE.read_text(encoding="utf-8"))
    pilot = PILOT.read_text(encoding="utf-8")
    branches = sorted(state["branches"], key=lambda branch: branch["id"])
    canonical = json.dumps(branches, sort_keys=True, separators=(",", ":")).encode("utf-8")
    expected_signature = hashlib.sha256(canonical).hexdigest().upper()

    if pilot.count(expected_signature) < 1:
        fail("source signature is absent")
    for condition in ("table", "static-graph", "vizz-candidate"):
        if condition not in pilot:
            fail(f"condition missing: {condition}")
    for field in ("confidence", "explanation", "detected_uncertainty", "duration_ms", "downloadResults"):
        if field not in pilot:
            fail(f"measurement field missing: {field}")
    for forbidden in ("fetch(", "XMLHttpRequest", "navigator.sendBeacon", "correct_action_for_pilot"):
        if forbidden in pilot:
            fail(f"forbidden token present: {forbidden}")

    accessibility_tokens = (
        '<html lang="es">',
        'role="status"',
        ':focus-visible',
        'role="button"',
        "event.key === 'Enter'",
        "event.key === ' '",
        'aria-pressed',
        'role="alert"',
        'min-height: 44px',
    )
    for token in accessibility_tokens:
        if token not in pilot:
            fail(f"accessibility safeguard missing: {token}")

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

    print("PILOT_VALID")
    print(f"conditions=3 branches={len(branches)} signature={expected_signature}")


if __name__ == "__main__":
    main()
