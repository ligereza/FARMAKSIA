"""Positive contract test for the 062 renderer and its local safety boundary."""

from __future__ import annotations

import json
import re
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
    if result.returncode != 0:
        raise SystemExit(result.stderr or "experiment 062 failed")
    payload = json.loads(result.stdout)
    assert payload["status"] == "REPRESENTATION_SPACE_RENDERER_VERIFIED"
    assert payload["metrics"]["alternative_plan_count"] == 4
    assert payload["metrics"]["distinct_representation_kinds"] == 4
    assert payload["metrics"]["source_semantics_preserved_by_all_plans"] is True
    assert payload["metrics"]["compare_requires_explicit_candidates"] is True
    assert payload["metrics"]["commit_requires_confirmation"] is True
    assert payload["metrics"]["preview_reversible"] is True
    assert payload["execution_allowed"] is False
    assert payload["external_execution"] is False
    assert payload["human_data"] is False
    assert payload["camera_used"] is False
    assert payload["network_used"] is False
    assert payload["generated_code_executed"] is False

    html = (HERE / "renderer.html").read_text(encoding="utf-8")
    required_markers = [
        "data-phase=\"explore\"",
        "data-phase=\"compare\"",
        "data-phase=\"commit\"",
        "id=\"representation-canvas\"",
        "id=\"alternative-tray\"",
        "id=\"revert\"",
        "confirm-direction",
        "id=\"space-data\"",
        "prefers-reduced-motion",
    ]
    for marker in required_markers:
        assert marker in html, f"renderer marker missing: {marker}"
    forbidden_markers = ["getUserMedia", "WebSocket", "XMLHttpRequest", "fetch(", "eval(", "new Function", "window.open"]
    for marker in forbidden_markers:
        assert marker not in html, f"renderer crossed local boundary: {marker}"
    canonical = json.loads((HERE / "space.json").read_text(encoding="utf-8"))
    embedded_match = re.search(r'<script id="space-data" type="application/json">\s*(.*?)\s*</script>', html, re.DOTALL)
    assert embedded_match, "renderer has no embedded local space data"
    embedded = json.loads(embedded_match.group(1))
    assert embedded["source_state"]["revision"] == canonical["source_state"]["revision"]
    assert {item["id"] for item in embedded["source_state"]["entities"]} == {item["id"] for item in canonical["source_state"]["entities"]}
    assert [item["id"] for item in embedded["plans"]] == [item["id"] for item in canonical["plans"]]
    assert all(set(item["preserves"]) == {"scene_entities", "scene_relations", "unknowns"} for item in embedded["plans"])
    print("FARMAXIA_062_REPRESENTATION_SPACE_CONTRACT_VALID")


if __name__ == "__main__":
    main()
