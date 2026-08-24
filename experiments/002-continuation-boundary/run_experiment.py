"""Compare order-only schedulers with a continuation-policy candidate.

This is a falsification experiment, not a CODE-INE implementation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
WORKFLOWS = ROOT / "workflows.json"


def load_workflows() -> dict[str, Any]:
    return json.loads(WORKFLOWS.read_text(encoding="utf-8"))


def new_state(scenario: dict[str, Any]) -> dict[str, Any]:
    return {
        "quality": float(scenario["initial_quality"]),
        "budget": float(scenario["budget"]),
        "used_cost": 0.0,
        "branch": "A",
        "uses": {},
        "trace": [],
    }


def can_execute(state: dict[str, Any], action_id: str, actions: dict[str, Any]) -> bool:
    action = actions[action_id]
    return (
        state["budget"] + 1e-9 >= action["cost"]
        and state["uses"].get(action_id, 0) < action["max_uses"]
    )


def execute(state: dict[str, Any], action_id: str, actions: dict[str, Any]) -> None:
    action = actions[action_id]
    before_branch = state["branch"]
    state["quality"] += action["realized_gain"]
    state["budget"] = max(0.0, state["budget"] - action["cost"])
    state["used_cost"] += action["cost"]
    state["branch"] = action["to_branch"]
    state["uses"][action_id] = state["uses"].get(action_id, 0) + 1
    state["trace"].append({
        "action": action_id,
        "kind": action["kind"],
        "branch_before": before_branch,
        "branch_after": state["branch"],
        "quality_after": round(state["quality"], 6),
        "budget_after": round(state["budget"], 6),
    })


def run_order_only(scenario: dict[str, Any], priority: bool) -> dict[str, Any]:
    state = new_state(scenario)
    actions = scenario["actions"]
    queue = list(scenario["static_queue"])
    while queue:
        if priority:
            candidates = [
                (index, action_id)
                for index, action_id in enumerate(queue)
                if can_execute(state, action_id, actions)
            ]
            if not candidates:
                break
            index, action_id = max(
                candidates,
                key=lambda item: actions[item[1]]["expected_gain"] / actions[item[1]]["cost"],
            )
            queue.pop(index)
        else:
            action_id = queue.pop(0)
            if not can_execute(state, action_id, actions):
                continue
        execute(state, action_id, actions)
    return summarize(state, "priority" if priority else "FIFO")


def run_continuation_candidate(scenario: dict[str, Any], threshold: float) -> dict[str, Any]:
    state = new_state(scenario)
    actions = scenario["actions"]
    stop_reason = "unknown"
    while True:
        candidates = [
            action_id
            for action_id in actions
            if can_execute(state, action_id, actions)
        ]
        if not candidates:
            stop_reason = "no_fitting_action"
            break
        action_id = max(
            candidates,
            key=lambda item: actions[item]["expected_gain"] / actions[item]["cost"],
        )
        ratio = actions[action_id]["expected_gain"] / actions[action_id]["cost"]
        if ratio < threshold:
            stop_reason = "expected_gain_below_threshold"
            break
        execute(state, action_id, actions)
    result = summarize(state, "continuation-candidate")
    result["stop_reason"] = stop_reason
    result["stopped_by_policy"] = stop_reason == "expected_gain_below_threshold"
    return result


def summarize(state: dict[str, Any], policy: str) -> dict[str, Any]:
    return {
        "policy": policy,
        "quality": round(state["quality"], 6),
        "used_cost": round(state["used_cost"], 6),
        "budget_left": round(state["budget"], 6),
        "utility": round(state["quality"] - 0.1 * state["used_cost"], 6),
        "trace": state["trace"],
        "branch_changes": sum(
            entry["branch_before"] != entry["branch_after"] for entry in state["trace"]
        ),
        "reuse_count": sum(entry["kind"] == "reuse" for entry in state["trace"]),
    }


def main() -> None:
    data = load_workflows()
    threshold = data["utility"]["min_expected_gain_per_cost"]
    report = []
    for scenario in data["scenarios"]:
        report.append({
            "scenario": scenario["id"],
            "results": [
                run_order_only(scenario, priority=False),
                run_order_only(scenario, priority=True),
                run_continuation_candidate(scenario, threshold),
            ],
        })
    print(json.dumps({"threshold": threshold, "scenarios": report}, indent=2))


if __name__ == "__main__":
    main()
