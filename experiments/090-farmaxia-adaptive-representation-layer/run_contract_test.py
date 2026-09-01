"""Offline tests for the ZIGO-derived VIZZ/PUPILA vertical slice."""

from __future__ import annotations

from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from contracts import append_audit_event, normalize_signal, verify_audit_chain  # noqa: E402
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


def test_audit_chain_is_replayable_and_tamper_evident() -> None:
    events: list[dict[str, object]] = []
    append_audit_event(events, "context.received", {"contextHash": "sha256:context"}, timestamp=1)
    append_audit_event(events, "proposal.created", {"proposalId": "proposal-1"}, timestamp=2)
    assert verify_audit_chain(events)["valid"] is True
    events[1]["payload"] = {"proposalId": "proposal-tampered"}
    assert verify_audit_chain(events)["valid"] is False


if __name__ == "__main__":
    tests = [
        test_consent_blocks_signal_and_drops_content,
        test_vizz_is_metadata_only_and_becomes_quiet_when_active,
        test_pupila_emerges_shared_checkpoint_for_two_different_policies,
        test_pupila_does_not_register_unconsented_presence,
        test_pupila_rejects_cross_room_state,
        test_audit_chain_is_replayable_and_tamper_evident,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"FARMAXIA_090_CONTRACT_VALID ({len(tests)} tests)")
