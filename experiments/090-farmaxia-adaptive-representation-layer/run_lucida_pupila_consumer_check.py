"""Verify LUCIDA consumes PUPILA snapshots and diffs without side effects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from canonical_event_bridge import CanonicalEventReplay  # noqa: E402
from pupila_lucida_projection import project_pupila_for_lucida  # noqa: E402
from lucida_render_plan import build_lucida_render_plan  # noqa: E402


def _event(event_id: str, peer_id: str, sequence: int, focused: bool) -> dict[str, object]:
    timestamp = f"2026-09-01T12:00:0{sequence}Z"
    return {
        "event_id": event_id,
        "schema_version": 1,
        "source_app": "XIO",
        "event_type": "focus.changed",
        "channel": "focus",
        "payload": {"focused": focused},
        "source_timestamp": timestamp,
        "received_timestamp": timestamp,
        "session_id": "session-pupila-lucida",
        "peer_id": peer_id,
        "sequence": sequence,
        "raw_hash": f"sha256:{event_id}",
        "provenance": {"rootId": "pupila-lucida-check", "measuredBy": "fixture"},
    }


def _cursor(sequence: int, event_id: str | None) -> dict[str, object]:
    timestamp = f"2026-09-01T12:00:0{sequence}Z" if event_id else None
    return {
        "contract_type": "LucidaOverlayCursor",
        "schema_version": "0.1",
        "surface": "LUCIDA",
        "mode": "read_only",
        "session_id": "session-pupila-lucida",
        "sequence": sequence,
        "last_event_id": event_id,
        "last_timestamp": timestamp,
        "checkpoint_id": f"checkpoint-{sequence}" if event_id else None,
        "safety": {
            "proposal_only": True,
            "automatic_actions": False,
            "external_side_effects": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lucida-root", required=True)
    args = parser.parse_args()

    lucida_root = Path(args.lucida_root).resolve()
    if not lucida_root.is_dir():
        raise FileNotFoundError(f"LUCIDA root does not exist: {lucida_root}")
    for module_name in list(sys.modules):
        if module_name == "lucida" or module_name.startswith("lucida."):
            del sys.modules[module_name]
    sys.path.insert(0, str(lucida_root))
    import lucida  # noqa: PLC0415

    loaded_lucida_path = Path(lucida.__file__).resolve()
    try:
        loaded_lucida_path.relative_to(lucida_root)
    except ValueError as error:
        raise AssertionError(
            f"loaded LUCIDA package is outside requested root: {loaded_lucida_path}"
        ) from error

    from lucida.overlay import diff_overlay_view, overlay_view_digest  # noqa: E402
    from lucida.overlay_consumer import (  # noqa: E402
        OverlayConsumer,
        OverlayConsumerConflictError,
    )

    report = CanonicalEventReplay().run(
        [
            _event("pupila-lucida-001", "peer-1", 1, True),
            _event("pupila-lucida-002", "peer-2", 2, False),
        ],
        {
            "roomId": "room-pupila-lucida",
            "surfaceId": "surface-pupila-lucida",
            "task": "consume-pupila-diff",
        },
        consent=True,
    )
    views = [
        project_pupila_for_lucida(result["pupilaView"])
        for result in report["results"]
    ]
    consumer = OverlayConsumer()
    consumer.accept_snapshot(views[0], _cursor(0, None))
    applied_diffs = []
    for index in range(1, len(views)):
        changes = diff_overlay_view(views[index - 1], views[index])
        cursor = _cursor(index, report["results"][index]["eventId"])
        update = {
            "contract_type": "LucidaOverlayUpdate",
            "schema_version": "0.1",
            "surface": "LUCIDA",
            "mode": "read_only",
            "view": views[index],
            "view_digest": overlay_view_digest(views[index]),
            "changes": changes,
            "cursor": cursor,
            "safety": {
                "proposal_only": True,
                "automatic_actions": False,
                "external_side_effects": False,
            },
        }
        before_failed_update = consumer.state
        tampered_update = {
            **update,
            "view": {**views[index], "status": "tampered"},
        }
        try:
            consumer.apply_update(tampered_update)
        except OverlayConsumerConflictError:
            pass
        else:
            raise AssertionError("tampered atomic update was accepted")
        assert consumer.state == before_failed_update
        consumer.apply_update(update)
        applied_diffs.append(changes)

    final_view = consumer.view
    render_plan = build_lucida_render_plan(final_view)
    summary = {
        "lucidaRoot": str(lucida_root),
        "loadedLucidaPath": str(loaded_lucida_path),
        "pupilaAcceptedCount": report["acceptedCount"],
        "pupilaParticipantCount": report["finalPupilaView"]["participantCount"],
        "pupilaProposalKind": report["finalPupilaView"]["proposals"][0]["kind"],
        "lucidaAppliedUpdateCount": consumer.state.applied_delta_count,
        "lucidaFinalProposalCount": len(final_view["pending_proposals"]),
        "lucidaFinalProposalOperation": final_view["pending_proposals"][0]["operation"],
        "lucidaSafety": final_view["safety"],
        "lucidaRenderElementCount": len(render_plan["elements"]),
        "lucidaRenderIntensity": render_plan["intensity"],
        "lucidaRenderClickThrough": render_plan["clickThrough"],
        "automaticActions": False,
        "externalSideEffects": False,
        "rawPayloadForwarded": any("payload" in result for result in report["results"]),
        "diffFieldCounts": [len(changes) for changes in applied_diffs],
    }
    assert summary["pupilaAcceptedCount"] == 2
    assert summary["pupilaParticipantCount"] == 2
    assert summary["pupilaProposalKind"] == "shared-checkpoint"
    assert summary["lucidaAppliedUpdateCount"] == 1
    assert summary["lucidaFinalProposalCount"] == 1
    assert summary["lucidaFinalProposalOperation"] == "pupila.coordinate"
    assert summary["lucidaRenderElementCount"] == 3
    assert summary["lucidaRenderIntensity"] == "high"
    assert summary["lucidaRenderClickThrough"] is True
    assert summary["lucidaSafety"]["proposal_only"] is True
    assert summary["lucidaSafety"]["automatic_actions"] is False
    assert summary["lucidaSafety"]["external_side_effects"] is False
    assert summary["rawPayloadForwarded"] is False
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
