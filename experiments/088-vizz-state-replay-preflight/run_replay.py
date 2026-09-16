"""Replay a VIZZ state sequence without starting any external application."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[2]
STATE_RENDERER = ROOT / "experiments" / "087-vizz-touchdesigner-state-renderer"
sys.path.insert(0, str(STATE_RENDERER))

from render_policy import compute_plan  # noqa: E402
from state_router import normalize_state, to_channels  # noqa: E402


def _unknown_for_sequence(payload: Mapping[str, Any], now_ms: float, max_age_ms: float) -> dict[str, Any]:
    """Ask the 087 router for its neutral shape, then label the ordering fault."""

    candidate = dict(payload)
    candidate["confidence"] = 0.0
    state = normalize_state(candidate, now_monotonic_ms=now_ms, max_age_ms=max_age_ms)
    state["reason"] = "SEQUENCE_NOT_MONOTONIC"
    return state


class ReplayCursor:
    """Apply normalized states only in strictly increasing sequence order."""

    def __init__(self, *, now_ms: float, max_age_ms: float) -> None:
        self.now_ms = now_ms
        self.max_age_ms = max_age_ms
        self.last_seq: int | None = None

    def apply(self, payload: Mapping[str, Any] | Any) -> dict[str, Any]:
        state = normalize_state(payload, now_monotonic_ms=self.now_ms, max_age_ms=self.max_age_ms)
        if not isinstance(payload, Mapping):
            return state
        seq = payload.get("seq")
        if isinstance(seq, int) and not isinstance(seq, bool):
            if self.last_seq is not None and seq <= self.last_seq:
                return _unknown_for_sequence(payload, self.now_ms, self.max_age_ms)
            self.last_seq = seq
        return state


def replay_records(
    records: Iterable[Mapping[str, Any] | Any],
    *,
    now_ms: float,
    max_age_ms: float = 500.0,
) -> list[dict[str, Any]]:
    """Return the renderer-visible result for each input record."""

    cursor = ReplayCursor(now_ms=now_ms, max_age_ms=max_age_ms)
    output: list[dict[str, Any]] = []
    for line_number, payload in enumerate(records, start=1):
        state = cursor.apply(payload)
        plan = compute_plan(state)
        output.append(
            {
                "line": line_number,
                "seq": state["seq"],
                "status": state["status"],
                "reason": state["reason"],
                "channels": to_channels(state),
                "plan": plan,
            }
        )
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="JSONL state sequence")
    parser.add_argument("--now-ms", required=True, type=float, help="fixed monotonic clock for deterministic replay")
    parser.add_argument("--max-age-ms", type=float, default=500.0)
    args = parser.parse_args(argv)
    if args.max_age_ms < 0:
        parser.error("--max-age-ms must be non-negative")
    try:
        lines = args.input.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        print(f"REPLAY_INVALID: {exc}", file=sys.stderr)
        return 2

    records: list[Mapping[str, Any] | Any] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            print(f"REPLAY_INVALID line={line_number}: {exc}", file=sys.stderr)
            return 2

    for result in replay_records(records, now_ms=args.now_ms, max_age_ms=args.max_age_ms):
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
