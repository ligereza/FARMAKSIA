"""Generate deterministic non-rectangular polygon cases."""

from __future__ import annotations

import json
import random
from pathlib import Path


ROOT = Path(__file__).parent
OUTPUT = ROOT / "cases.json"
SEED = 20260823
CASE_COUNT = 20


def generate_case(rng: random.Random, index: int) -> dict:
    point = {"x": 200.0, "y": 140.0}
    scale = round(rng.uniform(0.8, 1.2), 3)
    px, py = point["x"], point["y"]
    polygons = [
        {
            "id": "exact-inside",
            "style": "red",
            "layer": 2,
            "vertices": [
                {"x": px - 100 * scale, "y": py + 50 * scale},
                {"x": px + 100 * scale, "y": py + 50 * scale},
                {"x": px, "y": py - 100 * scale},
            ],
        },
        {
            "id": "bbox-only",
            "style": "blue",
            "layer": 1,
            "vertices": [
                {"x": px - 100 * scale, "y": py - 100 * scale},
                {"x": px + 100 * scale, "y": py - 100 * scale},
                {"x": px - 100 * scale, "y": py + 20 * scale},
            ],
        },
        {
            "id": "disjoint",
            "style": "green",
            "layer": 0,
            "vertices": [
                {"x": px + 140 * scale, "y": py + 60 * scale},
                {"x": px + 190 * scale, "y": py + 60 * scale},
                {"x": px + 160 * scale, "y": py + 110 * scale},
            ],
        },
    ]
    return {"id": f"polygon-case-{index:03d}", "query_point": point, "polygons": polygons}


def main() -> None:
    rng = random.Random(SEED)
    payload = {
        "schema": "farmaxia:synthetic-polygon-cases:0.1",
        "seed": SEED,
        "cases": [generate_case(rng, index) for index in range(CASE_COUNT)],
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"cases": CASE_COUNT, "seed": SEED, "output": str(OUTPUT)}, indent=2))


if __name__ == "__main__":
    main()
