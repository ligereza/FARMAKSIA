"""Compare broad CODE-INE policy behavior with constrained value-of-computation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
SCENARIOS = ROOT / "scenarios.json"
IRREVERSIBLE_RISK_THRESHOLD = 0.35
REUSE_POLICY_BONUS = 0.02


def base_utility(action: dict[str, Any]) -> float:
    return (
        action["expected_gain"]
        - action["cost"]
        + action["reuse_credit"]
        + action["option_value"]
        - action["irreversible_risk"]
    )


def eligible(action: dict[str, Any]) -> bool:
    return action["authorized"] and action["irreversible_risk"] <= IRREVERSIBLE_RISK_THRESHOLD


def choose(scored: list[tuple[dict[str, Any], float]], *, stable_tie: bool) -> tuple[str, str, list[str]]:
    discarded = []
    if not scored:
        return "stop", "no authorized action survives constraints", discarded
    if stable_tie:
        best_action, best_score = max(scored, key=lambda item: item[1])
    else:
        best_action, best_score = max(
            scored,
            key=lambda item: (item[1], 1 if item[0]["kind"] == "reuse" else 0),
        )
    if best_score <= 0:
        return "stop", "best constrained utility is non-positive", discarded
    return best_action["id"], "best constrained utility", discarded


def codeine_policy(actions: list[dict[str, Any]]) -> dict[str, Any]:
    eligible_actions = [action for action in actions if eligible(action)]
    scored = [
        (
            action,
            base_utility(action) + (REUSE_POLICY_BONUS if action["kind"] == "reuse" and action["verified"] else 0.0),
        )
        for action in eligible_actions
    ]
    chosen, reason, _ = choose(scored, stable_tie=False)
    return {
        "choice": chosen,
        "reason": reason,
        "policy_bonus": REUSE_POLICY_BONUS,
        "eligible": [action["id"] for action in eligible_actions],
        "scores": {action["id"]: round(score, 6) for action, score in scored},
    }


def constrained_voc(actions: list[dict[str, Any]]) -> dict[str, Any]:
    eligible_actions = [action for action in actions if eligible(action)]
    scored = [(action, base_utility(action)) for action in eligible_actions]
    chosen, reason, _ = choose(scored, stable_tie=True)
    return {
        "choice": chosen,
        "reason": reason,
        "eligible": [action["id"] for action in eligible_actions],
        "scores": {action["id"]: round(score, 6) for action, score in scored},
    }


def main() -> None:
    scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    results = []
    for scenario in scenarios:
        candidate = codeine_policy(scenario["actions"])
        control = constrained_voc(scenario["actions"])
        results.append({
            "scenario": scenario["id"],
            "description": scenario["description"],
            "codeine": candidate,
            "constrained_voc": control,
            "match": candidate["choice"] == control["choice"],
            "difference_class": None if candidate["choice"] == control["choice"] else "reuse_policy_bonus_or_tie_break",
        })
    matches = sum(result["match"] for result in results)
    print(json.dumps({
        "scenario_count": len(results),
        "matches": matches,
        "mismatches": len(results) - matches,
        "parameters": {
            "irreversible_risk_threshold": IRREVERSIBLE_RISK_THRESHOLD,
            "reuse_policy_bonus": REUSE_POLICY_BONUS,
        },
        "results": results,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
