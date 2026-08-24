"""Kill tests for the long VIZZ to CODE-INE dry-run."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
RUNNER = HERE / "run_experiment.py"
BRIDGE = ROOT / "experiments" / "020-vizz-codeine-event-bridge" / "run_experiment.py"
SPEC = importlib.util.spec_from_file_location("long_bridge_runner", BRIDGE)
if SPEC is None or SPEC.loader is None:
    raise SystemExit("KILL_TEST_INVALID: could not load bridge")
BRIDGE_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BRIDGE_MODULE)


def main() -> None:
    result = json.loads(subprocess.check_output([sys.executable, str(RUNNER)], cwd=ROOT, text=True))
    transition = result["transition"]
    if (
        result["vizz_event_count"],
        result["codeine_event_count"],
        transition["last_significant_improvement"],
        transition["repetition_entry"],
        result["dry_run_valid"],
    ) != (8, 8, "c04", "c07", True):
        raise SystemExit("KILL_TEST_INVALID: long bridge did not preserve transition")
    session = json.loads((HERE / "session.json").read_text(encoding="utf-8"))
    damaged = copy.deepcopy(session)
    damaged["events"][6]["payload"].pop("action_class")
    try:
        BRIDGE_MODULE.normalize_events(damaged)
    except ValueError as exc:
        if "action_class" not in str(exc):
            raise SystemExit("KILL_TEST_INVALID: missing action boundary changed") from exc
    else:
        raise SystemExit("KILL_TEST_INVALID: bridge accepted damaged long session")
    blocked = subprocess.run(
        [sys.executable, str(ROOT / "research" / "tools" / "manual_event_adapter.py"), "--output", str(HERE / "never-created.json")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if blocked.returncode == 0 or "ADAPTER_BLOCKED" not in blocked.stdout or (HERE / "never-created.json").exists():
        raise SystemExit("KILL_TEST_INVALID: long adapter bypassed consent")
    if result["human_data"] or result["pharmacological_inference"] or result["raw_capture"]:
        raise SystemExit("KILL_TEST_INVALID: long bridge made prohibited claim")
    print("KILL_TESTS_VALID")
    print("long_transition=c04_to_c07")
    print("missing_action_class=unavailable")
    print("consent_missing=blocked")


if __name__ == "__main__":
    main()
