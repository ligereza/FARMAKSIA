"""Static contract tests for the webcam-to-Blender bridge."""

from __future__ import annotations

import ast
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    runner = (HERE / "run_live_distance.py").read_text(encoding="utf-8")
    bridge = (HERE / "blender_live_bridge.py").read_text(encoding="utf-8")
    launcher = (HERE / "start_vizz_blender.ps1").read_text(encoding="utf-8")
    ast.parse(runner)
    ast.parse(bridge)
    for required in (
        "GpuTracker",
        "scale_only=True",
        "reference_distance_m",
        "relative_distance_ratio",
        "atomic_write",
        "raw_video",
        "network_used",
        "input_injected",
        "DEFAULT_REFERENCE_DISTANCE_M",
        "default=None",
        "until Ctrl+C",
        "transient Windows file locks",
        "focus_distance_m",
        "focus-mode",
    ):
        assert required in runner, required
    for required in (
        "VIZZ_CONTROLLER",
        "observer_distance_m",
        "focus_offset_m",
        "focus_distance_m",
        "bpy.app.timers.register",
        "update_tag",
    ):
        assert required in bridge, required
    assert "import socket" not in runner.lower()
    assert "import requests" not in runner.lower()
    assert "subprocess" not in bridge.lower()
    for required in ("blender_live_bridge.py", "run_live_distance.py", "--sample-hz", "5", "Wait-Process"):
        assert required in launcher, required
    print("FARMAXIA_086_VIZZ_BLENDER_LIVE_DISTANCE_CONTRACT_VALID")


if __name__ == "__main__":
    main()
