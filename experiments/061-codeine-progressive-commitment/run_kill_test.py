"""Adversarial tests for ambiguity tolerance and commitment gates."""

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


def main() -> None:
    base = load_fixture()

    premature = deepcopy(base)
    premature["intent_revisions"][0]["patch"].insert(1, {"op": "replace", "path": "/maturity", "value": "committed"})
    assert compile_fixture(premature)["status"] == "BLOCKED"

    no_alternatives = deepcopy(base)
    no_alternatives["representation_space"] = [no_alternatives["representation_space"][0]]
    assert compile_fixture(no_alternatives)["status"] == "BLOCKED"

    bad_patch = deepcopy(base)
    bad_patch["intent_revisions"][0]["patch"].append({"op": "replace", "path": "/missing/key", "value": "invalid"})
    try:
        compile_fixture(bad_patch)
    except KeyError:
        pass
    else:
        raise AssertionError("invalid JSON Patch path crossed the contract")

    no_verifier = deepcopy(base)
    no_verifier["action_contract"].pop("verification_method")
    assert compile_fixture(no_verifier)["status"] == "BLOCKED"

    consequential_without_auth = deepcopy(base)
    consequential_without_auth["action_contract"]["risk_class"] = "consequential"
    consequential_without_auth["action_contract"]["authorized"] = False
    assert compile_fixture(consequential_without_auth)["status"] == "BLOCKED"

    execute_early = deepcopy(base)
    execute_early["trajectory"].insert(0, {"type": "dry_run", "action_id": "preview-night-composition", "at_revision": 1})
    assert compile_fixture(execute_early)["status"] == "BLOCKED"

    print("CODEINE_061_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
