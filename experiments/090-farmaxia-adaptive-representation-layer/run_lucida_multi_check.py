"""Verify multiple XIO participants across the LUCIDA/MULTI boundary."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xio-root", default=r"C:\IA\XIO")
    parser.add_argument("--lucida-multi-root", required=True)
    args = parser.parse_args()

    sys.path.insert(0, str(Path(args.lucida_multi_root)))
    sys.path.insert(0, str(HERE))
    from XIO_LAYER.adapters.lucida_bridge import (  # noqa: E402
        application_event_to_transport,
        transport_to_application_event,
    )
    from XIO_LAYER.core.events import ApplicationEvent  # noqa: E402
    from XIO_LAYER.core.transport import Endpoint, NetworkMedium, NetworkScope  # noqa: E402
    from canonical_event_bridge import CanonicalEventReplay  # noqa: E402
    from run_xio_cross_branch_check import build_event  # noqa: E402

    connectivity_event = build_event(Path(args.xio_root)).to_dict()
    checked_at = datetime(2026, 9, 1, 12, 0, 2, tzinfo=timezone.utc)
    interaction_event = ApplicationEvent(
        event_id="xio-multi-focus-001",
        source_app="XIO",
        event_type="focus.changed",
        channel="focus",
        payload={"focused": True},
        source_timestamp=checked_at,
        received_timestamp=checked_at,
        session_id="session-cross-branch",
        peer_id="peer-1",
        sequence=2,
        provenance={"rootId": "xio-root-interaction", "measuredBy": "host"},
    )
    second_event = ApplicationEvent(
        event_id="xio-multi-focus-002",
        source_app="XIO",
        event_type="focus.changed",
        channel="focus",
        payload={"focused": False},
        source_timestamp=checked_at,
        received_timestamp=checked_at,
        session_id="session-cross-branch",
        peer_id="peer-2",
        sequence=3,
        provenance={"rootId": "xio-root-interaction", "measuredBy": "host"},
    )
    source_events = [ApplicationEvent.from_dict(connectivity_event), interaction_event, second_event]
    messages = [
        application_event_to_transport(
            event,
            source="xio-host",
            destination=Endpoint(
                "memory",
                "lucida-multi",
                medium=NetworkMedium.ETHERNET,
                scope=NetworkScope.LAN,
            ),
            sent_at=checked_at,
            message_id=f"xio-multi-message-{index:03d}",
        )
        for index, event in enumerate(source_events, start=1)
    ]
    recovered_events = [transport_to_application_event(message) for message in messages]
    assert all(
        recovered.to_dict() == source.to_dict()
        for recovered, source in zip(recovered_events, source_events)
    )

    report = CanonicalEventReplay().run(
        [event.to_dict() for event in recovered_events],
        {
            "roomId": "room-cross",
            "surfaceId": "surface-cross",
            "task": "lucida-multi-bridge-check",
        },
        consent=True,
    )
    summary = {
        "transportChannel": messages[0].channel,
        "transportedEventCount": len(messages),
        "roundTripPreserved": True,
        "eventIdsPreserved": all(
            recovered.event_id == source.event_id
            for recovered, source in zip(recovered_events, source_events)
        ),
        "provenancePreserved": all(
            recovered.raw_hash == source.raw_hash
            for recovered, source in zip(recovered_events, source_events)
        ),
        "farmaxiaAcceptedCount": report["acceptedCount"],
        "farmaxiaFinalView": report["finalPupilaView"],
        "farmaxiaViewDiffCount": len(report["pupilaViewDiffs"]),
        "payloadForwarded": any("payload" in result for result in report["results"]),
    }
    assert summary["transportedEventCount"] == 3
    assert summary["eventIdsPreserved"] is True
    assert summary["provenancePreserved"] is True
    assert summary["farmaxiaAcceptedCount"] == 3
    assert summary["farmaxiaFinalView"]["participantCount"] == 2
    assert summary["farmaxiaFinalView"]["proposals"][0]["kind"] == "shared-checkpoint"
    assert summary["farmaxiaViewDiffCount"] == 3
    assert summary["payloadForwarded"] is False
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
