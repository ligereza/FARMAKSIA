"""Consent-gated local adapter for abstract VIZZ task events.

This tool never reads a screen, keyboard, webcam, microphone, gaze stream, URL,
or file content. A caller must pass --consent before any event is parsed. The
tool is prepared for deliberate manual use; importing it has no side effects.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
VIZZ_VALIDATOR = ROOT / "experiments" / "015-vizz-session-contract" / "run_experiment.py"


def load_validator() -> Any:
    spec = importlib.util.spec_from_file_location("farmaxia_vizz_session_validator", VIZZ_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load VIZZ session validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_explicit_consent(consent: bool) -> None:
    if not consent:
        raise PermissionError("explicit --consent is required; no session was started")


def parse_event(raw: str) -> dict[str, Any]:
    event = json.loads(raw)
    if not isinstance(event, dict):
        raise ValueError("event must be a JSON object")
    return event


def build_session(events: list[dict[str, Any]], *, consent: bool) -> dict[str, Any]:
    require_explicit_consent(consent)
    session = {
        "schema": "farmaxia:vizz-session:0.1",
        "consent": {"granted": True, "scope": "task_events_only", "raw_capture": False},
        "capture": {"enabled": True, "source": "manual_event_adapter"},
        "events": events,
    }
    validator = load_validator()
    validator.validate_session(session)
    return session


def write_session(path: Path, session: dict[str, Any]) -> None:
    if path.exists():
        raise FileExistsError("refusing to overwrite an existing session; choose a new output path")
    if not path.parent.is_dir():
        raise FileNotFoundError("output parent directory does not exist")
    path.write_text(json.dumps(session, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record only abstract, consented VIZZ task events.")
    parser.add_argument("--consent", action="store_true", help="explicitly opt in to task-event recording")
    parser.add_argument("--output", type=Path, required=True, help="new JSON output path; existing files are never overwritten")
    parser.add_argument("--event", action="append", default=[], help="abstract VIZZ event as a JSON object; repeatable")
    parser.add_argument("--dry-run", action="store_true", help="validate the session without writing an output file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        require_explicit_consent(args.consent)
        events = [parse_event(raw) for raw in args.event]
        session = build_session(events, consent=True)
        if args.dry_run:
            print(f"ADAPTER_DRY_RUN_VALID events={len(events)} output_not_written=true")
            return
        write_session(args.output, session)
    except (FileExistsError, FileNotFoundError, PermissionError, ValueError, json.JSONDecodeError) as exc:
        print(f"ADAPTER_BLOCKED: {exc}")
        raise SystemExit(2) from exc
    print(f"ADAPTER_SESSION_WRITTEN events={len(events)} path={args.output}")


if __name__ == "__main__":
    main()
