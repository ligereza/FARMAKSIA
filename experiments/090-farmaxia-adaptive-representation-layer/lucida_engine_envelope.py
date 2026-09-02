"""Convert redacted FARMAXIA 090 states into LUCIDA engine values."""

from __future__ import annotations

from typing import Any, Mapping


class LucidaEnvelopeError(ValueError):
    """Raised when a source state cannot cross the LUCIDA boundary."""


def _text(value: Any, field_name: str, maximum: int = 280) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LucidaEnvelopeError(f"{field_name} must be non-empty text")
    result = value.strip()
    if len(result) > maximum:
        raise LucidaEnvelopeError(f"{field_name} exceeds the text bound")
    try:
        result.encode("ascii")
    except UnicodeEncodeError as error:
        raise LucidaEnvelopeError(f"{field_name} must contain ASCII only") from error
    return result


def _positive_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise LucidaEnvelopeError(f"{field_name} must be a positive integer")
    return value


def _mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise LucidaEnvelopeError(f"{field_name} must be a mapping")
    return value


def vizz_state_to_lucida_value(
    state: Mapping[str, Any],
    *,
    event_id: str,
    timestamp: str,
    sequence: int,
) -> dict[str, Any]:
    """Project one VIZZ state without copying its source payload."""

    source = _mapping(state, "vizz_state")
    session_id = _text(source.get("sessionId"), "vizz_state.sessionId", 120)
    if not isinstance(source.get("focusState"), bool):
        raise LucidaEnvelopeError("vizz_state.focusState must be boolean")
    return {
        "session_id": session_id,
        "event_id": _text(event_id, "event_id", 120),
        "timestamp": _text(timestamp, "timestamp", 80),
        "sequence": _positive_int(sequence, "sequence"),
        "event_type": "focus.state",
        "summary": {"focused": source["focusState"]},
    }


def pupila_room_to_lucida_value(
    room: Mapping[str, Any],
    *,
    event_id: str,
    timestamp: str,
    sequence: int,
) -> dict[str, Any]:
    """Project one PUPILA room proposal without forwarding room payloads."""

    source = _mapping(room, "pupila_room")
    session_id = _text(source.get("sessionId"), "pupila_room.sessionId", 120)
    participant_count = source.get("participantCount")
    if isinstance(participant_count, bool) or not isinstance(participant_count, int) or not 0 <= participant_count <= 64:
        raise LucidaEnvelopeError("pupila_room.participantCount is outside its bound")
    proposals = source.get("proposals")
    if not isinstance(proposals, list) or len(proposals) != 1:
        raise LucidaEnvelopeError("pupila_room must contain exactly one proposal")
    proposal = _mapping(proposals[0], "pupila_room.proposals[0]")
    if "action" in proposal and proposal["action"] is not None:
        raise LucidaEnvelopeError("pupila proposal action must be absent")
    kind = _text(proposal.get("kind"), "proposal.kind", 80)
    return {
        "session_id": session_id,
        "event_id": _text(event_id, "event_id", 120),
        "timestamp": _text(timestamp, "timestamp", 80),
        "sequence": _positive_int(sequence, "sequence"),
        "event_type": "coordination.proposal",
        "summary": {
            "participant_count": participant_count,
            "proposal_kind": kind,
            "proposal_state": _text(proposal.get("state"), "proposal.state", 40),
        },
        "proposal": {
            "proposal_id": _text(proposal.get("proposalId"), "proposal.proposalId", 120),
            "kind": kind.replace("-", "_"),
            "title": "PUPILA coordination proposal",
            "body": _text(proposal.get("reason"), "proposal.reason"),
            "priority": 60,
            "ttl_ms": 3000,
            "requires_confirmation": True,
            "reversible": True,
        },
    }


__all__ = [
    "LucidaEnvelopeError",
    "pupila_room_to_lucida_value",
    "vizz_state_to_lucida_value",
]
