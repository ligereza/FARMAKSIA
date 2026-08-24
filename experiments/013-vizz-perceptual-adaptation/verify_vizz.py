"""Verify that the local VIZZ prototype exposes its declared modes safely."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parent


def main() -> None:
    html = (ROOT / "vizz.html").read_text(encoding="utf-8")
    trace = json.loads((ROOT / "trace.json").read_text(encoding="utf-8"))
    required_modes = ("text", "timeline", "focus", "field")
    for mode in required_modes:
        if f'value="{mode}"' not in html:
            raise SystemExit(f"VIZZ_INVALID: missing mode {mode}")
    for token in ("luminance", "contrast", "focus_window", "aria-live", "prefers-reduced-motion"):
        if token not in html:
            raise SystemExit(f"VIZZ_INVALID: missing declared control or accessibility token {token}")
    if len(trace["events"]) != 10:
        raise SystemExit("VIZZ_INVALID: expected 10 trace events")
    if "fetch(" in html or "XMLHttpRequest" in html or "WebSocket" in html:
        raise SystemExit("VIZZ_INVALID: network access is not allowed")
    print("VIZZ_PROTOTYPE_VALID")


if __name__ == "__main__":
    main()
