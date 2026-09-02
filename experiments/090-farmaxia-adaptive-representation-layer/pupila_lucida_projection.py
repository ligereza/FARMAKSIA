"""Project a safe PUPILA view into the generic LUCIDA overlay contract."""

from __future__ import annotations

from typing import Any, Mapping

from pupila_view import diff_pupila_view


class PupilaLucidaProjectionError(ValueError):
    """Raised when a PUPILA view cannot cross the LUCIDA overlay boundary."""


def project_pupila_for_lucida(
    pupila_view: Mapping[str, Any],
    *,
    phase: str = "preparation",
) -> dict[str, Any]:
    """Create a lossy, proposal-only LUCIDA view from a PUPILA projection.

    The adapter carries only shared-surface counts and coordination proposals.
    It deliberately drops participant references, signal coverage, room IDs,
    activity values and all source payloads. It does not claim that PUPILA
    participants are LUCIDA capabilities.
    """

    if not isinstance(pupila_view, Mapping):
        raise PupilaLucidaProjectionError("pupila_view must be a mapping")
    try:
        diff_pupila_view(pupila_view, pupila_view)
    except ValueError as exc:
        raise PupilaLucidaProjectionError(str(exc)) from exc
    if not isinstance(phase, str) or not phase.strip():
        raise PupilaLucidaProjectionError("phase must be non-empty text")

    participant_count = pupila_view["participantCount"]
    proposal_count = pupila_view["proposalCount"]
    proposals = pupila_view["proposals"]
    if not isinstance(participant_count, int) or isinstance(participant_count, bool):
        raise PupilaLucidaProjectionError("participantCount must be an integer")
    if not isinstance(proposal_count, int) or isinstance(proposal_count, bool):
        raise PupilaLucidaProjectionError("proposalCount must be an integer")
    if not isinstance(proposals, list):
        raise PupilaLucidaProjectionError("proposals must be a list")

    pending_proposals = [
        {
            "proposal_id": proposal["proposalId"],
            "event_id": proposal["proposalId"],
            "phase": phase.strip(),
            "operation": "pupila.coordinate",
            "reason": proposal["reason"],
            "risk": "unknown",
            "requires_explicit_approval": True,
            "reversible": True,
            "execution_mode": "proposal_only",
        }
        for proposal in proposals
    ]
    if pending_proposals:
        next_attention = {
            "kind": "proposal",
            "id": pending_proposals[0]["proposal_id"],
            "reason": pending_proposals[0]["reason"],
        }
    else:
        next_attention = {
            "kind": "phase",
            "id": f"phase-{phase.strip()}",
            "reason": "Awaiting the next shared-surface event.",
        }

    return {
        "contract_type": "LucidaOverlayView",
        "schema_version": "0.1",
        "surface": "LUCIDA",
        "mode": "read_only",
        "session_id": str(pupila_view["sessionId"]),
        "phase": phase.strip(),
        "status": "observing" if participant_count else "created",
        "overlay_status": "proposal" if pending_proposals else "ready",
        "capabilities": [
            {
                "capability": "pupila.shared-surface",
                "state": {
                    "status": f"participants:{participant_count}",
                    "signal_status": "metadata-only",
                },
                "observed_count": participant_count,
                "expected_result_count": proposal_count,
                "unknowns": [],
            }
        ],
        "pending_proposals": pending_proposals,
        "unknowns": [],
        "next_attention": next_attention,
        "safety": {
            "proposal_only": True,
            "automatic_actions": False,
            "external_side_effects": False,
        },
    }


__all__ = ["PupilaLucidaProjectionError", "project_pupila_for_lucida"]
