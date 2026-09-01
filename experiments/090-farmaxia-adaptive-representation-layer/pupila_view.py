"""Bounded read-only projection for the PUPILA shared surface."""

from __future__ import annotations

import json
from typing import Any, Mapping


PUPILA_VIEW_SCHEMA_VERSION = 1
MAX_PARTICIPANTS = 16
MAX_PROPOSALS = 8
MAX_DISPLAY_TEXT = 240
PUPILA_DIFF_FIELDS = (
    "participantCount",
    "shownParticipantCount",
    "proposalCount",
    "shownProposalCount",
    "participants",
    "proposals",
    "nextAttention",
    "safety",
)
MAX_DIFF_CHANGES = len(PUPILA_DIFF_FIELDS)
_VIEW_FIELDS = {
    "contractType",
    "schemaVersion",
    "surface",
    "mode",
    "sessionId",
    "roomId",
    "surfaceId",
    "participantCount",
    "shownParticipantCount",
    "proposalCount",
    "shownProposalCount",
    "participants",
    "proposals",
    "nextAttention",
    "safety",
}
_NEXT_ATTENTION_FIELDS = {"kind", "proposalId", "reason"}
_SAFETY_FIELDS = {
    "proposalOnly",
    "requiresExplicitAcceptance",
    "reversible",
    "blocking",
    "clickThrough",
    "rawSignalsIncluded",
    "actionsIncluded",
}
_KIND_ORDER = {"peer-bridge": 0, "shared-checkpoint": 1, "co-presence": 2}


class PupilaViewError(ValueError):
    """Raised when a PUPILA view cannot be represented safely."""


def diff_pupila_view(
    previous_view: Mapping[str, Any],
    current_view: Mapping[str, Any],
    *,
    max_changes: int = MAX_DIFF_CHANGES,
) -> list[dict[str, Any]]:
    """Return bounded, deterministic changes between two projected views."""

    _limit(max_changes, "max_changes")
    previous = _validated_view(previous_view, "previous_view")
    current = _validated_view(current_view, "current_view")
    changes: list[dict[str, Any]] = []
    for field_name in PUPILA_DIFF_FIELDS:
        before = previous[field_name]
        after = current[field_name]
        if before != after:
            changes.append(
                {
                    "field": field_name,
                    "before": _json_copy(before),
                    "after": _json_copy(after),
                }
            )
    return changes[:max_changes]


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
    sample_count = value.get("sampleCount", 0)
    if isinstance(sample_count, bool) or not isinstance(sample_count, int) or sample_count < 0:
        raise PupilaViewError("participant.sampleCount must be a non-negative integer")
    coverage = value.get("signalCoverage", [])
    if not isinstance(coverage, list) or any(not isinstance(item, str) for item in coverage):
        raise PupilaViewError("participant.signalCoverage must be a list of text")
    safe_coverage = sorted({item.strip()[:40] for item in coverage if item.strip()})[:8]
    return {
        "participantRef": _text(value.get("participantRef"), "participantRef"),
        "policy": _text(value.get("policy"), "policy"),
        "focusState": value.get("focusState") is True,
        "interaction": {
            "sampleCount": min(sample_count, 128),
            "signalCoverage": safe_coverage,
        },
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


def _validated_view(value: Mapping[str, Any], field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise PupilaViewError(f"{field_name} must be an object")
    if set(value) != _VIEW_FIELDS:
        raise PupilaViewError(f"{field_name} contains unsupported or missing fields")
    if value["contractType"] != "PupilaOverlayView":
        raise PupilaViewError(f"{field_name}.contractType is invalid")
    if value["schemaVersion"] != PUPILA_VIEW_SCHEMA_VERSION:
        raise PupilaViewError(f"{field_name}.schemaVersion is invalid")
    if value["surface"] != "PUPILA" or value["mode"] != "read_only":
        raise PupilaViewError(f"{field_name} is not a read-only PUPILA view")
    for list_field in ("participants", "proposals"):
        if not isinstance(value[list_field], list):
            raise PupilaViewError(f"{field_name}.{list_field} must be a list")
    next_attention = value["nextAttention"]
    if not isinstance(next_attention, Mapping) or set(next_attention) != _NEXT_ATTENTION_FIELDS:
        raise PupilaViewError(f"{field_name}.nextAttention is invalid")
    safety = value["safety"]
    if not isinstance(safety, Mapping) or set(safety) != _SAFETY_FIELDS:
        raise PupilaViewError(f"{field_name}.safety is invalid")
    if (
        safety["proposalOnly"] is not True
        or safety["requiresExplicitAcceptance"] is not True
        or safety["reversible"] is not True
        or safety["blocking"] is not False
        or safety["clickThrough"] is not True
        or safety["rawSignalsIncluded"] is not False
        or safety["actionsIncluded"] is not False
    ):
        raise PupilaViewError(f"{field_name}.safety violates the read-only boundary")
    return _json_copy(dict(value))


def _json_copy(value: Any) -> Any:
    try:
        serialized = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise PupilaViewError("view values must be JSON serializable") from exc
    return json.loads(serialized)


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PupilaViewError(f"{field_name} must be non-empty text")
    return value.strip()[:MAX_DISPLAY_TEXT]


def _limit(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PupilaViewError(f"{field_name} must be a non-negative integer")


__all__ = [
    "MAX_DIFF_CHANGES",
    "MAX_PARTICIPANTS",
    "MAX_PROPOSALS",
    "PUPILA_DIFF_FIELDS",
    "PUPILA_VIEW_SCHEMA_VERSION",
    "PupilaViewError",
    "diff_pupila_view",
    "project_pupila_view",
]
