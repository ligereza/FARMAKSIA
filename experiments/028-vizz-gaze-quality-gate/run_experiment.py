"""Apply a synthetic consent, provenance, and gaze-quality gate for VIZZ."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
CASES = HERE / "cases.json"
TOOLS = HERE / "tool_candidates.json"
SOURCE_SESSION = ROOT / "experiments" / "022-vizz-codeine-long-bridge" / "session.json"
BRIDGE = ROOT / "experiments" / "020-vizz-codeine-event-bridge" / "run_experiment.py"
CODEINE = ROOT / "experiments" / "016-codeine-session-state" / "run_experiment.py"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_documents() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    tools = json.loads(TOOLS.read_text(encoding="utf-8"))
    session = json.loads(SOURCE_SESSION.read_text(encoding="utf-8"))
    if cases.get("schema") != "farmaxia:vizz-gaze-quality-cases:0.1":
        raise ValueError("wrong gaze quality cases schema")
    if tools.get("schema") != "farmaxia:vizz-gaze-tool-candidates:0.1":
        raise ValueError("wrong gaze tool candidates schema")
    return cases, tools, session


def validate_tool_catalog(tools: dict[str, Any]) -> None:
    candidates = tools.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("tool catalog is empty")
    ids = [candidate.get("id") for candidate in candidates]
    if any(not isinstance(item, str) for item in ids) or len(set(ids)) != len(ids):
        raise ValueError("tool candidate ids are invalid or duplicated")
    policy = tools.get("policy", {})
    required_policy = {
        "require_consent",
        "require_local_processing",
        "forbid_network_transport",
        "max_latency_ms",
        "max_calibration_error_px",
        "min_coverage_ratio",
        "require_stable_head_pose",
    }
    if set(policy) != required_policy:
        raise ValueError("tool policy fields are incomplete")
    if not all(isinstance(policy[key], bool) for key in ("require_consent", "require_local_processing", "forbid_network_transport", "require_stable_head_pose")):
        raise ValueError("tool boolean policy is invalid")
    if not all(isinstance(policy[key], (int, float)) for key in ("max_latency_ms", "max_calibration_error_px", "min_coverage_ratio")):
        raise ValueError("tool numeric policy is invalid")


def transition_summary(transition: dict[str, Any]) -> dict[str, Any]:
    return {
        "last_significant_improvement": transition["last_significant_improvement"],
        "repetition_entry": transition["repetition_entry"],
        "tail_event_ids": transition["tail_event_ids"],
    }


def validate_profile_shape(profile: dict[str, Any]) -> None:
    booleans = ("consent_granted", "processing_local", "network_transport_used", "calibration_valid", "head_pose_stable")
    if any(type(profile.get(key)) is not bool for key in booleans):
        raise ValueError("gaze profile boolean field is invalid")
    if not isinstance(profile.get("candidate"), str):
        raise ValueError("gaze candidate is invalid")
    for key in ("latency_ms", "coverage_ratio"):
        if not isinstance(profile.get(key), (int, float)) or isinstance(profile.get(key), bool):
            raise ValueError(f"gaze profile {key} is invalid")
    calibration_error = profile.get("calibration_error_px")
    if calibration_error is not None and (not isinstance(calibration_error, (int, float)) or isinstance(calibration_error, bool)):
        raise ValueError("calibration error is invalid")


def evaluate_profile(profile: dict[str, Any], candidate_map: dict[str, dict[str, Any]], policy: dict[str, Any]) -> dict[str, Any]:
    status = "available"
    reason = None
    adaptation_allowed = False
    try:
        validate_profile_shape(profile)
        candidate = candidate_map.get(profile["candidate"])
        if candidate is None:
            raise ValueError("unknown tool candidate")
        if policy["require_consent"] and not profile["consent_granted"]:
            status, reason = "blocked", "consent_required"
        elif policy["require_local_processing"] and not profile["processing_local"]:
            status, reason = "blocked", "local_processing_required"
        elif policy["forbid_network_transport"] and profile["network_transport_used"]:
            status, reason = "blocked", "network_transport_forbidden"
        elif not profile["calibration_valid"] or profile["calibration_error_px"] is None:
            status, reason = "unavailable", "calibration_missing_or_invalid"
        elif profile["calibration_error_px"] > policy["max_calibration_error_px"]:
            status, reason = "unavailable", "calibration_error_above_fixture_limit"
        elif profile["latency_ms"] > policy["max_latency_ms"]:
            status, reason = "unavailable", "latency_above_fixture_limit"
        elif profile["coverage_ratio"] < policy["min_coverage_ratio"]:
            status, reason = "unavailable", "coverage_below_required"
        elif policy["require_stable_head_pose"] and not profile["head_pose_stable"]:
            status, reason = "unavailable", "head_pose_unstable"
        else:
            adaptation_allowed = True
    except ValueError as exc:
        status, reason = "rejected", str(exc)
    return {
        "id": profile["id"],
        "candidate": profile.get("candidate"),
        "evidence_status": status,
        "reason": reason,
        "adaptation_allowed": adaptation_allowed,
        "human_data": False,
        "raw_capture": False,
        "physiological_inference": False,
        "pharmacological_inference": False,
        "neurochemical_inference": False,
    }


def main() -> None:
    cases, tools, session = load_documents()
    validate_tool_catalog(tools)
    bridge = load_module(BRIDGE, "bridge_028")
    codeine = load_module(CODEINE, "codeine_028")
    normalized, dropped = bridge.normalize_events(session)
    codeine.validate_events(normalized)
    baseline = transition_summary(codeine.derive_transition(normalized))
    candidate_map = {candidate["id"]: candidate for candidate in tools["candidates"]}
    results = [evaluate_profile(profile, candidate_map, tools["policy"]) for profile in cases["profiles"]]
    by_id = {result["id"]: result for result in results}
    expected_status = {profile["id"]: profile["expected_classification"] for profile in cases["profiles"]}
    expected_adaptation = {profile["id"]: profile["expected_adaptation_allowed"] for profile in cases["profiles"]}
    all_expected = all(
        by_id[item]["evidence_status"] == expected_status[item]
        and by_id[item]["adaptation_allowed"] == expected_adaptation[item]
        for item in expected_status
    )
    names = ("available", "blocked", "unavailable", "rejected")
    counts = {name: sum(result["evidence_status"] == name for result in results) for name in names}
    print(
        json.dumps(
            {
                "experiment": "028-vizz-gaze-quality-gate",
                "source_experiment": "022-vizz-codeine-long-bridge",
                "case_count": len(results),
                "evidence_status_counts": counts,
                "all_expected_classifications": all_expected,
                "baseline_transition": baseline,
                "dropped_vizz_fields": dropped,
                "policy": tools["policy"],
                "tool_dispositions": {candidate["id"]: candidate["adoption_status"] for candidate in tools["candidates"]},
                "cases": results,
                "human_data": False,
                "devices_started": False,
                "network_used": False,
                "raw_capture": False,
                "physiological_inference": False,
                "pharmacological_inference": False,
                "neurochemical_inference": False,
                "scope_limit": "synthetic consent, provenance, and gaze-quality gate; no human visual, ocular, circadian, or drug claim",
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
