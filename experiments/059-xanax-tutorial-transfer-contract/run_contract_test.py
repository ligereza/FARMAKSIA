"""Contract test for experiment 059 output and safety boundaries."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).parent
ROOT = HERE.parents[1]


def main() -> None:
    runner = subprocess.run(
        [sys.executable, str(HERE / "run_experiment.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if runner.returncode != 0:
        raise SystemExit(runner.stderr or "experiment 059 failed")
    result = json.loads(runner.stdout)
    assert result["document_only"]["status"] == "TEACHING_DRAFT"
    assert result["document_only"]["automation_ready"] is False
    assert result["source_cards"]["incomplete"]["status"] == "SOURCE_INVALID"
    assert result["composed_with_bridge"]["status"] == "COMPOSABLE_DRY_RUN"
    assert result["composed_with_bridge"]["execution_allowed"] is False
    assert result["composed_without_bridge"]["status"] == "COMPOSITION_BLOCKED"
    assert result["composed_without_bridge"]["bridge"]["status"] == "BRIDGE_BLOCKED"
    assert result["human_data"] is False
    assert result["network_used"] is False
    assert result["applications_started"] is False
    assert result["commands_executed"] is False
    print("XANAX_059_TUTORIAL_TRANSFER_CONTRACT_VALID")


if __name__ == "__main__":
    main()
