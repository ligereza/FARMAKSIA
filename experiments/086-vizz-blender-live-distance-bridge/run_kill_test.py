"""Kill tests for unsafe or non-identifiable live distance behavior."""

from __future__ import annotations

import ast
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    runner = (HERE / "run_live_distance.py").read_text(encoding="utf-8")
    bridge = (HERE / "blender_live_bridge.py").read_text(encoding="utf-8")
    ast.parse(runner)
    ast.parse(bridge)
    assert "status = \"UNKNOWN\"" in runner
    assert "facial_rulers_disagree" in runner
    assert "face_observation_missing" in runner
    assert "distance_outside_safe_bridge_domain" in runner
    assert "deadline = None if args.duration is None" in runner
    assert "while deadline is None or" in runner
    assert "temporary.replace(path)" in runner
    assert "VIZZ_086_CONTROL_WRITE_LOCKED_RETRYING" in runner
    assert "focus_distance_m" in runner
    assert "focus_distance_m" in bridge
    assert "payload.get(\"status\") != \"VALID\"" in bridge
    assert "if not isinstance(distance" in bridge
    assert '"network_used": False' in runner
    assert '"input_injected": False' in runner
    print("FARMAXIA_086_VIZZ_BLENDER_LIVE_DISTANCE_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
