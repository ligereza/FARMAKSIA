"""VIZZ adapter: convert consented interaction signals into visual policy."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from contracts import clamp, deterministic_id, normalize_context, normalize_signal, sha256


class VizzAdapter:
    """A rendering heuristic, not a classifier of attention or mental state."""

    def __init__(self, window_ms: int = 5000, max_events: int = 128) -> None:
        self.window_ms = max(1000, int(window_ms))
        self.max_events = max(8, int(max_events))
        self._events: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)

    def ingest(self, raw_context: dict[str, Any] | None, raw_signal: dict[str, Any] | None) -> dict[str, Any]:
        context = normalize_context(raw_context)
        event = normalize_signal({**(raw_signal or {}), "sessionId": context["sessionId"], "roomId": context["roomId"], "surfaceId": context["surfaceId"]})
        key = (context["sessionId"], event["participantRef"], context["surfaceId"])
        if event["accepted"]:
            self._events[key].append(event)
            self._events[key] = self._events[key][-self.max_events :]
        return self.state(context, event["participantRef"])

    def state(self, raw_context: dict[str, Any] | None, participant_ref: str = "participant-local") -> dict[str, Any]:
        context = normalize_context(raw_context)
        key = (context["sessionId"], participant_ref, context["surfaceId"])
        events = self._events.get(key, [])
        latest_at = events[-1]["atMs"] if events else 0
        recent = [item for item in events if latest_at - item["atMs"] <= self.window_ms]
        kinds = Counter(item["kind"] for item in recent)
        focused = [item["value"]["focused"] for item in recent if item["kind"] == "focus"]
        focus_state = focused[-1] if focused else False
        gaze_quality = [item["value"]["quality"] for item in recent if item["kind"] == "gaze"]
        interaction_kinds = {"pointer", "keyboard", "focus", "gaze"}
        interaction_recent = [item for item in recent if item["kind"] in interaction_kinds]
        interaction_counts = Counter(item["kind"] for item in interaction_recent)
        activity = clamp(
            (len(interaction_recent) / 12.0) * 0.65
            + min(1.0, interaction_counts["keyboard"] / 4.0) * 0.2
            + min(1.0, interaction_counts["pointer"] / 8.0) * 0.15
        )
        coverage = sorted(kinds)
        if not recent:
            policy, reason = "quiet", "no-consented-signal"
        elif not focus_state:
            policy, reason = "anchor", "surface-not-confirmed-focused"
        elif activity < 0.18:
            policy, reason = "guide", "low-interaction-rate"
        elif activity > 0.78:
            policy, reason = "quiet", "high-interaction-rate-avoid-interference"
        else:
            policy, reason = "support", "active-surface-within-normal-signal-budget"
        return {
            "schemaVersion": 1,
            "adapter": "vizz",
            "stateId": deterministic_id("vizz-state", {"contextHash": context["contextHash"], "participantRef": participant_ref, "events": [item["eventId"] for item in recent]}),
            "contextHash": context["contextHash"],
            "sessionId": context["sessionId"],
            "roomId": context["roomId"],
            "surfaceId": context["surfaceId"],
            "participantRef": participant_ref,
            "windowMs": self.window_ms,
            "signalCoverage": coverage,
            "sampleCount": len(recent),
            "consent": bool(recent),
            "focusState": focus_state,
            "activityScore": round(activity, 6),
            "gazeQualityMean": round(sum(gaze_quality) / len(gaze_quality), 6) if gaze_quality else None,
            "policy": policy,
            "reason": reason,
            "overlay": {
                "mode": "transparent-popup",
                "blocking": False,
                "clickThrough": True,
                "visualIntensity": {"min": 0.12, "max": 0.42},
                "requiresExplicitAcceptance": True,
            },
            "meaning": "rendering-policy-heuristic; not a psychological or medical inference",
            "stateHash": sha256({"contextHash": context["contextHash"], "participantRef": participant_ref, "recent": [item["eventId"] for item in recent], "policy": policy}),
        }
