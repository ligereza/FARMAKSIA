"""Adversarial tests for budget, source contract and selection authority."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_experiment import compile_fixture  # noqa: E402


def load_fixture() -> dict:
    return json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))


def assert_blocked(fixture: dict, reason: str) -> None:
    assert compile_fixture(fixture)["status"] == "BLOCKED", reason


def main() -> None:
    base = load_fixture()

    no_source_contract = deepcopy(base)
    no_source_contract["source_contract"]["required_query_count"] = 99
    assert_blocked(no_source_contract, "selection detached from semantic query contract")

    too_small_budget = deepcopy(base)
    too_small_budget["selection_policy"]["display_budget"] = 1.0
    assert_blocked(too_small_budget, "anchor exceeds display budget")

    mmr_authority = deepcopy(base)
    mmr_authority["selection_policy"]["mmr_role"] = "final_rank"
    assert_blocked(mmr_authority, "MMR became an opaque final ranking")

    unknown_need = deepcopy(base)
    unknown_need["candidates"][1]["coverage"].append("invented_need")
    assert_blocked(unknown_need, "candidate introduced an uncontracted need")

    missing_anchor = deepcopy(base)
    missing_anchor["selection_policy"]["anchor_plan_id"] = "plan-missing"
    assert_blocked(missing_anchor, "full anchor disappeared")

    candidate_not_query_safe = deepcopy(base)
    candidate_not_query_safe["candidates"][2]["preserves_critical_queries"] = False
    assert_blocked(candidate_not_query_safe, "candidate bypassed semantic invariants")

    negative_threshold = deepcopy(base)
    negative_threshold["selection_policy"]["min_marginal_gain"] = -1
    assert_blocked(negative_threshold, "negative stop threshold accepted")

    print("FARMAXIA_064_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
