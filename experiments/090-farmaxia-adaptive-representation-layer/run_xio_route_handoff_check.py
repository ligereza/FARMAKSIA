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
    summary = {
        "routeStatus": route_plan["status"],
        "selectedSource": selection.source_app,
        "handoffStatus": "prepared",
        "projectedPayloadKeys": sorted(handoff.event.payload),
        "transportChannel": handoff.message.channel,
        "roundTripEventPreserved": recovered.event_id == handoff.event.event_id,
        "auditVerified": audit.verify(),
        "executionAttempted": False,
    }
    assert summary["routeStatus"] == "matched"
    assert summary["selectedSource"] == "XIO"
    assert summary["projectedPayloadKeys"] == []
    assert summary["transportChannel"] == "application-event"
    assert summary["roundTripEventPreserved"] is True
    assert summary["auditVerified"] is True
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
