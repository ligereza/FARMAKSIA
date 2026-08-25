"""Adversarial tests for the CODE-INE experience compiler."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_experiment import compile_fixture, compile_machine, compile_representation_plan, simulate  # noqa: E402


def fixture() -> dict:
    return json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))


def main() -> None:
    base = fixture()
    missing_residue = deepcopy(base)
    missing_residue["analogy"]["mappings"][0].pop("residue")
    assert compile_fixture(missing_residue)["status"] == "BLOCKED"

    no_revert = deepcopy(base)
    no_revert["intent"]["declared_preferences"]["motion"] = "full"
    result = compile_fixture(no_revert)
    assert result["status"] == "COMPILED_VERIFIED_WITH_RESIDUE"
    result["representation_plan"]["controls"].remove("revert")
    assert "missing_user_control" in __import__("run_experiment").validate_representation_plan(result["representation_plan"])

    mutated_machine = compile_machine(base)
    mutated_machine["transition_table"]["working"]["failure"]["to"] = "verified"
    simulation = simulate(mutated_machine, base["task"]["trace"])
    assert simulation["states"] != base["task"]["expected_states"]

    flashing = compile_representation_plan(base, {"states": base["task"]["expected_states"]})
    flashing["intensity_policy"]["periodic_flashing"] = True
    assert "periodic_flashing_not_allowed" in __import__("run_experiment").validate_representation_plan(flashing)

    unknown_event = deepcopy(base)
    unknown_event["task"]["trace"].append("unexplained_event")
    unknown_event["task"]["expected_states"].append("verified")
    assert compile_fixture(unknown_event)["status"] == "BLOCKED"

    print("CODEINE_060_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
