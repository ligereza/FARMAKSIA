"""Positive contract test for the lighting surface adapter."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    result = subprocess.run(
        [sys.executable, str(HERE / "run_experiment.py")],
        cwd=HERE.parents[1],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode:
        raise SystemExit(result.stderr or "experiment 083 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "LIGHTING_SURFACE_CONTRACT_VERIFIED"
    assert payload["blockers"] == []
    assert payload["contract"]["source_app"] == "grandMA3"
    assert payload["contract"]["source_version"] == "2.4.2.2"
    assert payload["contract"]["target_vocabulary"] == "Avolites Titan"
    assert payload["contract"]["task_count"] == 5
    assert payload["contract"]["partial_task_count"] == 3
    assert all(item["max_error"] <= 1e-12 for item in payload["roundtrips"])
    assert payload["safety"] == {
        "network_used": False,
        "external_execution": False,
        "input_injected": False,
        "source_write_attempted": False,
        "observed_surfaces": False,
    }
    print("FARMAXIA_083_LIGHTING_SURFACE_CONTRACT_VALID")


if __name__ == "__main__":
    main()
