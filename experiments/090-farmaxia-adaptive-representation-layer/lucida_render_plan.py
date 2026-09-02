"""Build a bounded visual plan for the future transparent LUCIDA surface."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


VIEW_FIELDS = {
    "contract_type",
    "schema_version",
    "surface",
    "mode",
    "session_id",
    "phase",
    "status",
    "overlay_status",
    "capabilities",
    "pending_proposals",
    "unknowns",
    "next_attention",
    "safety",
}


class LucidaRenderPlanError(ValueError):
    """Raised when a view cannot be represented safely."""


def build_lucida_render_plan(view: Mapping[str, Any]) -> dict[str, Any]:
    """Convert a redacted LUCIDA view into generic visual elements.

    This function does not render, open a window, capture input, or describe
    host-specific actions. It only selects bounded message keys, tones and
    safe references for a future transparent surface.
    """

    validated = _validate_view(view)
    proposals = validated["pending_proposals"]
    capabilities = validated["capabilities"]
    elements: list[dict[str, Any]] = [
        _element(
            "status",
            validated["status"],
            {
                "messageKey": f"overlay.status.{validated['status']}",
                "tone": "accent" if validated["overlay_status"] == "proposal" else "neutral",
            },
        )
    ]
    for capability in capabilities[:4]:
        elements.append(
            _element(
                "capability",
                capability["capability"],
                {
                    "messageKey": "capability.observed",
                    "capability": capability["capability"],
                    "observedCount": capability["observed_count"],
                    "expectedResultCount": capability["expected_result_count"],
                    "tone": "muted",
                },
            )
        )
    for proposal in proposals[:3]:
        elements.append(
            _element(
                "proposal",
                proposal["proposal_id"],
                {
                    "messageKey": "proposal.requires_explicit_acceptance",
                    "proposalId": proposal["proposal_id"],
                    "tone": "attention",
                    "requiresExplicitAcceptance": True,
                    "reversible": True,
                },
            )
        )
    if not proposals and validated["next_attention"]["kind"] == "waiting":
        elements.append(
            _element(
                "attention",
                validated["next_attention"]["id"],
                {
                    "messageKey": "overlay.waiting",
                    "tone": "muted",
                },
            )
        )

    intensity = "high" if proposals else "medium" if capabilities else "low"
    plan = {
        "contractType": "LucidaRenderPlan",
        "schemaVersion": 1,
        "surface": "LUCIDA",
        "mode": "read_only",
        "sessionId": validated["session_id"],
        "phase": validated["phase"],
        "viewDigest": _digest(validated),
        "transparent": True,
        "clickThrough": True,
        "blocking": False,
        "intensity": intensity,
        "elements": elements[:8],
        "safety": {
            "proposalOnly": True,
            "automaticActions": False,
            "externalSideEffects": False,
            "rawPayloadIncluded": False,
        },
    }
    _reject_unsafe_plan(plan)
    return plan


def _validate_view(view: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(view, Mapping):
        raise LucidaRenderPlanError("view must be a mapping")
    if set(view) != VIEW_FIELDS:
        raise LucidaRenderPlanError("view contains unsupported or missing fields")
    if view.get("contract_type") != "LucidaOverlayView":
        raise LucidaRenderPlanError("view contract_type is invalid")
    if view.get("schema_version") != "0.1":
        raise LucidaRenderPlanError("view schema_version is invalid")
    if view.get("surface") != "LUCIDA" or view.get("mode") != "read_only":
        raise LucidaRenderPlanError("view surface or mode is invalid")
    for field in ("session_id", "phase", "status", "overlay_status"):
        if not isinstance(view.get(field), str) or not view[field].strip():
            raise LucidaRenderPlanError(f"{field} must be non-empty text")
    safety = view["safety"]
    if not isinstance(safety, Mapping):
        raise LucidaRenderPlanError("view safety must be a mapping")
    if safety.get("proposal_only") is not True:
        raise LucidaRenderPlanError("view must remain proposal_only")
    if safety.get("automatic_actions") is not False:
        raise LucidaRenderPlanError("view must reject automatic actions")
    if safety.get("external_side_effects") is not False:
        raise LucidaRenderPlanError("view must reject external side effects")
    capabilities = view["capabilities"]
    proposals = view["pending_proposals"]
    unknowns = view["unknowns"]
    attention = view["next_attention"]
    if not isinstance(capabilities, list) or not isinstance(proposals, list):
        raise LucidaRenderPlanError("capabilities and pending_proposals must be lists")
    if not isinstance(unknowns, list) or not isinstance(attention, Mapping):
        raise LucidaRenderPlanError("unknowns and next_attention are invalid")
    for capability in capabilities:
        if not isinstance(capability, Mapping):
            raise LucidaRenderPlanError("capability must be a mapping")
        required = {"capability", "state", "observed_count", "expected_result_count", "unknowns"}
        if set(capability) != required:
            raise LucidaRenderPlanError("capability contains unsupported or missing fields")
        if not isinstance(capability["capability"], str):
            raise LucidaRenderPlanError("capability name must be text")
        if not isinstance(capability["observed_count"], int) or capability["observed_count"] < 0:
            raise LucidaRenderPlanError("observed_count must be a non-negative integer")
        if not isinstance(capability["expected_result_count"], int) or capability["expected_result_count"] < 0:
            raise LucidaRenderPlanError("expected_result_count must be a non-negative integer")
    for proposal in proposals:
        if not isinstance(proposal, Mapping):
            raise LucidaRenderPlanError("proposal must be a mapping")
        required = {
            "proposal_id",
            "event_id",
            "phase",
            "operation",
            "reason",
            "risk",
            "requires_explicit_approval",
            "reversible",
            "execution_mode",
        }
        if set(proposal) != required:
            raise LucidaRenderPlanError("proposal contains unsupported or missing fields")
        if proposal["requires_explicit_approval"] is not True or proposal["reversible"] is not True:
            raise LucidaRenderPlanError("proposal must remain explicit and reversible")
        if proposal["execution_mode"] != "proposal_only":
            raise LucidaRenderPlanError("proposal execution mode is invalid")
    return dict(view)


def _element(kind: str, identity: str, body: Mapping[str, Any]) -> dict[str, Any]:
    element_id = hashlib.sha256(f"{kind}:{identity}".encode("utf-8")).hexdigest()[:16]
    return {"elementId": f"element-{element_id}", "kind": kind, **dict(body)}


def _digest(view: Mapping[str, Any]) -> str:
    canonical = json.dumps(view, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _reject_unsafe_plan(plan: Mapping[str, Any]) -> None:
    forbidden_keys = {"payload", "command", "shell", "action", "coordinates"}

    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if str(key).lower() in forbidden_keys:
                    raise LucidaRenderPlanError(
                        f"unsafe field leaked into render plan: {key}"
                    )
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(plan)


__all__ = ["LucidaRenderPlanError", "build_lucida_render_plan"]
