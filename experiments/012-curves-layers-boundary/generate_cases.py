"""Generate deterministic closed Bezier curve scenes with layers."""

from __future__ import annotations

import json
import random
from pathlib import Path


ROOT = Path(__file__).parent
OUTPUT = ROOT / "cases.json"
SEED = 20260823
CASE_COUNT = 20
KAPPA = 0.5522847498


def ellipse_segments(cx: float, cy: float, rx: float, ry: float) -> list[list[dict[str, float]]]:
    top = {"x": cx, "y": cy - ry}
    right = {"x": cx + rx, "y": cy}
    bottom = {"x": cx, "y": cy + ry}
    left = {"x": cx - rx, "y": cy}
    return [
        [top, {"x": cx + KAPPA * rx, "y": cy - ry}, {"x": cx + rx, "y": cy - KAPPA * ry}, right],
        [right, {"x": cx + rx, "y": cy + KAPPA * ry}, {"x": cx + KAPPA * rx, "y": cy + ry}, bottom],
        [bottom, {"x": cx - KAPPA * rx, "y": cy + ry}, {"x": cx - rx, "y": cy + KAPPA * ry}, left],
        [left, {"x": cx - rx, "y": cy - KAPPA * ry}, {"x": cx - KAPPA * rx, "y": cy - ry}, top],
    ]


def generate_case(rng: random.Random, index: int) -> dict:
    scale = rng.uniform(0.8, 1.2)
    point = {"x": 200.0, "y": 140.0}
    return {
        "id": f"curve-case-{index:03d}",
        "query_point": point,
        "shapes": [
            {
                "id": "solid-curve",
                "style": "red",
                "layer": 1,
                "fill_rule": "nonzero",
                "contours": [ellipse_segments(point["x"], point["y"], 70 * scale, 45 * scale)],
            },
            {
                "id": "donut-curve",
                "style": "blue",
                "layer": 3,
                "fill_rule": "evenodd",
                "contours": [
                    ellipse_segments(point["x"], point["y"], 95 * scale, 65 * scale),
                    ellipse_segments(point["x"], point["y"], 25 * scale, 18 * scale),
                ],
            },
            {
                "id": "off-center-curve",
                "style": "green",
                "layer": 2,
                "fill_rule": "nonzero",
                "contours": [ellipse_segments(330, 260, 30 * scale, 20 * scale)],
            },
        ],
    }


def main() -> None:
    rng = random.Random(SEED)
    payload = {
        "schema": "farmaxia:synthetic-bezier-layer-cases:0.1",
        "seed": SEED,
        "sample_steps": 40,
        "cases": [generate_case(rng, index) for index in range(CASE_COUNT)],
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"cases": CASE_COUNT, "seed": SEED, "output": str(OUTPUT)}, indent=2))


if __name__ == "__main__":
    main()
