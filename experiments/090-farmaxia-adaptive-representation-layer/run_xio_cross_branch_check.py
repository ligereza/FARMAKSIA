"""Verify the real XIO event contract against the local VIZZ/PUPILA bridge."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent


def build_event(xio_root: Path):
    sys.path.insert(0, str(xio_root))
    sys.path.insert(0, str(HERE))
    from XIO_LAYER.adapters import connectivity_status_to_event
    from XIO_LAYER.core.transport import (
        ConnectionState,
        ConnectionStatus,
        Endpoint,
        NetworkMedium,
        NetworkScope,
    )

    checked_at = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
    status = ConnectionStatus(
        endpoint=Endpoint(
            "memory",
            "ethernet-host",
            medium=NetworkMedium.ETHERNET,
            scope=NetworkScope.LAN,
        ),
        state=ConnectionState.CONNECTED,
        checked_at=checked_at,
        latency_ms=15.0,
        packets_sent=10,
        packets_received=9,
        packets_lost=1,
        reason="host_probe_ok",
    )
    return connectivity_status_to_event(
        status,
        source_app="XIO",
        session_id="session-cross-branch",
        peer_id="peer-1",
        sequence=1,
        received_timestamp=datetime(2026, 9, 1, 12, 0, 1, tzinfo=timezone.utc),
    )


def build_interaction_event(
    event_id: str,
    *,
    event_type: str,
    channel: str,
    sequence: int,
    payload: dict[str, object],
) -> dict[str, object]:
    """Build a deterministic XIO-carried interaction event for the replay."""

    timestamp = f"2026-09-01T12:00:0{sequence}Z"
    return {
        "event_id": event_id,
        "schema_version": 1,
        "source_app": "XIO",
        "event_type": event_type,
        "channel": channel,
        "payload": payload,
        "source_timestamp": timestamp,
        "received_timestamp": timestamp,
        "session_id": "session-cross-branch",
        "peer_id": "peer-1",
        "sequence": sequence,
        "raw_hash": f"sha256:{event_id}",
        "provenance": {"rootId": "xio-root-interaction", "measuredBy": "host"},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xio-root", default=r"C:\IA\XIO")
    args = parser.parse_args()
    from canonical_event_bridge import CanonicalEventReplay

    connectivity_event = build_event(Path(args.xio_root)).to_dict()
    events = [
        connectivity_event,
        build_interaction_event(
            "xio-focus-001",
            event_type="focus.changed",
            channel="focus",
            sequence=2,
            payload={"focused": True},
        ),
        build_interaction_event(
            "xio-pointer-001",
            event_type="pointer.moved",
            channel="pointer",
            sequence=3,
            payload={"x": 0.5, "y": 0.5},
        ),
        build_interaction_event(
            "xio-keyboard-001",
            event_type="keyboard.input",
            channel="keyboard",
            sequence=4,
            payload={"count": 2, "shortcut": "CTRL+K", "text": "never-persist"},
        ),
    ]
    events.append(dict(events[-1]))
    report = CanonicalEventReplay().run(
        events,
        {
            "roomId": "room-cross",
            "surfaceId": "surface-cross",
            "task": "cross-branch-interaction-replay",
        },
        consent=True,
    )
    summary = {
        "eventTypes": [event["event_type"] for event in events],
        "acceptedCount": report["acceptedCount"],
        "duplicateCount": report["duplicateCount"],
        "payloadForwarded": any("payload" in result for result in report["results"]),
        "interactionMetrics": report["interactionMetrics"],
        "finalPupilaView": report["finalPupilaView"],
    }
    assert summary["acceptedCount"] == 4
    assert summary["duplicateCount"] == 1
    assert summary["payloadForwarded"] is False
    assert summary["interactionMetrics"]["participants"][0]["focusState"] is True
    assert summary["finalPupilaView"]["participantCount"] == 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
