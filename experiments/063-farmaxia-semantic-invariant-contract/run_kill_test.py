"""Adversarial tests for query preservation, provenance and UNKNOWN state."""

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

    lost_relation = deepcopy(base)
    lost_relation["views"][0]["relation_records"] = [
        item for item in lost_relation["views"][0]["relation_records"]
        if item["stable_ref"] != "relation:objects-form-composition"
    ]
    assert_blocked(lost_relation, "a critical relation disappeared from a view")

    invented_relation = deepcopy(base)
    invented_relation["views"][1]["relation_records"].append({"stable_ref": "relation:invented", "from": "entity:scene", "to": "entity:purpose", "kind": "proves", "source_ref": "relation:invented"})
    assert_blocked(invented_relation, "a view invented a relation")

    unknown_as_fact = deepcopy(base)
    unknown_as_fact["views"][2]["claims"][0]["state"] = "fact"
    assert_blocked(unknown_as_fact, "UNKNOWN silently became FACT")

    missing_provenance = deepcopy(base)
    missing_provenance["views"][3]["relation_records"][0].pop("source_ref")
    assert_blocked(missing_provenance, "a visible relation lost provenance")

    changed_relation = deepcopy(base)
    changed_relation["views"][0]["relation_records"][2]["kind"] = "causes"
    assert_blocked(changed_relation, "a relation changed meaning")

    active_entity_drift = deepcopy(base)
    active_entity_drift["views"][1]["active_entity"] = "entity:objects"
    assert_blocked(active_entity_drift, "the active entity drifted")

    print("FARMAXIA_063_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
