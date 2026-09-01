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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xio-root", default=r"C:\IA\XIO")
    args = parser.parse_args()
    from canonical_event_bridge import CanonicalEventBridge

    event = build_event(Path(args.xio_root))
    result = CanonicalEventBridge().ingest(
        event.to_dict(),
        {
            "roomId": "room-cross",
            "surfaceId": "surface-cross",
            "task": "cross-branch-contract-check",
        },
        consent=True,
    )
    summary = {
        "eventType": event.event_type,
        "channel": event.channel,
        "signalKind": result["signal"]["kind"],
        "sampleCount": result["vizzState"]["sampleCount"],
        "payloadForwarded": "payload" in result,
        "provenancePreserved": result["lineage"]["rawHash"] == event.raw_hash,
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
