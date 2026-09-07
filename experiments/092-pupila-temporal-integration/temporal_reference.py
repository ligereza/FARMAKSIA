"""Independent temporal oracle used by the integration tests."""

from __future__ import annotations

from typing import Iterable, Mapping, Any


def eligible_events(
    events: Iterable[Mapping[str, Any]],
    *,
    evaluation_ms: int,
    stale_after_ms: int,
    consent_epochs: Mapping[str, int],
) -> list[Mapping[str, Any]]:
    """Return events visible at a reference time without mutating state."""
    result = []
    for event in events:
        if bool(event.get("accepted")) is not True:
            continue
        at_ms = int(event["source_ms"])
        if at_ms > evaluation_ms or evaluation_ms - at_ms > stale_after_ms:
            continue
        if at_ms < int(event.get("active_from", 0)):
            continue
        if int(event.get("consent_epoch", 0)) != int(consent_epochs.get(str(event["peer_id"]), -1)):
            continue
        result.append(event)
    return sorted(result, key=lambda item: (int(item["source_ms"]), str(item["event_id"])))


__all__ = ["eligible_events"]
