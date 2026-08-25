"""Contract test for the CODE-INE experience compiler."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    runner = subprocess.run(
        [sys.executable, str(HERE / "run_experiment.py")],
        cwd=HERE.parents[1],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if runner.returncode != 0:
        raise SystemExit(runner.stderr or "experiment 060 failed")
    result = json.loads(runner.stdout)
    assert result["status"] == "COMPILED_VERIFIED_WITH_RESIDUE"
    assert result["semantic_map"]["unknown_count"] == 1
    assert len(result["semantic_map"]["residue"]) == 5
    assert result["simulation"]["states"] == ["ready", "working", "blocked", "retrying", "verified"]
    assert result["oracle"]["validation"] == "verified"
    assert result["machine"]["execution_policy"] == "dry_run_only"
    plan = result["representation_plan"]
    assert plan["reversible"] is True
    assert plan["intensity_policy"]["periodic_flashing"] is False
    assert plan["friction_policy"]["source"] == "declared_interaction_only"
    assert result["execution_allowed"] is False
    assert result["human_data"] is False
    assert result["camera_used"] is False
    assert result["network_used"] is False
    assert result["arbitrary_code_executed"] is False
    print("CODEINE_060_EXPERIENCE_COMPILER_CONTRACT_VALID")


if __name__ == "__main__":
    main()
