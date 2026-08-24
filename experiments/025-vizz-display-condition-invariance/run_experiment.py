"""Verify display-condition invariance and query coverage for VIZZ."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
CASES = HERE / "cases.json"
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


def semantic_fingerprint(events: list[dict[str, Any]]) -> str:
    payload = json.dumps(events, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def load_documents() -> tuple[dict[str, Any], dict[str, Any]]:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    session = json.loads(SOURCE_SESSION.read_text(encoding="utf-8"))
    if cases.get("schema") != "farmaxia:vizz-display-condition-cases:0.1":
        raise ValueError("wrong display condition cases schema")
    return cases, session


def transition_summary(transition: dict[str, Any]) -> dict[str, Any]:
    return {
        "last_significant_improvement": transition["last_significant_improvement"],
        "repetition_entry": transition["repetition_entry"],
        "tail_event_ids": transition["tail_event_ids"],
    }


def evaluate_profile(
    profile: dict[str, Any],
    normalized: list[dict[str, Any]],
    baseline_fingerprint: str,
    expected_transition: dict[str, Any],
    required_ids: set[str],
    codeine: Any,
) -> dict[str, Any]:
    if profile["visible_event_ids"] == "all":
        visible = normalized
    else:
        wanted = set(profile["visible_event_ids"])
        visible = [event for event in normalized if event["event_id"] in wanted]
    visible_ids = {event["event_id"] for event in visible}
    required_coverage = required_ids.issubset(visible_ids)
    context_before_anchor_preserved = {event["event_id"] for event in visible}.issuperset({"c01", "c02", "c03"})
    transition = None
    decision_available = False
    if profile["representation"] != "field" and required_coverage:
        codeine.validate_events(visible)
        candidate = codeine.derive_transition(visible)
        transition = transition_summary(candidate)
        decision_available = transition == expected_transition
    classification = "available" if decision_available else "unavailable"
    presentation = {
        "condition": profile["condition"],
        "luminance": profile["luminance"],
        "contrast": profile["contrast"],
        "chromatic_shift": profile["chromatic_shift"],
        "text_scale": profile["text_scale"],
    }
    return {
        "id": profile["id"],
        "condition": profile["condition"],
        "representation": profile["representation"],
        "presentation": presentation,
        "visible_event_ids": [event["event_id"] for event in visible],
        "required_coverage": required_coverage,
        "context_before_anchor_preserved": context_before_anchor_preserved,
        "semantic_fingerprint": baseline_fingerprint if profile["visible_event_ids"] == "all" else semantic_fingerprint(visible),
        "classification": classification,
        "decision_available": decision_available,
        "transition": transition,
        "physiological_claim": False,
        "pharmacological_claim": False,
    }


def main() -> None:
    cases, session = load_documents()
    bridge = load_module(BRIDGE, "bridge_025")
    codeine = load_module(CODEINE, "codeine_025")
    normalized, dropped = bridge.normalize_events(session)
    codeine.validate_events(normalized)
    expected = transition_summary(codeine.derive_transition(normalized))
    baseline_fingerprint = semantic_fingerprint(normalized)
    required_ids = set(cases["required_query_event_ids"])
    results = [
        evaluate_profile(profile, normalized, baseline_fingerprint, expected, required_ids, codeine)
        for profile in cases["profiles"]
    ]
    by_id = {result["id"]: result for result in results}
    expected_classes = {profile["id"]: profile["expected_classification"] for profile in cases["profiles"]}
    all_expected = all(by_id[item]["classification"] == expected_classes[item] for item in expected_classes)
    full_fingerprints = {
        result["semantic_fingerprint"]
        for result in results
        if result["representation"] == "full"
    }
    counts = {name: sum(result["classification"] == name for result in results) for name in ("available", "unavailable")}
    print(
        json.dumps(
            {
                "experiment": "025-vizz-display-condition-invariance",
                "source_experiment": "022-vizz-codeine-long-bridge",
                "case_count": len(results),
                "classification_counts": counts,
                "all_expected_classifications": all_expected,
                "full_display_fingerprints": sorted(full_fingerprints),
                "full_display_invariant": full_fingerprints == {baseline_fingerprint},
                "dropped_vizz_fields": dropped,
                "required_query_event_ids": sorted(required_ids),
                "baseline_transition": expected,
                "cases": results,
                "human_data": False,
                "devices_started": False,
                "network_used": False,
                "raw_capture": False,
                "physiological_inference": False,
                "pharmacological_inference": False,
                "optical_prescription_applied": False,
                "scope_limit": "synthetic display metadata and query coverage; no comfort, circadian, pupillary, or drug claim",
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
