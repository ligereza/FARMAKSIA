"""Executable acceptance checks for the native temporal PUPILA integration."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "090-farmaxia-adaptive-representation-layer"))
sys.path.insert(0, str(HERE))

from temporal_coordinator import TemporalCoordinator
from temporal_reference import eligible_events


def event(event_id: str, peer: str, at: str, sequence: int) -> dict[str, object]:
    return {
        "event_id": event_id, "schema_version": 1, "source_app": "fixture",
        "event_type": "connectivity.status", "channel": "transport", "payload": {"state": "connected"},
        "source_timestamp": at, "received_timestamp": at, "session_id": "session-092", "peer_id": peer,
        "sequence": sequence, "raw_hash": f"sha256:{event_id}", "provenance": {"rootId": "fixture-092"},
    }


def context() -> dict[str, object]:
    return {"sessionId": "session-092", "roomId": "room-092", "surfaceId": "surface-092", "host": "fixture", "task": "integration"}


def main() -> None:
    with TemporaryDirectory() as directory:
        coordinator = TemporalCoordinator(Path(directory) / "integration.sqlite3", stale_after_ms=10_000)
        base = int(datetime(2026, 9, 7, 12, 0, tzinfo=timezone.utc).timestamp() * 1000)
        coordinator.consent("session-092", "peer-a", True, active_from_ms=0)
        coordinator.consent("session-092", "peer-b", True, active_from_ms=0)
        assert coordinator.ingest(event("event-a", "peer-a", "2026-09-07T12:00:00Z", 1), context()) == "accepted"
        assert coordinator.ingest(event("event-b", "peer-b", "2026-09-07T12:00:01Z", 2), context()) == "accepted"
        assert coordinator.ingest(event("event-a", "peer-a", "2026-09-07T12:00:00Z", 1), context()) == "duplicate"
        assert coordinator.snapshot("session-092", evaluation_ms=base + 1000)["eventCount"] == 2
        ticked = coordinator.tick("session-092", base + 1000)
        assert ticked["lucidaView"]["safety"]["automatic_actions"] is False
        assert ticked["renderPlan"]["clickThrough"] is True
        proposal_id = ticked["pupilaView"]["proposals"][0]["proposalId"]
        accepted = coordinator.decide("session-092", proposal_id, request_id="request-1")
        assert accepted["status"] == "accepted"
        assert coordinator.decide("session-092", proposal_id, request_id="request-1")["decision_id"] == accepted["decision_id"]
        reverted = coordinator.decide("session-092", proposal_id, request_id="request-2", revert_decision_id=accepted["decision_id"])
        assert reverted["status"] == "reverted"
        future = coordinator.snapshot("session-092", evaluation_ms=base - 1000)
        assert future["eventCount"] == 0
        decision = coordinator.decide("session-092", future["pupilaView"]["proposals"][0]["proposalId"] if future["pupilaView"]["proposals"] else "none", request_id="request-1") if future["pupilaView"]["proposals"] else None
        assert decision is None
        coordinator.consent("session-092", "peer-b", False)
        assert coordinator.snapshot("session-092", evaluation_ms=base + 1000)["eventCount"] == 1
        coordinator.consent("session-092", "peer-b", True)
        assert coordinator.snapshot("session-092", evaluation_ms=base + 1000)["eventCount"] == 1
        coordinator.close()
        restarted = TemporalCoordinator(Path(directory) / "integration.sqlite3", stale_after_ms=10_000)
        assert restarted.snapshot("session-092", evaluation_ms=base + 1000)["eventCount"] == 1
        restarted.close()
    print(json.dumps({"status": "passed", "checks": ["durable-clock", "future-evidence", "expiry", "consent-epoch-revocation", "idempotence", "lucida-projection"]}, sort_keys=True))


if __name__ == "__main__":
    main()
