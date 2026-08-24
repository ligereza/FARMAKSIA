"""Check that VIZZ task events can feed the CODE-INE state detector."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
VIZZ_CASES = ROOT / "experiments" / "015-vizz-session-contract" / "cases.json"
VIZZ_RUNNER = ROOT / "experiments" / "015-vizz-session-contract" / "run_experiment.py"
CODEINE_RUNNER = ROOT / "experiments" / "016-codeine-session-state" / "run_experiment.py"
REQUIRED_BRIDGE_FIELDS = {"event_id", "t_ms", "action_class", "gain", "errors"}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_opt_in_session() -> dict[str, Any]:
    cases = json.loads(VIZZ_CASES.read_text(encoding="utf-8"))
    return next(case["session"] for case in cases["cases"] if case["id"] == "opt-in-task-events")


def normalize_events(session: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    normalized = []
    dropped_fields: set[str] = set()
    for event in session["events"]:
        payload = event["payload"]
        missing = {"action_class", "gain", "errors"} - set(payload)
        if missing:
            raise ValueError(f"bridge requires fields: {','.join(sorted(missing))}")
        normalized.append({
            "event_id": event["event_id"],
            "t_ms": event["t_ms"],
            "action_class": payload["action_class"],
            "gain": payload["gain"],
            "errors": payload["errors"],
        })
        dropped_fields.update(set(payload) - {"action_class", "gain", "errors"})
    return normalized, sorted(dropped_fields)


def run_bridge() -> dict[str, Any]:
    vizz = load_module(VIZZ_RUNNER, "vizz_session_contract_015")
    codeine = load_module(CODEINE_RUNNER, "codeine_state_016")
    session = load_opt_in_session()
    vizz_event_count = vizz.validate_session(session)
    normalized, dropped_fields = normalize_events(session)
    codeine.validate_events(normalized)
    transition = codeine.derive_transition(normalized)
    return {
        "experiment": "020-vizz-codeine-event-bridge",
        "source_contract": "farmaxia:vizz-session:0.1",
        "target_contract": "farmaxia:codeine-session-trace:0.1",
        "vizz_event_count": vizz_event_count,
        "codeine_event_count": len(normalized),
        "bridge_fields": sorted(REQUIRED_BRIDGE_FIELDS),
        "dropped_vizz_fields": dropped_fields,
        "transition": transition,
        "repetition_boundary": "unavailable: only one event follows the last significant improvement",
        "human_data": False,
        "devices_started": False,
        "network_used": False,
        "raw_capture": False,
        "scope_limit": "synthetic contract interoperability; no human state or pharmacological inference",
    }


def main() -> None:
    try:
        result = run_bridge()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"BRIDGE_INVALID: {exc}") from exc
    if result["vizz_event_count"] != 3 or result["codeine_event_count"] != 3:
        raise SystemExit("BRIDGE_INVALID: event counts diverged")
    if result["transition"]["last_significant_improvement"] != "s02":
        raise SystemExit("BRIDGE_INVALID: improvement anchor changed")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
