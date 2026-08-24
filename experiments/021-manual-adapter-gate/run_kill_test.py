"""Kill tests for the manual VIZZ adapter gate."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
ADAPTER_PATH = ROOT / "research" / "tools" / "manual_event_adapter.py"
SPEC = importlib.util.spec_from_file_location("farmaxia_manual_adapter_kill", ADAPTER_PATH)
if SPEC is None or SPEC.loader is None:
    raise SystemExit("KILL_TEST_INVALID: could not load adapter")
ADAPTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADAPTER)


def load_events() -> list[dict]:
    cases = json.loads((ROOT / "experiments" / "015-vizz-session-contract" / "cases.json").read_text(encoding="utf-8"))
    session = next(case["session"] for case in cases["cases"] if case["id"] == "opt-in-task-events")
    return session["events"]


def main() -> None:
    events = load_events()
    with tempfile.TemporaryDirectory(prefix="farmaxia-adapter-kill-021-") as directory:
        output = Path(directory) / "session.json"
        blocked = subprocess.run(
            [sys.executable, str(ADAPTER_PATH), "--output", str(output)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if blocked.returncode == 0 or "ADAPTER_BLOCKED" not in blocked.stdout or output.exists():
            raise SystemExit("KILL_TEST_INVALID: consent gate allowed an output")
        session = ADAPTER.build_session(events, consent=True)
        ADAPTER.write_session(output, session)
        try:
            ADAPTER.write_session(output, session)
        except FileExistsError:
            pass
        else:
            raise SystemExit("KILL_TEST_INVALID: existing output was overwritten")
    raw = copy.deepcopy(events)
    raw[0]["payload"]["text"] = "must be rejected"
    try:
        ADAPTER.build_session(raw, consent=True)
    except ValueError as exc:
        if "text" not in str(exc):
            raise SystemExit("KILL_TEST_INVALID: raw-field rejection reason changed") from exc
    else:
        raise SystemExit("KILL_TEST_INVALID: raw field crossed adapter")
    print("KILL_TESTS_VALID")
    print("consent_missing=blocked")
    print("existing_output=protected")
    print("raw_field=unavailable")


if __name__ == "__main__":
    main()
