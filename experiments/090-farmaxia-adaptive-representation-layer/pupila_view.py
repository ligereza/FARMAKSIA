"""Bounded read-only projection for the PUPILA shared surface."""

from __future__ import annotations

from typing import Any, Mapping


PUPILA_VIEW_SCHEMA_VERSION = 1
MAX_PARTICIPANTS = 16
MAX_PROPOSALS = 8
MAX_DISPLAY_TEXT = 240
_KIND_ORDER = {"peer-bridge": 0, "shared-checkpoint": 1, "co-presence": 2}


class PupilaViewError(ValueError):
    """Raised when a PUPILA view cannot be represented safely."""


def project_pupila_view(
    raw_state: Mapping[str, Any],
    *,
    max_participants: int = MAX_PARTICIPANTS,
    max_proposals: int = MAX_PROPOSALS,
) -> dict[str, Any]:
    """Project one PUPILA state into bounded multi-participant overlay data."""

    if not isinstance(raw_state, Mapping):
        raise PupilaViewError("PUPILA state must be an object")
    _limit(max_participants, "max_participants")
    _limit(max_proposals, "max_proposals")

    participants = raw_state.get("participants", [])
    proposals = raw_state.get("proposals", [])
    if not isinstance(participants, list) or not isinstance(proposals, list):
        raise PupilaViewError("participants and proposals must be lists")

    participant_views = sorted(
        (_participant_view(item) for item in participants),
        key=lambda item: item["participantRef"],
    )
    proposal_views = sorted(
        (_proposal_view(item) for item in proposals),
        key=lambda item: (_KIND_ORDER.get(item["kind"], len(_KIND_ORDER)), item["proposalId"]),
    )
    visible_participants = participant_views[:max_participants]
    visible_proposals = proposal_views[:max_proposals]

    return {
        "contractType": "PupilaOverlayView",
        "schemaVersion": PUPILA_VIEW_SCHEMA_VERSION,
        "surface": "PUPILA",
        "mode": "read_only",
        "sessionId": _text(raw_state.get("sessionId"), "sessionId"),
        "roomId": _text(raw_state.get("roomId"), "roomId"),
        "surfaceId": _text(raw_state.get("surfaceId"), "surfaceId"),
        "participantCount": len(participant_views),
        "shownParticipantCount": len(visible_participants),
        "proposalCount": len(proposal_views),
        "shownProposalCount": len(visible_proposals),
        "participants": visible_participants,
        "proposals": visible_proposals,
        "nextAttention": _next_attention(visible_proposals, len(participant_views)),
        "safety": {
            "proposalOnly": True,
            "requiresExplicitAcceptance": True,
            "reversible": True,
            "blocking": False,
            "clickThrough": True,
            "rawSignalsIncluded": False,
            "actionsIncluded": False,
        },
    }


def _participant_view(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise PupilaViewError("participant must be an object")
    return {
        "participantRef": _text(value.get("participantRef"), "participantRef"),
        "policy": _text(value.get("policy"), "policy"),
        "focusState": value.get("focusState") is True,
    }


def _proposal_view(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise PupilaViewError("proposal must be an object")
    return {
        "proposalId": _text(value.get("proposalId"), "proposalId"),
        "kind": _text(value.get("kind"), "kind"),
        "reason": _text(value.get("reason"), "reason"),
        "state": _text(value.get("state"), "state"),
        "requiresExplicitAcceptance": value.get("requiresExplicitAcceptance") is True,
        "reversible": value.get("reversible") is True,
    }


def _next_attention(proposals: list[dict[str, Any]], participant_count: int) -> dict[str, Any]:
    if proposals:
        proposal = proposals[0]
        return {
            "kind": "proposal",
            "proposalId": proposal["proposalId"],
            "reason": proposal["reason"],
        }
    if participant_count < 2:
        return {
            "kind": "waiting",
            "proposalId": None,
            "reason": "A second consented participant is needed for a shared proposal.",
        }
    return {
        "kind": "observation",
        "proposalId": None,
        "reason": "Participants share the surface; no proposal is pending.",
    }


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PupilaViewError(f"{field_name} must be non-empty text")
    return value.strip()[:MAX_DISPLAY_TEXT]


def _limit(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PupilaViewError(f"{field_name} must be a non-negative integer")


__all__ = [
    "MAX_PARTICIPANTS",
    "MAX_PROPOSALS",
    "PUPILA_VIEW_SCHEMA_VERSION",
    "PupilaViewError",
    "project_pupila_view",
]
