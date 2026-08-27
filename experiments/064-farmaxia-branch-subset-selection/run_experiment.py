"""Select a small semantic branch subset under an explicit display budget."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def validate_fixture(fixture: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    contract = fixture.get("source_contract", {})
    contract_path = (HERE / contract.get("path", "")).resolve()
    if not contract_path.is_file():
        blockers.append("source_contract_missing")
    else:
        source = load_json(contract_path)
        if len(source.get("queries", [])) != contract.get("required_query_count"):
            blockers.append("source_query_contract_changed")
        if contract.get("required_mode") != "query_relative_preservation":
            blockers.append("source_contract_mode_invalid")
    needs = fixture.get("semantic_needs", [])
    need_ids = [need.get("id") for need in needs]
    if not needs or len(need_ids) != len(set(need_ids)):
        blockers.append("semantic_needs_not_unique")
    if any(need.get("weight", 0) <= 0 for need in needs):
        blockers.append("semantic_need_weight_invalid")
    policy = fixture.get("selection_policy", {})
    if policy.get("method") != "facility_location_greedy":
        blockers.append("selection_method_not_facility_location")
    if policy.get("mmr_role") != "diagnostic_only":
        blockers.append("mmr_promoted_to_selection_authority")
    if policy.get("max_visible_branches", 0) < 2 or policy.get("display_budget", 0) <= 0 or policy.get("display_cost_penalty", -1) < 0 or policy.get("min_marginal_gain", -1) < 0:
        blockers.append("selection_policy_bounds_invalid")
    candidates = fixture.get("candidates", [])
    candidate_ids = [candidate.get("id") for candidate in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        blockers.append("candidate_ids_not_unique")
    if policy.get("anchor_plan_id") not in set(candidate_ids):
        blockers.append("anchor_plan_missing")
    valid_needs = set(need_ids)
    for candidate in candidates:
        if candidate.get("display_cost", 0) <= 0:
            blockers.append(f"candidate_cost_invalid:{candidate.get('id')}")
        if not candidate.get("coverage"):
            blockers.append(f"candidate_coverage_missing:{candidate.get('id')}")
        if not set(candidate.get("coverage", [])).issubset(valid_needs):
            blockers.append(f"candidate_covers_unknown_need:{candidate.get('id')}")
        if candidate.get("preserves_critical_queries") is not True:
            blockers.append(f"candidate_query_contract_missing:{candidate.get('id')}")
    return blockers


def objective(selected: list[dict[str, Any]], need_weights: dict[str, float], penalty: float) -> float:
    covered = set().union(*(set(candidate["coverage"]) for candidate in selected)) if selected else set()
    gain = sum(need_weights[need] for need in covered)
    cost = sum(candidate["display_cost"] for candidate in selected)
    return gain - penalty * cost


def facility_location_greedy(fixture: dict[str, Any]) -> dict[str, Any]:
    policy = fixture["selection_policy"]
    weights = {need["id"]: need["weight"] for need in fixture["semantic_needs"]}
    candidates = fixture["candidates"]
    by_id = {candidate["id"]: candidate for candidate in candidates}
    selected = [by_id[policy["anchor_plan_id"]]]
    remaining = [candidate for candidate in candidates if candidate["id"] != policy["anchor_plan_id"]]
    steps = [{"selected": policy["anchor_plan_id"], "marginal_gain": None, "reason": "required_anchor"}]
    while len(selected) < policy["max_visible_branches"]:
        feasible = [candidate for candidate in remaining if sum(item["display_cost"] for item in selected) + candidate["display_cost"] <= policy["display_budget"] + 1e-9]
        if not feasible:
            break
        scored = []
        current_value = objective(selected, weights, policy["display_cost_penalty"])
        for candidate in feasible:
            marginal = objective(selected + [candidate], weights, policy["display_cost_penalty"]) - current_value
            scored.append((marginal, candidate["id"], candidate))
        marginal, _, best = sorted(scored, key=lambda item: (-item[0], item[1]))[0]
        if marginal <= policy["min_marginal_gain"]:
            break
        selected.append(best)
        remaining = [candidate for candidate in remaining if candidate["id"] != best["id"]]
        steps.append({"selected": best["id"], "marginal_gain": marginal, "reason": "positive_marginal_gain"})
    next_candidates = []
    current_value = objective(selected, weights, policy["display_cost_penalty"])
    for candidate in remaining:
        if sum(item["display_cost"] for item in selected) + candidate["display_cost"] <= policy["display_budget"] + 1e-9:
            next_candidates.append({"id": candidate["id"], "marginal_gain": objective(selected + [candidate], weights, policy["display_cost_penalty"]) - current_value})
    next_best = max(next_candidates, key=lambda item: (item["marginal_gain"], item["id"])) if next_candidates else None
    pairwise = []
    for index, left in enumerate(selected):
        for right in selected[index + 1:]:
            pairwise.append(jaccard(set(left["coverage"]), set(right["coverage"])))
    mmr_selected = [by_id[policy["anchor_plan_id"]]]
    mmr_remaining = [candidate for candidate in candidates if candidate["id"] != policy["anchor_plan_id"]]
    while mmr_remaining:
        scored = []
        for candidate in mmr_remaining:
            relevance = sum(weights[item] for item in candidate["coverage"]) / sum(weights.values())
            redundancy = max(jaccard(set(candidate["coverage"]), set(item["coverage"])) for item in mmr_selected)
            scored.append((0.7 * relevance - 0.3 * redundancy, candidate["id"]))
        _, best_id = sorted(scored, key=lambda item: (-item[0], item[1]))[0]
        mmr_selected.append(by_id[best_id])
        mmr_remaining = [candidate for candidate in mmr_remaining if candidate["id"] != best_id]
    return {
        "selected_ids": [candidate["id"] for candidate in selected],
        "unselected_recoverable_ids": [candidate["id"] for candidate in candidates if candidate not in selected],
        "steps": steps,
        "objective": objective(selected, weights, policy["display_cost_penalty"]),
        "coverage": sorted(set().union(*(set(candidate["coverage"]) for candidate in selected))),
        "total_display_cost": sum(candidate["display_cost"] for candidate in selected),
        "mean_pairwise_redundancy": sum(pairwise) / len(pairwise) if pairwise else 0.0,
        "next_best_feasible": next_best,
        "mmr_diagnostic_order": [candidate["id"] for candidate in mmr_selected],
    }


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    blockers = validate_fixture(fixture)
    selection = facility_location_greedy(fixture) if not blockers else {"selected_ids": [], "unselected_recoverable_ids": []}
    policy = fixture.get("selection_policy", {})
    if selection.get("selected_ids") and selection["selected_ids"][0] != policy.get("anchor_plan_id"):
        blockers.append("anchor_not_first")
    if selection.get("total_display_cost", 0) > policy.get("display_budget", 0) + 1e-9:
        blockers.append("display_budget_exceeded")
    return {
        "experiment": "064-farmaxia-branch-subset-selection",
        "status": "BRANCH_SUBSET_SELECTION_VERIFIED" if not blockers else "BLOCKED",
        "blockers": blockers,
        "selection": selection,
        "metrics": {
            "selected_count": len(selection.get("selected_ids", [])),
            "candidate_count": len(fixture.get("candidates", [])),
            "unselected_branches_recoverable": policy.get("keep_unselected_recoverable") is True,
            "selection_method": policy.get("method"),
            "mmr_is_not_selection_authority": policy.get("mmr_role") == "diagnostic_only",
            "source_query_contract_required": True,
        },
        "execution_allowed": False,
        "external_execution": False,
        "human_data": False,
        "camera_used": False,
        "network_used": False,
        "scope_limit": "synthetic subset selection under display cost; no claim of optimal human cognitive load",
    }


def main() -> None:
    print(json.dumps(compile_fixture(load_json(FIXTURE)), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
