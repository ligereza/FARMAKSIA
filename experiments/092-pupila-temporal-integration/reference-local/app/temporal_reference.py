"""Small, uncached temporal oracle used for differential tests."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping


def _event_ms(event: Mapping[str, Any]) -> int:
    value = str(event["source_timestamp"]).replace("Z", "+00:00")
    return int(datetime.fromisoformat(value).astimezone(timezone.utc).timestamp() * 1000)


def evaluate_temporal_reference(events: list[Mapping[str, Any]], consent: Mapping[str, tuple[bool, int]], context: Mapping[str, Any], evaluation_ms: int, stale_after_ms: int) -> dict[str, Any]:
    """Reference semantics: facts, consent epoch, context, and one instant."""
    eligible = []
    for event in events:
        peer = str(event["peer_id"])
        consent_row = consent.get(peer)
        age = evaluation_ms - _event_ms(event)
        if consent_row and consent_row[0] and age >= 0 and age <= stale_after_ms:
            eligible.append(dict(event))
    eligible.sort(key=lambda event: (str(event["peer_id"]), int(event["sequence"])))
    return {"context": dict(context), "eligibleEvents": eligible, "acceptedEventIds": [event["event_id"] for event in eligible]}
