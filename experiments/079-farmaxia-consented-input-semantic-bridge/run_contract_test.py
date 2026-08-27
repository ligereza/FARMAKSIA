"""Positive contract for the real local consented input observer."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    completed = subprocess.run(
        [sys.executable, str(HERE / "run_experiment.py"), "--duration", "1.0", "--sample-hz", "5"],
        cwd=HERE.parents[1],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode:
        raise SystemExit(completed.stderr or "experiment 079 failed")
    payload = json.loads(completed.stdout)
    assert payload["status"] == "CONSENTED_INPUT_OBSERVER_VERIFIED"
    assert payload["validation_blockers"] == []
    assert payload["observation"]["sample_count"] >= 1
    assert payload["observation"]["key_values_persisted"] is False
    assert payload["observation"]["text_persisted"] is False
    assert payload["observation"]["window_titles_persisted"] is False
    assert payload["observation"]["semantic_intent_claimed"] is False
    assert payload["actions_performed"] == []
    print("FARMAXIA_079_CONSENTED_INPUT_CONTRACT_VALID")


if __name__ == "__main__":
    main()
