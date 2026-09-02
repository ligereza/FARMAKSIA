"""Verify multiple XIO participants across the LUCIDA/MULTI boundary."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent


def _clear_xio_modules() -> None:
    for module_name in list(sys.modules):
        if module_name == "XIO_LAYER" or module_name.startswith("XIO_LAYER."):
            del sys.modules[module_name]


def _load_xio_event(xio_root: Path) -> tuple[dict[str, object], str]:
    if not xio_root.is_dir():
        raise FileNotFoundError(f"XIO root does not exist: {xio_root}")
    _clear_xio_modules()
    sys.path.insert(0, str(xio_root))
    import XIO_LAYER  # noqa: PLC0415

    loaded_xio_path = Path(XIO_LAYER.__file__).resolve()
    try:
        loaded_xio_path.relative_to(xio_root)
    except ValueError as error:
        raise AssertionError(
            f"loaded XIO package is outside requested root: {loaded_xio_path}"
        ) from error

    from run_xio_cross_branch_check import build_event  # noqa: PLC0415

    return build_event(xio_root).to_dict(), str(loaded_xio_path)


def _load_multi_transport(multi_root: Path) -> tuple[object, object, object, object, object, object, str]:
    if not multi_root.is_dir():
        raise FileNotFoundError(f"LUCIDA MULTI root does not exist: {multi_root}")
    _clear_xio_modules()
    sys.path.insert(0, str(multi_root))
    import XIO_LAYER  # noqa: PLC0415

    loaded_multi_path = Path(XIO_LAYER.__file__).resolve()
    try:
        loaded_multi_path.relative_to(multi_root)
    except ValueError as error:
        raise AssertionError(
            f"loaded LUCIDA MULTI package is outside requested root: {loaded_multi_path}"
        ) from error

    from XIO_LAYER.adapters.lucida_bridge import (  # noqa: PLC0415
        application_event_to_transport,
        transport_to_application_event,
    )
    from XIO_LAYER.core.events import ApplicationEvent  # noqa: PLC0415
    from XIO_LAYER.core.transport import Endpoint, NetworkMedium, NetworkScope  # noqa: PLC0415
    return (
        application_event_to_transport,
        transport_to_application_event,
        ApplicationEvent,
        Endpoint,
        NetworkMedium,
        NetworkScope,
        str(loaded_multi_path),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xio-root", default=r"C:\IA\XIO")
    parser.add_argument("--lucida-multi-root", required=True)
    args = parser.parse_args()

    sys.path.insert(0, str(HERE))
    from canonical_event_bridge import CanonicalEventReplay  # noqa: E402

    xio_root = Path(args.xio_root).resolve()
    multi_root = Path(args.lucida_multi_root).resolve()
    connectivity_event, loaded_xio_path = _load_xio_event(xio_root)
    (
        application_event_to_transport,
        transport_to_application_event,
        ApplicationEvent,
        Endpoint,
        NetworkMedium,
        NetworkScope,
        loaded_multi_path,
    ) = _load_multi_transport(multi_root)
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
        "xioRoot": str(xio_root),
        "loadedXioPath": loaded_xio_path,
        "lucidaMultiRoot": str(multi_root),
        "loadedLucidaMultiPath": loaded_multi_path,
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
