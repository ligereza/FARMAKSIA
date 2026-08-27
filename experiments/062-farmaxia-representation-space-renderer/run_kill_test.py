"""Adversarial tests for semantic preservation and commitment boundaries."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_experiment import compile_space  # noqa: E402


def load_space() -> dict:
    return json.loads((HERE / "space.json").read_text(encoding="utf-8"))


def assert_blocked(space: dict, reason: str) -> None:
    result = compile_space(space)
    assert result["status"] == "BLOCKED", reason


def main() -> None:
    base = load_space()

    lost_semantics = deepcopy(base)
    lost_semantics["plans"][0]["preserves"].remove("scene_relations")
    assert_blocked(lost_semantics, "a branch dropped source relations")

    explore_execute = deepcopy(base)
    explore_execute["phase_contracts"]["explore"]["allowed"].append("execute")
    assert_blocked(explore_execute, "exploration acquired execution")

    no_confirmation = deepcopy(base)
    no_confirmation["phase_contracts"]["commit"]["requires"].remove("user_confirmation")
    assert_blocked(no_confirmation, "commit lost explicit confirmation")

    unknown_plan = deepcopy(base)
    unknown_plan["trajectory"][4]["plan_ids"].append("plan-not-declared")
    assert_blocked(unknown_plan, "comparison referenced an unknown branch")

    flashing = deepcopy(base)
    flashing["plans"][1]["sensory_policy"]["flashing"] = True
    assert_blocked(flashing, "unsafe periodic flashing crossed sensory policy")

    commit_before_confirm = deepcopy(base)
    commit_before_confirm["trajectory"].insert(7, {"type": "commit", "phase": "commit", "plan_id": "plan-map"})
    assert_blocked(commit_before_confirm, "commit happened before confirmation")

    no_revert = deepcopy(base)
    no_revert["phase_contracts"]["commit"]["allowed"].remove("revert")
    assert_blocked(no_revert, "commit lost reversibility")

    print("FARMAXIA_062_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
