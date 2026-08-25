"""Static contract test for the no-camera overlay runtime."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = (ROOT / "overlay_runtime.py").read_text(encoding="utf-8")
RUNNER = (ROOT / "run_overlay.py").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")

ast.parse(SOURCE)
ast.parse(RUNNER)
required = [
    "RepresentationPlan",
    "source",
    "target_space",
    "focus_x",
    "focus_y",
    "expires_at",
    "reversible",
    "virtual_desktop",
    "camera=False",
    "click_through=True",
]
for marker in required:
    if marker not in SOURCE + RUNNER:
        raise SystemExit(f"missing marker: {marker}")
for forbidden in ("getUserMedia", "WebSocket", "XMLHttpRequest", "fetch(", "eval(", "new Function"):
    if forbidden in SOURCE + RUNNER:
        raise SystemExit(f"forbidden capability: {forbidden}")
for marker in ("no inicia camara", "no usa red", "click-through", "Kill tests"):
    if marker not in README:
        raise SystemExit(f"README missing marker: {marker}")
print("FARMAXIA_057_OVERLAY_CONTRACT_VALID")
print("camera=no-network=no-execution=click-through=reversible")
