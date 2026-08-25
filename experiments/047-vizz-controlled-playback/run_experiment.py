"""Run the four controlled VIZZ playback policies on a synthetic scene."""

from __future__ import annotations

import json
from pathlib import Path

from playback_policy import PlaybackConfig, SceneElement, evaluate_scene


HERE = Path(__file__).parent


SCENE = (
    SceneElement("editor", 0.25, 0.50, "text", text=True),
    SceneElement("terminal", 0.78, 0.72, "text", text=True),
    SceneElement("alert", 0.95, 0.12, "alert", base_detail=0.85, peripheral_signal=True),
    SceneElement("chart", 0.83, 0.25, "chart", base_detail=0.80, peripheral_signal=True),
    SceneElement("toolbar", 0.50, 0.04, "control", text=True),
    SceneElement("background", 0.52, 0.52, "background", base_detail=0.90),
)


def main() -> None:
    results = []
    for mode in ("static_full", "static_clean", "adaptive_protected", "adaptive_unprotected"):
        config = PlaybackConfig(mode=mode, focus_u=0.25, focus_v=0.50)
        elements = evaluate_scene(SCENE, config, task="coding")
        results.append(
            {
                "mode": mode,
                "focus": [config.focus_u, config.focus_v],
                "elements": elements,
                "peripheral_signals_preserved": sum(item["peripheral_signal_preserved"] for item in elements),
                "legible_text_descriptors": sum(item["text_legible_descriptor"] for item in elements),
            }
        )
    result = {
        "schema": "farmaxia:vizz-controlled-playback:0.1",
        "experiment": "047-vizz-controlled-playback",
        "objective": "compare static and gaze-contingent visual policies without human data or desktop mutation",
        "scene_element_count": len(SCENE),
        "results": results,
        "human_data": False,
        "camera_opened": False,
        "screen_content_mutated": False,
        "network_used": False,
        "scope_limit": "synthetic descriptors and local HTML playback; no claim of human comfort, attention or task improvement",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
