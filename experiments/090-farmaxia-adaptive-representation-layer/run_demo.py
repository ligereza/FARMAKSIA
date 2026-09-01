"""Offline demonstration of the two distinct adapters."""

from __future__ import annotations

import json

from pupila_adapter import PupilaAdapter
from vizz_adapter import VizzAdapter


def main() -> None:
    context = {"sessionId": "demo-session", "roomId": "demo-room", "surfaceId": "surface-a", "host": "fixture", "task": "shared-demo"}
    adapter = VizzAdapter()
    user_a = {**context, "participantRef": "user-a"}
    user_b = {**context, "participantRef": "user-b"}
    state_a = adapter.ingest(user_a, {**user_a, "kind": "focus", "atMs": 100, "value": {"focused": True}, "consent": True})
    state_b = adapter.ingest(user_b, {**user_b, "kind": "focus", "atMs": 100, "value": {"focused": False}, "consent": True})
    room = PupilaAdapter()
    room.ingest(user_a, state_a)
    shared = room.ingest(user_b, state_b)
    print(json.dumps({"vizz": [state_a, state_b], "pupila": shared}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
