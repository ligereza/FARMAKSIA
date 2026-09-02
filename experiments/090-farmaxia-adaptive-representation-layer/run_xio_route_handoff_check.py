"""Verify XIO route selection and a redacted handoff without delivery."""

from __future__ import annotations

from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import sys
import tempfile


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from canonical_event_bridge import CanonicalEventReplay  # noqa: E402


XIO_ROOT = Path(r"C:\IA\XIO")


def _load_xio(xio_root: Path) -> str:
    """Load XIO from the explicitly requested checkout and prove its origin."""

    global AuditLedger
    global Endpoint
    global JsonLineHandoffStore
    global NetworkMedium
    global NetworkScope
    global OscEnvelope
    global PermissionRegistry
    global PrivacyPolicy
    global ProtocolEventAdapter
    global SourceAdapterRegistry
    global deliver_adapter_handoff
    global prepare_adapter_handoff
    global transport_to_application_event
    global XIO_ROOT

    XIO_ROOT = xio_root.resolve()
    if not XIO_ROOT.is_dir():
        raise FileNotFoundError(f"XIO root does not exist: {XIO_ROOT}")
    for module_name in list(sys.modules):
        if module_name == "XIO_LAYER" or module_name.startswith("XIO_LAYER."):
            del sys.modules[module_name]
    sys.path.insert(0, str(XIO_ROOT))

    import XIO_LAYER  # noqa: PLC0415
    from XIO_LAYER.adapters import (  # noqa: PLC0415
        JsonLineHandoffStore,
        ProtocolEventAdapter,
        SourceAdapterRegistry,
    )
    from XIO_LAYER.adapters.handoff import (  # noqa: PLC0415
        PrivacyPolicy,
        deliver_adapter_handoff,
        prepare_adapter_handoff,
    )
    from XIO_LAYER.adapters.lucida_bridge import (  # noqa: PLC0415
        transport_to_application_event,
    )
    from XIO_LAYER.core.audit import AuditLedger, PermissionRegistry  # noqa: PLC0415
    from XIO_LAYER.core.transport import (  # noqa: PLC0415
        Endpoint,
        NetworkMedium,
        NetworkScope,
        OscEnvelope,
    )

    loaded_path = Path(XIO_LAYER.__file__).resolve()
    try:
        loaded_path.relative_to(XIO_ROOT)
    except ValueError as error:
        raise AssertionError(
            f"loaded XIO package is outside requested root: {loaded_path}"
        ) from error
    return str(loaded_path)


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xio-root", default=str(XIO_ROOT))
    args = parser.parse_args()
    loaded_xio_path = _load_xio(Path(args.xio_root))

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
    with tempfile.TemporaryDirectory() as directory:
        store = JsonLineHandoffStore(Path(directory) / "handoffs.jsonl")
        assert store.append(handoff) is True
        restored = store.replay(caller_id="farmaxia-check")
    assert len(restored) == 1
    restored_handoff = restored[0]
    assert restored_handoff.event.to_dict() == handoff.event.to_dict()

    class CountingTransport:
        def __init__(self) -> None:
            self.calls = 0

        def send(self, message: object) -> None:
            self.calls += 1
            raise AssertionError("revoked handoff must not reach transport")

    permissions = PermissionRegistry()
    permissions.grant("farmaxia-check", "handoff.deliver")
    permissions.revoke("farmaxia-check", "handoff.deliver")
    transport = CountingTransport()
    delivery = deliver_adapter_handoff(
        restored_handoff,
        transport,
        audit,
        permissions=permissions,
    )
    assert delivery.status == "rejected"
    assert delivery.error == "permission_missing_or_revoked"
    assert transport.calls == 0
    assert audit.verify() is True
    replay = CanonicalEventReplay().run(
        [restored_handoff.event.to_dict()],
        {
            "roomId": "room-route-check",
            "surfaceId": "surface-route-check",
            "task": "route-handoff-to-pupila",
        },
        consent=True,
    )
    summary = {
        "xioRoot": str(XIO_ROOT),
        "loadedXioPath": loaded_xio_path,
        "routeStatus": route_plan["status"],
        "selectedSource": selection.source_app,
        "handoffStatus": "prepared",
        "projectedPayloadKeys": sorted(handoff.event.payload),
        "transportChannel": handoff.message.channel,
        "roundTripEventPreserved": recovered.event_id == handoff.event.event_id,
        "persistedHandoffRestored": len(restored) == 1,
        "restoredEventPreserved": restored_handoff.event.to_dict() == handoff.event.to_dict(),
        "revokedDeliveryStatus": delivery.status,
        "revokedDeliveryTransportCalls": transport.calls,
        "revokedDeliveryNoSideEffect": transport.calls == 0,
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
    assert summary["persistedHandoffRestored"] is True
    assert summary["restoredEventPreserved"] is True
    assert summary["revokedDeliveryStatus"] == "rejected"
    assert summary["revokedDeliveryTransportCalls"] == 0
    assert summary["revokedDeliveryNoSideEffect"] is True

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
    with tempfile.TemporaryDirectory() as directory:
        multi_store = JsonLineHandoffStore(Path(directory) / "multi-handoffs.jsonl")
        for handoff, _ in multi_handoffs:
            assert multi_store.append(handoff) is True
        restored_multi = multi_store.replay(caller_id="farmaxia-multi-check")
    assert len(restored_multi) == 2
    multi_replay = CanonicalEventReplay().run(
        [item.event.to_dict() for item in restored_multi],
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
        "multiPersistedHandoffCount": len(restored_multi),
        "multiRestoredEventsPreserved": all(
            restored.event.to_dict() == original.event.to_dict()
            for restored, (original, _) in zip(restored_multi, multi_handoffs)
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
    assert multi_summary["multiPersistedHandoffCount"] == 2
    assert multi_summary["multiRestoredEventsPreserved"] is True
    assert multi_summary["multiAuditVerified"] is True
    assert multi_summary["executionAttempted"] is False

    summary.update(multi_summary)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
