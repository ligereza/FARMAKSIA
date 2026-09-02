"""Verify XIO route selection and a redacted handoff without delivery."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
XIO_ROOT = Path(r"C:\IA\XIO")
sys.path.insert(0, str(XIO_ROOT))
sys.path.insert(0, str(HERE))

from XIO_LAYER.adapters import ProtocolEventAdapter, SourceAdapterRegistry  # noqa: E402
from XIO_LAYER.adapters.handoff import PrivacyPolicy, prepare_adapter_handoff  # noqa: E402
from XIO_LAYER.adapters.lucida_bridge import transport_to_application_event  # noqa: E402
from XIO_LAYER.core.audit import AuditLedger  # noqa: E402
from XIO_LAYER.core.transport import Endpoint, NetworkMedium, NetworkScope, OscEnvelope  # noqa: E402
from canonical_event_bridge import CanonicalEventReplay  # noqa: E402


def _prepare_multi_handoff(
    *,
    peer_id: str,
    selection_id: str,
    message_id: str,
    handoff_id: str,
    focus_value: float,
    checked_at: datetime,
    audit: AuditLedger,
) -> tuple[object, object]:
    """Prepare one redacted XIO handoff for the shared-surface fixture."""

    registry = SourceAdapterRegistry()
    registry.register(
        ProtocolEventAdapter(
            source_app="XIO",
            session_id="session-route-multi",
            peer_id=peer_id,
        )
    )
    route_plan = registry.route_plan("osc.message", {"protocol.osc"})
    selection = registry.select_candidate(
        source_app="XIO",
        event_type="osc.message",
        required_capabilities={"protocol.osc"},
        caller_id=f"farmaxia-{peer_id}",
        plan=route_plan,
        selection_id=selection_id,
        selected_at=checked_at,
    )
    handoff = prepare_adapter_handoff(
        registry,
        selection,
        {
            "envelope": OscEnvelope("/vizz/focus", (focus_value,), timetag=checked_at),
            "channel": "osc",
            "sequence": 1,
            "source_timestamp": checked_at,
            "received_timestamp": checked_at,
            "provenance": {"fixture": "multi-participant-route-handoff"},
        },
        source="xio-host",
        destination=Endpoint(
            "memory",
            "lucida-multi",
            medium=NetworkMedium.ETHERNET,
            scope=NetworkScope.LAN,
        ),
        audit=audit,
        privacy_policy=PrivacyPolicy(),
        sent_at=checked_at,
        message_id=message_id,
        handoff_id=handoff_id,
    )
    recovered = transport_to_application_event(handoff.message)
    return handoff, recovered


def main() -> int:
    checked_at = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    registry = SourceAdapterRegistry()
    registry.register(
        ProtocolEventAdapter(
            source_app="XIO",
            session_id="session-route-check",
            peer_id="peer-route-check",
        )
    )
    route_plan = registry.route_plan("osc.message", {"protocol.osc"})
    selection = registry.select_candidate(
        source_app="XIO",
        event_type="osc.message",
        required_capabilities={"protocol.osc"},
        caller_id="farmaxia-check",
        plan=route_plan,
        selection_id="selection-route-001",
        selected_at=checked_at,
    )
    audit = AuditLedger()
    handoff = prepare_adapter_handoff(
        registry,
        selection,
        {
            "envelope": OscEnvelope("/vizz/focus", (1.0,), timetag=checked_at),
            "channel": "osc",
            "sequence": 1,
            "source_timestamp": checked_at,
            "received_timestamp": checked_at,
            "provenance": {"fixture": "route-handoff-check"},
        },
        source="xio-host",
        destination=Endpoint(
            "memory",
            "lucida-multi",
            medium=NetworkMedium.ETHERNET,
            scope=NetworkScope.LAN,
        ),
        audit=audit,
        privacy_policy=PrivacyPolicy(),
        sent_at=checked_at,
        message_id="message-route-001",
        handoff_id="handoff-route-001",
    )
    recovered = transport_to_application_event(handoff.message)
    replay = CanonicalEventReplay().run(
        [handoff.event.to_dict()],
        {
            "roomId": "room-route-check",
            "surfaceId": "surface-route-check",
            "task": "route-handoff-to-pupila",
        },
        consent=True,
    )
    summary = {
        "routeStatus": route_plan["status"],
        "selectedSource": selection.source_app,
        "handoffStatus": "prepared",
        "projectedPayloadKeys": sorted(handoff.event.payload),
        "transportChannel": handoff.message.channel,
        "roundTripEventPreserved": recovered.event_id == handoff.event.event_id,
        "auditVerified": audit.verify(),
        "executionAttempted": False,
        "pupilaAcceptedCount": replay["acceptedCount"],
        "pupilaViewDiffCount": len(replay["pupilaViewDiffs"]),
        "pupilaParticipantCount": replay["finalPupilaView"]["participantCount"],
        "pupilaSignalCoverage": replay["finalPupilaView"]["participants"][0]["interaction"]["signalCoverage"],
    }
    assert summary["routeStatus"] == "matched"
    assert summary["selectedSource"] == "XIO"
    assert summary["projectedPayloadKeys"] == []
    assert summary["transportChannel"] == "application-event"
    assert summary["roundTripEventPreserved"] is True
    assert summary["auditVerified"] is True
    assert summary["pupilaAcceptedCount"] == 1
    assert summary["pupilaViewDiffCount"] == 1
    assert summary["pupilaParticipantCount"] == 1
    assert summary["pupilaSignalCoverage"] == ["task"]

    multi_handoffs = [
        _prepare_multi_handoff(
            peer_id="peer-route-a",
            selection_id="selection-route-multi-a",
            message_id="message-route-multi-a",
            handoff_id="handoff-route-multi-a",
            focus_value=1.0,
            checked_at=checked_at,
            audit=audit,
        ),
        _prepare_multi_handoff(
            peer_id="peer-route-b",
            selection_id="selection-route-multi-b",
            message_id="message-route-multi-b",
            handoff_id="handoff-route-multi-b",
            focus_value=0.0,
            checked_at=checked_at,
            audit=audit,
        ),
    ]
    multi_recovered = [item[1] for item in multi_handoffs]
    multi_replay = CanonicalEventReplay().run(
        [item[0].event.to_dict() for item in multi_handoffs],
        {
            "roomId": "room-route-multi",
            "surfaceId": "surface-route-multi",
            "task": "multi-participant-route-handoff",
        },
        consent=True,
    )
    multi_view = multi_replay["finalPupilaView"]
    multi_proposal = multi_view["proposals"][0]
    multi_diff_fields = [
        change["field"]
        for change in multi_replay["pupilaViewDiffs"][1]["changes"]
    ]
    multi_summary = {
        "multiParticipantCount": multi_view["participantCount"],
        "multiAcceptedCount": multi_replay["acceptedCount"],
        "multiProposalKind": multi_proposal["kind"],
        "multiDiffFields": multi_diff_fields,
        "multiRoundTripEventPreserved": all(
            recovered.event_id == handoff.event.event_id
            for (handoff, _), recovered in zip(multi_handoffs, multi_recovered)
        ),
        "multiAuditVerified": audit.verify(),
        "executionAttempted": False,
    }
    assert multi_summary["multiParticipantCount"] == 2
    assert multi_summary["multiAcceptedCount"] == 2
    assert multi_summary["multiProposalKind"] == "co-presence"
    assert "participants" in multi_summary["multiDiffFields"]
    assert "proposals" in multi_summary["multiDiffFields"]
    assert multi_summary["multiRoundTripEventPreserved"] is True
    assert multi_summary["multiAuditVerified"] is True
    assert multi_summary["executionAttempted"] is False

    summary.update(multi_summary)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
