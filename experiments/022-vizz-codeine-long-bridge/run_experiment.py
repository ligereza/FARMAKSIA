"""Run a long synthetic VIZZ session through the manual adapter and CODE-INE."""

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
SESSION = HERE / "session.json"
ADAPTER = ROOT / "research" / "tools" / "manual_event_adapter.py"
BRIDGE = ROOT / "experiments" / "020-vizz-codeine-event-bridge" / "run_experiment.py"
CODEINE = ROOT / "experiments" / "016-codeine-session-state" / "run_experiment.py"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def events() -> list[dict[str, Any]]:
    return json.loads(SESSION.read_text(encoding="utf-8"))["events"]


def run_dry_run(adapter: Any, event_list: list[dict[str, Any]], output: Path) -> bool:
    arguments = [sys.executable, str(ADAPTER), "--consent", "--output", str(output), "--dry-run"]
    for event in event_list:
        arguments.extend(["--event", json.dumps(event, separators=(",", ":"))])
    completed = subprocess.run(
        arguments,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return completed.returncode == 0 and "ADAPTER_DRY_RUN_VALID" in completed.stdout and not output.exists()


def main() -> None:
    adapter = load_module(ADAPTER, "manual_adapter_021")
    bridge = load_module(BRIDGE, "bridge_020")
    codeine = load_module(CODEINE, "codeine_016")
    session = json.loads(SESSION.read_text(encoding="utf-8"))
    vizz_count = adapter.load_validator().validate_session(session)
    event_list = events()
    normalized, dropped = bridge.normalize_events(session)
    codeine.validate_events(normalized)
    transition = codeine.derive_transition(normalized)
    with tempfile.TemporaryDirectory(prefix="farmaxia-long-022-") as directory:
        dry_run_valid = run_dry_run(adapter, event_list, Path(directory) / "session.json")
    print(
        json.dumps(
            {
                "experiment": "022-vizz-codeine-long-bridge",
                "vizz_event_count": vizz_count,
                "codeine_event_count": len(normalized),
                "dropped_vizz_fields": dropped,
                "transition": transition,
                "dry_run_valid": dry_run_valid,
                "session_written": False,
                "human_data": False,
                "pharmacological_inference": False,
                "devices_started": False,
                "network_used": False,
                "raw_capture": False,
                "scope_limit": "synthetic long-sequence interoperability; no human session or state claim",
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
