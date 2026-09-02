"""Offline tests for the ZIGO-derived VIZZ/PUPILA vertical slice."""

from __future__ import annotations

from pathlib import Path
import sys
import json
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from contracts import append_audit_event, normalize_signal, verify_audit_chain  # noqa: E402
from canonical_event_bridge import CanonicalEventBridge, CanonicalEventError, CanonicalEventReplay  # noqa: E402
from boundary_matrix import inspect_matrix  # noqa: E402
from pupila_adapter import PupilaAdapter  # noqa: E402
from pupila_view import (  # noqa: E402
    MAX_DIFF_CHANGES,
    MAX_PARTICIPANTS,
    MAX_PROPOSALS,
    diff_pupila_view,
    project_pupila_view,
)
from pupila_lucida_projection import project_pupila_for_lucida  # noqa: E402
from lucida_render_plan import (  # noqa: E402
    LucidaRenderPlanError,
    build_lucida_render_plan,
)
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
    assert result["pupilaView"]["contractType"] == "PupilaOverlayView"
    assert result["pupilaView"]["nextAttention"]["kind"] == "waiting"
    assert "secret" not in json.dumps(result, ensure_ascii=True)
    assert '"payload":' not in json.dumps(result, ensure_ascii=True)
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
    assert result["pupilaView"]["participantCount"] == 0
    assert result["pupilaView"]["nextAttention"]["kind"] == "waiting"
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
    assert first["pupilaView"] == second["pupilaView"]


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


def test_canonical_replay_is_deterministic_and_keeps_final_multi_state() -> None:
    replay = CanonicalEventReplay()
    results = replay.run(
        [
            canonical_event(
                "canonical-event-008",
                peer_id="user-a",
                event_type="focus.changed",
                channel="focus",
                payload={"focused": True},
            ),
            canonical_event(
                "canonical-event-009",
                peer_id="user-b",
                event_type="focus.changed",
                channel="focus",
                payload={"focused": False},
            ),
            canonical_event(
                "canonical-event-009",
                peer_id="user-b",
                event_type="focus.changed",
                channel="focus",
                payload={"focused": False},
            ),
        ],
        context(),
        consent=True,
    )
    assert results["status"] == "complete"
    assert results["eventCount"] == 3
    assert results["acceptedCount"] == 2
    assert results["duplicateCount"] == 1
    assert results["blockedCount"] == 0
    assert results["finalPupilaState"]["participantCount"] == 2
    assert results["finalPupilaState"]["proposals"]
    assert results["finalPupilaView"]["contractType"] == "PupilaOverlayView"
    assert results["finalPupilaView"]["nextAttention"]["kind"] == "proposal"
    assert results["pupilaViewDiffs"][0]["fromEventId"] is None
    assert results["pupilaViewDiffs"][-1]["changes"] == []
    assert "payload" not in json.dumps(results, ensure_ascii=True)


def test_canonical_replay_reports_bounded_interaction_metrics() -> None:
    replay = CanonicalEventReplay()
    result = replay.run(
        [
            canonical_event(
                "canonical-event-metrics-001",
                event_type="focus.changed",
                channel="focus",
                payload={"focused": True},
            ),
            canonical_event(
                "canonical-event-metrics-002",
                event_type="pointer.moved",
                channel="pointer",
                payload={"x": 120, "y": 80, "secret": "never-persist"},
            ),
            canonical_event(
                "canonical-event-metrics-003",
                event_type="keyboard.input",
                channel="keyboard",
                payload={"count": 2, "shortcut": "CTRL+K", "text": "secret"},
            ),
            canonical_event(
                "canonical-event-metrics-003",
                event_type="keyboard.input",
                channel="keyboard",
                payload={"count": 2, "shortcut": "CTRL+K", "text": "secret"},
            ),
        ],
        context(),
        consent=True,
    )
    metrics = result["interactionMetrics"]
    assert metrics["statusCounts"] == {"accepted": 3, "duplicate": 1}
    assert metrics["kindStatusCounts"]["focus"] == {"accepted": 1}
    assert metrics["kindStatusCounts"]["pointer"] == {"accepted": 1}
    assert metrics["kindStatusCounts"]["keyboard"] == {"accepted": 1, "duplicate": 1}
    assert metrics["participants"] == [
        {
            "participantRef": "user-a",
            "policy": "support",
            "focusState": True,
            "activityScore": 0.23125,
            "sampleCount": 3,
            "signalCoverage": ["focus", "keyboard", "pointer"],
        }
    ]
    final_participant = result["finalPupilaView"]["participants"][0]
    assert final_participant["interaction"] == {
        "sampleCount": 3,
        "signalCoverage": ["focus", "keyboard", "pointer"],
    }
    serialized = json.dumps(metrics, ensure_ascii=True)
    assert "secret" not in serialized
    assert "never-persist" not in serialized
    assert any(
        change["field"] == "participants"
        for change in result["pupilaViewDiffs"][1]["changes"]
    )
    assert result["pupilaViewDiffs"][-1]["changes"] == []


def test_pupila_view_is_bounded_and_redacts_internal_state() -> None:
    raw_state = {
        "schemaVersion": 1,
        "sessionId": "session-view",
        "roomId": "room-view",
        "surfaceId": "surface-view",
        "participantCount": 2,
        "participants": [
            {
                "participantRef": "user-b",
                "policy": "support",
                "focusState": True,
                "activityScore": 0.7,
                "stateHash": "sha256:private-state",
            },
            {
                "participantRef": "user-a",
                "policy": "guide",
                "focusState": False,
                "activityScore": 0.1,
                "stateHash": "sha256:other-state",
            },
        ],
        "proposals": [
            {
                "proposalId": "proposal-view",
                "kind": "peer-bridge",
                "reason": "One participant can provide a shared next step.",
                "state": "proposed",
                "requiresExplicitAcceptance": True,
                "reversible": True,
                "action": "must-not-leak",
            }
        ],
    }

    view = project_pupila_view(raw_state)
    serialized = json.dumps(view, sort_keys=True)

    assert view["contractType"] == "PupilaOverlayView"
    assert view["participants"][0]["participantRef"] == "user-a"
    assert view["nextAttention"]["proposalId"] == "proposal-view"
    assert view["safety"]["proposalOnly"] is True
    assert "activityScore" not in serialized
    assert "stateHash" not in serialized
    assert "must-not-leak" not in serialized
    assert '"action":' not in serialized


def test_pupila_view_is_deterministic_after_participant_reordering() -> None:
    base = {
        "sessionId": "session-deterministic",
        "roomId": "room-deterministic",
        "surfaceId": "surface-deterministic",
        "participants": [
            {"participantRef": "user-b", "policy": "quiet", "focusState": True},
            {"participantRef": "user-a", "policy": "support", "focusState": False},
        ],
        "proposals": [
            {
                "proposalId": "proposal-2",
                "kind": "co-presence",
                "reason": "Shared surface.",
                "state": "proposed",
                "requiresExplicitAcceptance": True,
                "reversible": True,
            },
            {
                "proposalId": "proposal-1",
                "kind": "peer-bridge",
                "reason": "Shared next step.",
                "state": "proposed",
                "requiresExplicitAcceptance": True,
                "reversible": True,
            },
        ],
    }
    reordered = {**base, "participants": list(reversed(base["participants"]))}

    assert project_pupila_view(base) == project_pupila_view(reordered)


def test_pupila_view_limits_and_empty_state_are_explicit() -> None:
    state = {
        "sessionId": "session-limits",
        "roomId": "room-limits",
        "surfaceId": "surface-limits",
        "participants": [
            {"participantRef": f"user-{index:02d}", "policy": "quiet", "focusState": False}
            for index in range(MAX_PARTICIPANTS + 2)
        ],
        "proposals": [
            {
                "proposalId": f"proposal-{index:02d}",
                "kind": "co-presence",
                "reason": "Shared surface.",
                "state": "proposed",
                "requiresExplicitAcceptance": True,
                "reversible": True,
            }
            for index in range(MAX_PROPOSALS + 2)
        ],
    }
    view = project_pupila_view(state)
    empty = project_pupila_view({"sessionId": "s", "roomId": "r", "surfaceId": "f"})

    assert view["participantCount"] == MAX_PARTICIPANTS + 2
    assert view["shownParticipantCount"] == MAX_PARTICIPANTS
    assert view["proposalCount"] == MAX_PROPOSALS + 2
    assert view["shownProposalCount"] == MAX_PROPOSALS
    assert empty["nextAttention"]["kind"] == "waiting"

    try:
        project_pupila_view(state, max_proposals=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative view limit was accepted")


def test_pupila_view_diff_is_deterministic_bounded_and_redacted() -> None:
    previous = project_pupila_view(
        {
            "sessionId": "session-diff",
            "roomId": "room-diff",
            "surfaceId": "surface-diff",
            "participants": [
                {"participantRef": "user-a", "policy": "quiet", "focusState": True},
            ],
            "proposals": [],
        }
    )
    current = project_pupila_view(
        {
            "sessionId": "session-diff",
            "roomId": "room-diff",
            "surfaceId": "surface-diff",
            "participants": [
                {"participantRef": "user-a", "policy": "quiet", "focusState": True},
                {"participantRef": "user-b", "policy": "support", "focusState": False},
            ],
            "proposals": [
                {
                    "proposalId": "proposal-diff",
                    "kind": "co-presence",
                    "reason": "A shared surface is available.",
                    "state": "proposed",
                    "requiresExplicitAcceptance": True,
                    "reversible": True,
                    "action": "must-not-leak",
                }
            ],
        }
    )

    first = diff_pupila_view(previous, current)
    second = diff_pupila_view(previous, current)
    serialized = json.dumps(first, sort_keys=True)

    assert first == second
    assert [item["field"] for item in first] == [
        "participantCount",
        "shownParticipantCount",
        "proposalCount",
        "shownProposalCount",
        "participants",
        "proposals",
        "nextAttention",
    ]
    assert len(first) <= MAX_DIFF_CHANGES
    assert "must-not-leak" not in serialized
    assert '"action":' not in serialized
    assert diff_pupila_view(previous, previous) == []


def test_pupila_view_diff_rejects_unsafe_or_invalid_views() -> None:
    view = project_pupila_view(
        {
            "sessionId": "session-invalid",
            "roomId": "room-invalid",
            "surfaceId": "surface-invalid",
            "participants": [],
            "proposals": [],
        }
    )

    unsafe = dict(view)
    unsafe["rawPayload"] = {"secret": "must-not-enter"}
    try:
        diff_pupila_view(view, unsafe)
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe PUPILA view was accepted")

    invalid_safety = dict(view)
    invalid_safety["safety"] = {**view["safety"], "actionsIncluded": True}
    try:
        diff_pupila_view(view, invalid_safety)
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe PUPILA safety was accepted")


def test_boundary_matrix_accepts_separated_surfaces() -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        farmaxia = root / "farmaxia"
        vj = root / "vj"
        adobe = root / "adobe"
        resolume = root / "resolume"
        multi = root / "multi"
        xio = root / "xio"
        for path in (farmaxia, vj, adobe, resolume, multi, xio):
            path.mkdir()
        for name in (
            "canonical_event_bridge.py",
            "pupila_adapter.py",
            "pupila_view.py",
            "vizz_adapter.py",
        ):
            (farmaxia / name).touch()
        (vj / "lucida").mkdir()
        (adobe / "adobe").mkdir()
        for name in ("lucida", "resolume", "adapters"):
            (resolume / name).mkdir()
        for name in ("XIO_LAYER", "multi"):
            (multi / name).mkdir()
        (xio / "XIO_LAYER").mkdir()

        report = inspect_matrix(
            {
                "farmaxia_vizz_pupila": farmaxia,
                "vj_lucida": vj,
                "lucida_adobe": adobe,
                "lucida_resolume": resolume,
                "lucida_multi": multi,
                "xio": xio,
            }
        )
        assert report["status"] == "PASS"
        assert report["failedCount"] == 0
        assert report["networkOpened"] is False
        assert report["guiOpened"] is False
        assert report["hostActionsExecuted"] is False


def test_boundary_matrix_rejects_cross_surface_contamination() -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "adobe").mkdir()
        (root / "XIO_LAYER").mkdir()
        report = inspect_matrix({"lucida_adobe": root})
        assert report["status"] == "FAIL"
        assert report["failedCount"] == 1
        assert report["checks"][0]["forbidden"] == ["XIO_LAYER"]


def test_lucida_render_plan_is_deterministic_and_non_blocking() -> None:
    view = project_pupila_for_lucida(
        project_pupila_view(
            {
                "sessionId": "session-render",
                "roomId": "room-render",
                "surfaceId": "surface-render",
                "participants": [
                    {"participantRef": "user-a", "policy": "guide", "focusState": True},
                    {"participantRef": "user-b", "policy": "anchor", "focusState": False},
                ],
                "proposals": [
                    {
                        "proposalId": "proposal-render",
                        "kind": "shared-checkpoint",
                        "reason": "The shared surface needs a visible checkpoint.",
                        "state": "proposed",
                        "requiresExplicitAcceptance": True,
                        "reversible": True,
                    }
                ],
            }
        )
    )
    first = build_lucida_render_plan(view)
    second = build_lucida_render_plan(view)
    serialized = json.dumps(first, sort_keys=True)

    assert first == second
    assert first["contractType"] == "LucidaRenderPlan"
    assert first["transparent"] is True
    assert first["clickThrough"] is True
    assert first["blocking"] is False
    assert first["intensity"] == "high"
    assert first["safety"]["proposalOnly"] is True
    assert first["safety"]["automaticActions"] is False
    assert first["safety"]["externalSideEffects"] is False
    assert first["safety"]["rawPayloadIncluded"] is False
    assert '"action":' not in serialized
    assert '"payload":' not in serialized
    assert '"coordinates":' not in serialized


def test_lucida_render_plan_rejects_unsafe_view_fields() -> None:
    view = project_pupila_for_lucida(
        project_pupila_view(
            {
                "sessionId": "session-render-invalid",
                "roomId": "room-render-invalid",
                "surfaceId": "surface-render-invalid",
                "participants": [],
                "proposals": [],
            }
        )
    )
    unsafe = dict(view)
    unsafe["rawPayload"] = {"secret": "must-not-enter"}
    try:
        build_lucida_render_plan(unsafe)
    except LucidaRenderPlanError:
        pass
    else:
        raise AssertionError("unsafe LUCIDA render input was accepted")


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
        test_canonical_replay_is_deterministic_and_keeps_final_multi_state,
        test_pupila_view_is_bounded_and_redacts_internal_state,
        test_pupila_view_is_deterministic_after_participant_reordering,
        test_pupila_view_limits_and_empty_state_are_explicit,
        test_pupila_view_diff_is_deterministic_bounded_and_redacted,
        test_pupila_view_diff_rejects_unsafe_or_invalid_views,
        test_boundary_matrix_accepts_separated_surfaces,
        test_boundary_matrix_rejects_cross_surface_contamination,
        test_lucida_render_plan_is_deterministic_and_non_blocking,
        test_lucida_render_plan_rejects_unsafe_view_fields,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"FARMAXIA_090_CONTRACT_VALID ({len(tests)} tests)")
