"""Generate deterministic synthetic geometry cases for experiment 010."""

from __future__ import annotations

import json
import random
from pathlib import Path


ROOT = Path(__file__).parent
OUTPUT = ROOT / "cases.json"
SEED = 20260823
CASE_COUNT = 40
CENTER_X = 200.0
TIME = 0.5
AREA_THRESHOLD = 6000.0


def generate_case(rng: random.Random, index: int) -> dict:
    regions = [
        {"id": "anchor-crossing", "x": 170.0, "y": 80.0, "width": 60.0, "height": 100.0, "stroke": "red"},
        {"id": "anchor-right", "x": 245.0, "y": 80.0, "width": 80.0, "height": 100.0, "stroke": "green"},
    ]
    palette = ["red", "green", "blue", "purple"]
    for region_index in range(6):
        regions.append({
            "id": f"region-{region_index:02d}",
            "x": float(rng.randint(20, 340)),
            "y": float(rng.randint(20, 160)),
            "width": float(rng.randint(20, 120)),
            "height": float(rng.randint(20, 110)),
            "stroke": palette[rng.randrange(len(palette))],
        })
    events = [
        {"time": 0.0, "region": "anchor-crossing", "event": "enter"},
        {"time": 0.9, "region": "anchor-crossing", "event": "exit"},
        {"time": 0.4, "region": "anchor-right", "event": "enter"},
        {"time": 0.8, "region": "anchor-right", "event": "exit"},
    ]
    for region in regions[2:]:
        start = round(rng.uniform(0.0, 0.8), 3)
        end = round(min(1.0, start + rng.uniform(0.1, 0.5)), 3)
        events.extend([
            {"time": start, "region": region["id"], "event": "enter"},
            {"time": end, "region": region["id"], "event": "exit"},
        ])
    return {"id": f"case-{index:03d}", "regions": regions, "events": events}


def main() -> None:
    rng = random.Random(SEED)
    payload = {
        "schema": "farmaxia:synthetic-svg-cases:0.1",
        "seed": SEED,
        "center_x": CENTER_X,
        "time": TIME,
        "area_threshold": AREA_THRESHOLD,
        "cases": [generate_case(rng, index) for index in range(CASE_COUNT)],
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"cases": CASE_COUNT, "seed": SEED, "output": str(OUTPUT)}, indent=2))


if __name__ == "__main__":
    main()
