"""Verify one XIO event across the LUCIDA/MULTI transport boundary."""

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
    from run_xio_cross_branch_check import build_event, build_interaction_event  # noqa: E402

    connectivity_event = build_event(Path(args.xio_root)).to_dict()
    interaction_event = build_interaction_event(
        "xio-multi-focus-001",
        event_type="focus.changed",
        channel="focus",
        sequence=2,
        payload={"focused": True},
    )
    source_event = ApplicationEvent.from_dict(connectivity_event)
    message = application_event_to_transport(
        source_event,
        source="xio-host",
        destination=Endpoint(
            "memory",
            "lucida-multi",
            medium=NetworkMedium.ETHERNET,
            scope=NetworkScope.LAN,
        ),
        sent_at=datetime(2026, 9, 1, 12, 0, 2, tzinfo=timezone.utc),
        message_id="xio-multi-message-001",
    )
    recovered = transport_to_application_event(message)
    assert recovered.to_dict() == source_event.to_dict()

    report = CanonicalEventReplay().run(
        [connectivity_event, interaction_event],
        {
            "roomId": "room-cross",
            "surfaceId": "surface-cross",
            "task": "lucida-multi-bridge-check",
        },
        consent=True,
    )
    summary = {
        "transportChannel": message.channel,
        "roundTripPreserved": True,
        "eventIdPreserved": recovered.event_id == source_event.event_id,
        "provenancePreserved": recovered.raw_hash == source_event.raw_hash,
        "farmaxiaAcceptedCount": report["acceptedCount"],
        "farmaxiaFinalView": report["finalPupilaView"],
        "farmaxiaViewDiffCount": len(report["pupilaViewDiffs"]),
        "payloadForwarded": any("payload" in result for result in report["results"]),
    }
    assert summary["farmaxiaAcceptedCount"] == 2
    assert summary["farmaxiaViewDiffCount"] == 2
    assert summary["payloadForwarded"] is False
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
