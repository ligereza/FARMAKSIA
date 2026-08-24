"""Verify the consent gate and dry-run behavior of the manual adapter."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
ADAPTER_PATH = ROOT / "research" / "tools" / "manual_event_adapter.py"
VIZZ_CASES = ROOT / "experiments" / "015-vizz-session-contract" / "cases.json"


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("farmaxia_manual_event_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load manual adapter")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def opt_in_events() -> list[dict[str, Any]]:
    cases = json.loads(VIZZ_CASES.read_text(encoding="utf-8"))
    session = next(case["session"] for case in cases["cases"] if case["id"] == "opt-in-task-events")
    return session["events"]


def main() -> None:
    adapter = load_adapter()
    events = opt_in_events()
    consent_blocked = False
    try:
        adapter.require_explicit_consent(False)
    except PermissionError:
        consent_blocked = True
    session = adapter.build_session(events, consent=True)
    with tempfile.TemporaryDirectory(prefix="farmaxia-adapter-021-") as directory:
        output = Path(directory) / "session.json"
        dry_run = subprocess.run(
            [
                sys.executable,
                str(ADAPTER_PATH),
                "--consent",
                "--output",
                str(output),
                "--dry-run",
                *sum((["--event", json.dumps(event, separators=(",", ":"))] for event in events), []),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        dry_run_valid = dry_run.returncode == 0 and "ADAPTER_DRY_RUN_VALID" in dry_run.stdout and not output.exists()
    print(
        json.dumps(
            {
                "experiment": "021-manual-adapter-gate",
                "consent_gate": consent_blocked,
                "validated_event_count": len(session["events"]),
                "dry_run_valid": dry_run_valid,
                "session_written": False,
                "human_data": False,
                "devices_started": False,
                "network_used": False,
                "raw_capture": False,
                "scope_limit": "adapter gate and dry-run only; no real session was collected",
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
