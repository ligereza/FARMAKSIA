"""Kill test for the current CODE-INE candidate.

The dynamic baselines receive the same semantic action set as the candidate.
This asks whether the current policy is just value-of-computation reasoning.
"""

from __future__ import annotations

import json
from pathlib import Path

from run_experiment import (
    can_execute,
    execute,
    load_workflows,
    new_state,
    run_continuation_candidate,
    summarize,
)


ROOT = Path(__file__).parent
KILL_SCENARIOS = ROOT / "kill_scenarios.json"


def run_dynamic_priority(scenario: dict) -> dict:
    state = new_state(scenario)
    actions = scenario["actions"]
    while True:
        candidates = [
            action_id for action_id in actions if can_execute(state, action_id, actions)
        ]
        if not candidates:
            break
        action_id = max(
            candidates,
            key=lambda item: actions[item]["expected_gain"] / actions[item]["cost"],
        )
        execute(state, action_id, actions)
    result = summarize(state, "dynamic-priority")
    result["stop_reason"] = "no_fitting_action"
    return result


def run_value_of_computation(scenario: dict, cost_penalty: float) -> dict:
    state = new_state(scenario)
    actions = scenario["actions"]
    while True:
        candidates = [
            action_id for action_id in actions if can_execute(state, action_id, actions)
        ]
        if not candidates:
            stop_reason = "no_fitting_action"
            break
        action_id = max(
            candidates,
            key=lambda item: actions[item]["expected_gain"] - cost_penalty * actions[item]["cost"],
        )
        net_expected_gain = actions[action_id]["expected_gain"] - cost_penalty * actions[action_id]["cost"]
        if net_expected_gain <= 0:
            stop_reason = "non_positive_expected_net_gain"
            break
        execute(state, action_id, actions)
    result = summarize(state, "value-of-computation")
    result["stop_reason"] = stop_reason
    return result


def action_trace(result: dict) -> list[str]:
    return [entry["action"] for entry in result["trace"]]


def main() -> None:
    data = load_workflows()
    extra = json.loads(KILL_SCENARIOS.read_text(encoding="utf-8"))
    penalty = data["utility"]["cost_penalty"]
    threshold = data["utility"]["min_expected_gain_per_cost"]
    report = []
    for scenario in data["scenarios"] + extra["scenarios"]:
        candidate = run_continuation_candidate(scenario, threshold)
        dynamic = run_dynamic_priority(scenario)
        value = run_value_of_computation(scenario, penalty)
        report.append({
            "scenario": scenario["id"],
            "candidate": candidate,
            "dynamic_priority": dynamic,
            "value_of_computation": value,
            "candidate_matches_dynamic_priority": action_trace(candidate) == action_trace(dynamic),
            "candidate_matches_value_of_computation": action_trace(candidate) == action_trace(value),
        })
    print(json.dumps({"cost_penalty": penalty, "threshold": threshold, "scenarios": report}, indent=2))


if __name__ == "__main__":
    main()
