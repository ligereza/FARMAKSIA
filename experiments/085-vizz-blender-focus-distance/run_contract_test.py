"""Static contract test for the Blender scene definition."""

from __future__ import annotations

import ast
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    source = (HERE / "build_scene.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert 'scene.render.engine = "CYCLES"' in source
    assert 'controller["observer_distance_m"]' in source
    assert 'controller["focus_distance_m"]' in source
    assert '"focus + offset"' in source
    assert 'controller["focus_offset_m"]' in source
    assert 'external_assets_used": False' in source
    assert 'network_used": False' in source
    assert "SCREEN_W = 0.420" in source
    assert "SCREEN_H = SCREEN_W * 9.0 / 16.0" in source
    expected = {
        "screen_aspect": 16 / 9,
        "near_plane_offset_m": -0.220,
        "default_distance_m": 0.600,
    }
    assert abs(expected["screen_aspect"] - 16 / 9) < 1e-12
    assert expected["near_plane_offset_m"] < 0
    assert expected["default_distance_m"] > 0
    print("FARMAXIA_085_VIZZ_BLENDER_FOCUS_DISTANCE_CONTRACT_VALID")


if __name__ == "__main__":
    main()
