"""Offline guard for keeping product and host responsibilities separate."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class BoundaryRule:
    """Top-level markers that define and reject a repository surface."""

    required: tuple[str, ...]
    forbidden: tuple[str, ...]


BOUNDARY_RULES: dict[str, BoundaryRule] = {
    "farmaxia_vizz_pupila": BoundaryRule(
        required=(
            "canonical_event_bridge.py",
            "pupila_adapter.py",
            "pupila_view.py",
            "vizz_adapter.py",
        ),
        forbidden=("adobe", "resolume", "XIO_LAYER"),
    ),
    "vj_lucida": BoundaryRule(
        required=("lucida",),
        forbidden=("adobe", "resolume", "XIO_LAYER", "multi"),
    ),
    "lucida_adobe": BoundaryRule(
        required=("adobe",),
        forbidden=("resolume", "XIO_LAYER", "multi"),
    ),
    "lucida_resolume": BoundaryRule(
        required=("lucida", "resolume", "adapters"),
        forbidden=("adobe", "XIO_LAYER", "multi"),
    ),
    "lucida_multi": BoundaryRule(
        required=("XIO_LAYER", "multi"),
        forbidden=("adobe", "resolume"),
    ),
    "xio": BoundaryRule(
        required=("XIO_LAYER",),
        forbidden=("lucida", "adobe", "resolume", "multi"),
    ),
}


class BoundaryMatrixError(ValueError):
    """Raised when a role is unknown or a root violates its boundary."""


def inspect_root(role: str, root: str | Path) -> dict[str, Any]:
    """Inspect only direct children of one explicit repository root."""

    if role not in BOUNDARY_RULES:
        raise BoundaryMatrixError(f"unknown boundary role: {role}")
    resolved = Path(root).expanduser().resolve()
    if not resolved.is_dir():
        raise BoundaryMatrixError(f"boundary root is not a directory: {resolved}")
    children = {item.name for item in resolved.iterdir()}
    rule = BOUNDARY_RULES[role]
    missing = sorted(set(rule.required) - children)
    forbidden = sorted(set(rule.forbidden) & children)
    return {
        "role": role,
        "root": str(resolved),
        "required": list(rule.required),
        "missing": missing,
        "forbidden": forbidden,
        "status": "PASS" if not missing and not forbidden else "FAIL",
    }


def inspect_matrix(entries: Mapping[str, str | Path]) -> dict[str, Any]:
    """Inspect a named set of roots without opening a network or host app."""

    if not entries:
        raise BoundaryMatrixError("at least one boundary root is required")
    if len(entries) != len(set(entries)):
        raise BoundaryMatrixError("boundary roles must be unique")
    checks = [inspect_root(role, root) for role, root in sorted(entries.items())]
    failures = [check for check in checks if check["status"] != "PASS"]
    return {
        "contractType": "FarmaxiaBoundaryMatrixReport",
        "schemaVersion": 1,
        "checks": checks,
        "passedCount": len(checks) - len(failures),
        "failedCount": len(failures),
        "status": "PASS" if not failures else "FAIL",
        "networkOpened": False,
        "guiOpened": False,
        "hostActionsExecuted": False,
    }


__all__ = [
    "BOUNDARY_RULES",
    "BoundaryMatrixError",
    "BoundaryRule",
    "inspect_matrix",
    "inspect_root",
]
