"""PUPILA adapter: emergent, consented multi-participant overlay proposals."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from contracts import deterministic_id, normalize_context, sha256


class PupilaAdapter:
    """Connects states without sharing private signal content or taking action."""

    def __init__(self, state_ttl_ms: int = 15000) -> None:
        if isinstance(state_ttl_ms, bool) or not isinstance(state_ttl_ms, int) or state_ttl_ms < 1000:
            raise ValueError("state_ttl_ms must be an integer >= 1000")
        self.state_ttl_ms = state_ttl_ms
        self._states: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)

    @staticmethod
    def _state_key(context: dict[str, Any]) -> tuple[str, str, str]:
        return (context["sessionId"], context["roomId"], context["surfaceId"])

    def ingest(self, raw_context: dict[str, Any] | None, vizz_state: dict[str, Any]) -> dict[str, Any]:
        context = normalize_context(raw_context)
        if vizz_state.get("sessionId") != context["sessionId"] or vizz_state.get("roomId") != context["roomId"]:
            raise ValueError("VIZZ state and PUPILA context belong to different rooms")
        participant = str(vizz_state.get("participantRef") or "participant-local")
        observed_at = vizz_state.get("latestAtMs", 0)
        if isinstance(observed_at, bool) or not isinstance(observed_at, int) or observed_at < 0:
            raise ValueError("VIZZ latestAtMs must be a non-negative integer")
        if vizz_state.get("consent") is not True:
            return self.snapshot(context, now_ms=observed_at)
        self._states[self._state_key(context)][participant] = {
            "participantRef": participant,
            "policy": str(vizz_state.get("policy") or "quiet"),
            "activityScore": float(vizz_state.get("activityScore") or 0.0),
            "focusState": bool(vizz_state.get("focusState")),
            "sampleCount": int(vizz_state.get("sampleCount") or 0),
            "signalCoverage": list(vizz_state.get("signalCoverage", [])),
            "stateHash": str(vizz_state.get("stateHash") or ""),
            "observedAtMs": observed_at,
        }
        return self.snapshot(context, now_ms=observed_at)

    def snapshot(self, raw_context: dict[str, Any] | None, *, now_ms: int | None = None) -> dict[str, Any]:
        context = normalize_context(raw_context)
        state_bucket = self._states.get(self._state_key(context), {})
        if now_ms is None:
            now_ms = max((int(item.get("observedAtMs", 0)) for item in state_bucket.values()), default=0)
        if isinstance(now_ms, bool) or not isinstance(now_ms, int) or now_ms < 0:
            raise ValueError("now_ms must be a non-negative integer")
        cutoff = max(0, now_ms - self.state_ttl_ms)
        expired = [participant for participant, item in state_bucket.items()
                   if int(item.get("observedAtMs", 0)) < cutoff]
        for participant in expired:
            state_bucket.pop(participant, None)
        states = list(state_bucket.values())
        active = [item for item in states if item["activityScore"] > 0.18]
        blocked = [item for item in states if item["policy"] == "guide"]
        proposals: list[dict[str, Any]] = []
        if len(states) >= 2 and blocked and active:
            kind, reason = "peer-bridge", "one participant needs guidance while another progresses"
        elif len(states) >= 2 and len({item["policy"] for item in states}) > 1:
            kind, reason = "shared-checkpoint", "participants have different rhythms and may need a shared next step"
        elif len(states) >= 2:
            kind, reason = "co-presence", "more than one participant shares the work surface"
        else:
            kind, reason = None, None
        if kind:
            proposal = {
                "schemaVersion": 1,
                "proposalId": deterministic_id("pupila-proposal", {"sessionId": context["sessionId"], "roomId": context["roomId"], "surfaceId": context["surfaceId"], "kind": kind, "stateHashes": sorted(item["stateHash"] for item in states)}),
                "adapter": "pupila",
                "roomId": context["roomId"],
                "surfaceId": context["surfaceId"],
                "kind": kind,
                "reason": reason,
                "state": "proposed",
                "mode": "transparent-popup",
                "visibleTo": "consented-room-members",
                "requiresExplicitAcceptance": True,
                "reversible": True,
                "action": None,
            }
            proposals.append(proposal)
        return {
            "schemaVersion": 1,
            "adapter": "pupila",
            "sessionId": context["sessionId"],
            "roomId": context["roomId"],
            "surfaceId": context["surfaceId"],
            "stateTtlMs": self.state_ttl_ms,
            "expiredParticipantCount": len(expired),
            "participantCount": len(states),
            "participants": [
                {
                    "participantRef": item["participantRef"],
                    "policy": item["policy"],
                    "focusState": item["focusState"],
                    "sampleCount": item["sampleCount"],
                    "signalCoverage": item["signalCoverage"],
                }
                for item in sorted(states, key=lambda value: value["participantRef"])
            ],
            "proposals": proposals,
            "overlay": {"blocking": False, "clickThrough": True, "emergesFrom": "shared-state-delta"},
            "stateHash": sha256({"roomId": context["roomId"], "states": states, "proposals": proposals}),
            "meaning": "coordination-proposal; not a comprehension, attention or performance verdict",
        }
