"""Offline tests for the ZIGO-derived VIZZ/PUPILA vertical slice."""

from __future__ import annotations

from pathlib import Path
import sys
import json


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from contracts import append_audit_event, normalize_signal, verify_audit_chain  # noqa: E402
from canonical_event_bridge import CanonicalEventBridge, CanonicalEventError  # noqa: E402
from pupila_adapter import PupilaAdapter  # noqa: E402
from vizz_adapter import VizzAdapter  # noqa: E402


def context(room: str = "room-demo", participant: str = "user-a") -> dict[str, object]:
    return {
        "sessionId": "session-demo",
        "roomId": room,
        "surfaceId": "surface-demo",
        "host": "fixture-host",
        "task": "shared-workflow",
        "capabilities": ["pointer", "keyboard", "focus"],
        "viewport": {"width": 1920, "height": 1080, "unit": "px"},
        "participantRef": participant,
    }


def signal(participant: str, kind: str, at_ms: int, value: dict[str, object]) -> dict[str, object]:
    return {
        "sessionId": "session-demo",
        "roomId": "room-demo",
        "surfaceId": "surface-demo",
        "participantRef": participant,
        "kind": kind,
        "atMs": at_ms,
        "value": value,
        "consent": True,
    }


def canonical_event(
    event_id: str,
    *,
    peer_id: str = "user-a",
    event_type: str = "connectivity.status",
    channel: str = "transport",
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "event_id": event_id,
        "schema_version": 1,
        "source_app": "XIO",
        "event_type": event_type,
        "channel": channel,
        "payload": payload or {"state": "connected"},
        "source_timestamp": "2026-09-01T12:00:00Z",
        "received_timestamp": "2026-09-01T12:00:00.050Z",
        "session_id": "session-demo",
        "peer_id": peer_id,
        "sequence": 1,
        "raw_hash": "sha256:canonical-event-fixture",
        "provenance": {"rootId": "xio-root-1", "measuredBy": "host"},
    }


def test_consent_blocks_signal_and_drops_content() -> None:
    event = normalize_signal({"kind": "keyboard", "value": {"text": "secret"}, "consent": False})
    assert event["accepted"] is False
    assert event["reason"] == "consent-required"
    assert event["value"] == {}


def test_vizz_is_metadata_only_and_becomes_quiet_when_active() -> None:
    adapter = VizzAdapter()
    ctx = context(participant="user-a")
    state = adapter.ingest(ctx, signal("user-a", "focus", 100, {"focused": True}))
    for index in range(6):
        state = adapter.ingest(ctx, signal("user-a", "keyboard", 200 + index * 100, {"count": 1, "text": "never-persist"}))
    assert state["adapter"] == "vizz"
    assert state["policy"] in {"support", "quiet"}
    assert state["overlay"]["blocking"] is False
    assert state["overlay"]["clickThrough"] is True
    assert state["gazeQualityMean"] is None


def test_pupila_emerges_shared_checkpoint_for_two_different_policies() -> None:
    vizz = VizzAdapter()
    pupila = PupilaAdapter()
    ctx_a = context(participant="user-a")
    ctx_b = context(participant="user-b")
    state_a = vizz.ingest(ctx_a, signal("user-a", "focus", 100, {"focused": True}))
    state_b = vizz.ingest(ctx_b, signal("user-b", "focus", 100, {"focused": False}))
    pupila.ingest(ctx_a, state_a)
    room = pupila.ingest(ctx_b, state_b)
    assert room["participantCount"] == 2
    assert room["proposals"]
    assert room["proposals"][0]["state"] == "proposed"
    assert room["proposals"][0]["requiresExplicitAcceptance"] is True
    assert room["proposals"][0]["action"] is None


def test_pupila_does_not_register_unconsented_presence() -> None:
    vizz = VizzAdapter()
    pupila = PupilaAdapter()
    ctx = context(participant="user-a")
    state = vizz.state(ctx, "user-a")
    room = pupila.ingest(ctx, state)
    assert room["participantCount"] == 0


def test_pupila_rejects_cross_room_state() -> None:
    vizz = VizzAdapter()
    pupila = PupilaAdapter()
    state = vizz.ingest(context(room="room-a"), signal("user-a", "focus", 100, {"focused": True}))
    try:
        pupila.ingest(context(room="room-b"), state)
    except ValueError as error:
        assert "different rooms" in str(error)
    else:
        raise AssertionError("cross-room state was accepted")


def test_pupila_does_not_mix_sessions_with_same_room_id() -> None:
    vizz = VizzAdapter()
    pupila = PupilaAdapter()
    session_a = context(participant="user-a")
    session_b = {**context(participant="user-b"), "sessionId": "session-other"}
    state_a = vizz.ingest(session_a, signal("user-a", "focus", 100, {"focused": True}))
    state_b = vizz.ingest(
        session_b,
        {
            **signal("user-b", "focus", 100, {"focused": True}),
            "sessionId": "session-other",
        },
    )
    room_a = pupila.ingest(session_a, state_a)
    room_b = pupila.ingest(session_b, state_b)
    assert room_a["participantCount"] == 1
    assert room_b["participantCount"] == 1
    assert room_a["sessionId"] != room_b["sessionId"]


def test_audit_chain_is_replayable_and_tamper_evident() -> None:
    events: list[dict[str, object]] = []
    append_audit_event(events, "context.received", {"contextHash": "sha256:context"}, timestamp=1)
    append_audit_event(events, "proposal.created", {"proposalId": "proposal-1"}, timestamp=2)
    assert verify_audit_chain(events)["valid"] is True
    events[1]["payload"] = {"proposalId": "proposal-tampered"}
    assert verify_audit_chain(events)["valid"] is False


def test_canonical_connectivity_event_is_metadata_only() -> None:
    bridge = CanonicalEventBridge()
    result = bridge.ingest(
        canonical_event("canonical-event-001", payload={"state": "connected", "secret": "never-persist"}),
        context(),
        consent=True,
    )
    assert result["status"] == "accepted"
    assert result["signal"]["kind"] == "presence"
    assert result["vizzState"]["signalCoverage"] == ["presence"]
    assert result["vizzState"]["activityScore"] == 0.0
    assert "secret" not in json.dumps(result, ensure_ascii=True)
    assert result["lineage"]["sourceEventId"] == "canonical-event-001"


def test_canonical_keyboard_event_drops_text_and_keeps_shortcut_metadata() -> None:
    bridge = CanonicalEventBridge()
    result = bridge.ingest(
        canonical_event(
            "canonical-event-002",
            event_type="keyboard.input",
            channel="keyboard",
            payload={"text": "PASSWORD", "count": 2, "shortcut": "CTRL+K"},
        ),
        context(),
        consent=True,
    )
    value = result["signal"]["value"]
    assert result["signal"]["kind"] == "keyboard"
    assert value == {"count": 2, "shortcut": "CTRL+K"}
    assert result["vizzState"]["activityScore"] > 0.0
    assert "PASSWORD" not in json.dumps(result, ensure_ascii=True)


def test_unconsented_canonical_event_is_blocked_before_registration() -> None:
    bridge = CanonicalEventBridge()
    result = bridge.ingest(
        canonical_event("canonical-event-003", payload={"state": "connected", "secret": "blocked"}),
        context(),
        consent=False,
    )
    assert result["status"] == "blocked"
    assert result["signal"]["value"] == {}
    assert result["vizzState"]["sampleCount"] == 0
    assert result["pupilaState"]["participantCount"] == 0
    assert "blocked" in result["signal"]["status"]
    assert "secret" not in json.dumps(result, ensure_ascii=True)


def test_duplicate_external_event_is_idempotent() -> None:
    bridge = CanonicalEventBridge()
    event = canonical_event("canonical-event-004", event_type="focus.changed", channel="focus", payload={"focused": True})
    first = bridge.ingest(event, context(), consent=True)
    second = bridge.ingest(event, context(), consent=True)
    assert first["status"] == "accepted"
    assert second["status"] == "duplicate"
    assert first["vizzState"]["sampleCount"] == 1
    assert second["vizzState"]["sampleCount"] == 1


def test_two_canonical_peers_produce_a_pupila_proposal() -> None:
    bridge = CanonicalEventBridge()
    bridge.ingest(
        canonical_event("canonical-event-005", peer_id="user-a", event_type="focus.changed", channel="focus", payload={"focused": True}),
        context(participant="user-a"),
        consent=True,
    )
    result = bridge.ingest(
        canonical_event("canonical-event-006", peer_id="user-b", event_type="focus.changed", channel="focus", payload={"focused": False}),
        context(participant="user-b"),
        consent=True,
    )
    assert result["pupilaState"]["participantCount"] == 2
    assert result["pupilaState"]["proposals"]
    assert result["pupilaState"]["proposals"][0]["requiresExplicitAcceptance"] is True
    assert result["pupilaState"]["proposals"][0]["action"] is None


def test_malformed_canonical_event_is_rejected() -> None:
    bridge = CanonicalEventBridge()
    malformed = canonical_event("canonical-event-007")
    del malformed["raw_hash"]
    try:
        bridge.ingest(malformed, context(), consent=True)
    except CanonicalEventError as error:
        assert "missing fields" in str(error)
    else:
        raise AssertionError("malformed canonical event was accepted")


if __name__ == "__main__":
    tests = [
        test_consent_blocks_signal_and_drops_content,
        test_vizz_is_metadata_only_and_becomes_quiet_when_active,
        test_pupila_emerges_shared_checkpoint_for_two_different_policies,
        test_pupila_does_not_register_unconsented_presence,
        test_pupila_rejects_cross_room_state,
        test_pupila_does_not_mix_sessions_with_same_room_id,
        test_audit_chain_is_replayable_and_tamper_evident,
        test_canonical_connectivity_event_is_metadata_only,
        test_canonical_keyboard_event_drops_text_and_keeps_shortcut_metadata,
        test_unconsented_canonical_event_is_blocked_before_registration,
        test_duplicate_external_event_is_idempotent,
        test_two_canonical_peers_produce_a_pupila_proposal,
        test_malformed_canonical_event_is_rejected,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"FARMAXIA_090_CONTRACT_VALID ({len(tests)} tests)")
