"""Correlate consented input observations with native state deltas, never intent."""

from __future__ import annotations

import hashlib
import math
from typing import Any


def digest(value: Any, salt: bytes) -> str:
    """Keep content-derived identity in memory; never emit the digest."""
    encoded = repr(value).encode("utf-8", errors="replace")
    return hashlib.sha256(salt + encoded).hexdigest()


def snapshot_excel(app: Any, salt: bytes, target: Any | None = None) -> dict[str, Any]:
    """Read a content-minimized Excel state snapshot without changing the app."""
    workbook_count = int(app.Workbooks.Count)
    snapshot: dict[str, Any] = {
        "workbook_count": workbook_count,
        "worksheet_count": 0,
        "active_cell_signature": None,
        "value_signature": None,
        "formula_signature": None,
        "nonempty_count": None,
        "formula_count": None,
    }
    if workbook_count <= 0:
        return snapshot
    try:
        active_workbook = app.ActiveWorkbook
        snapshot["worksheet_count"] = int(active_workbook.Worksheets.Count)
    except Exception:
        pass
    try:
        active_cell = app.ActiveCell
        snapshot["active_cell_signature"] = digest(active_cell.Address(False, False), salt)
        snapshot["value_signature"] = digest(active_cell.Value, salt)
        snapshot["formula_signature"] = digest(active_cell.Formula, salt)
    except Exception:
        pass
    if target is not None:
        try:
            snapshot["nonempty_count"] = int(app.WorksheetFunction.CountA(target))
            formula_count = 0
            for cell in target:
                if str(cell.Formula).startswith("="):
                    formula_count += 1
            snapshot["formula_count"] = formula_count
        except Exception:
            pass
    return snapshot


def classify_delta(
    before: dict[str, Any],
    after: dict[str, Any],
    reversion_target: dict[str, Any] | None = None,
) -> str:
    if reversion_target is not None and before != reversion_target and after == reversion_target:
        return "revert"
    if before.get("workbook_count", 0) == 0 and after.get("workbook_count", 0) > 0:
        return "create_entity"
    if before.get("workbook_count", 0) > 0 and after.get("workbook_count", 0) == 0:
        return "revert"
    if before.get("nonempty_count") != after.get("nonempty_count"):
        return "modify_property"
    if before.get("formula_count") != after.get("formula_count"):
        return "modify_property"
    if before.get("formula_signature") != after.get("formula_signature") or before.get("value_signature") != after.get("value_signature"):
        return "modify_property"
    if before.get("active_cell_signature") != after.get("active_cell_signature"):
        return "select_entity"
    if before.get("worksheet_count") != after.get("worksheet_count"):
        return "create_entity"
    return "no_change"


def correlate(
    input_events: list[dict[str, Any]],
    delta_events: list[dict[str, Any]],
    window_ms: float = 750.0,
) -> list[dict[str, Any]]:
    """Return associations as candidates; multiple matches remain ambiguous."""
    if window_ms <= 0.0 or not math.isfinite(window_ms):
        raise ValueError("window_ms must be finite and positive")
    associations: list[dict[str, Any]] = []
    for delta in delta_events:
        delta_time = float(delta["t_monotonic"])
        candidates = [
            event
            for event in input_events
            if event.get("application_class") == delta.get("application_class")
            and 0.0 <= (delta_time - float(event["t_monotonic"])) * 1000.0 <= window_ms
        ]
        if len(candidates) == 1:
            status = "candidate_association"
            lag_ms = (delta_time - float(candidates[0]["t_monotonic"])) * 1000.0
        elif len(candidates) > 1:
            status = "ambiguous_association"
            lag_ms = None
        else:
            status = "unassociated_native_delta"
            lag_ms = None
        associations.append(
            {
                "delta_kind": delta["delta_kind"],
                "application_class": delta.get("application_class"),
                "status": status,
                "lag_ms": lag_ms,
                "intent_claimed": False,
            }
        )
    return associations
