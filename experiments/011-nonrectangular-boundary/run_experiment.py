"""Measure exact polygon queries against lossy bounding-box graphs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
CASES = ROOT / "cases.json"


def contains_point(vertices: list[dict[str, float]], point: dict[str, float]) -> bool:
    inside = False
    x, y = point["x"], point["y"]
    previous = vertices[-1]
    for current in vertices:
        crosses = (current["y"] > y) != (previous["y"] > y)
        if crosses:
            boundary_x = (previous["x"] - current["x"]) * (y - current["y"]) / (previous["y"] - current["y"]) + current["x"]
            if x < boundary_x:
                inside = not inside
        previous = current
    return inside


def bbox(vertices: list[dict[str, float]]) -> dict[str, float]:
    xs = [vertex["x"] for vertex in vertices]
    ys = [vertex["y"] for vertex in vertices]
    return {"min_x": min(xs), "max_x": max(xs), "min_y": min(ys), "max_y": max(ys)}


def bbox_contains(box: dict[str, float], point: dict[str, float]) -> bool:
    return box["min_x"] <= point["x"] <= box["max_x"] and box["min_y"] <= point["y"] <= box["max_y"]


def check_case(case: dict[str, Any]) -> dict[str, Any]:
    point = case["query_point"]
    source = case["polygons"]
    vertex_table = [{"id": polygon["id"], "vertices": polygon["vertices"]} for polygon in source]
    bbox_graph = [{"id": polygon["id"], "bbox": bbox(polygon["vertices"])} for polygon in source]
    exact_relations = [polygon["id"] for polygon in source if contains_point(polygon["vertices"], point)]
    source_style = [polygon["id"] for polygon in source if polygon["style"] == "red"]
    vertex_answers = [polygon["id"] for polygon in vertex_table if contains_point(polygon["vertices"], point)]
    bbox_answers = [polygon["id"] for polygon in bbox_graph if bbox_contains(polygon["bbox"], point)]
    return {
        "source_answers": exact_relations,
        "vertex_answers": vertex_answers,
        "bbox_answers": bbox_answers,
        "exact_relation_answers": exact_relations,
        "style_answers": source_style,
        "vertex_preserves_exact_query": vertex_answers == exact_relations,
        "bbox_preserves_exact_query": bbox_answers == exact_relations,
        "bbox_false_positive": sorted(set(bbox_answers) - set(exact_relations)),
        "relation_graph_preserves_precomputed_relation": exact_relations == exact_relations,
        "bbox_graph_lacks_vertices": all("vertices" not in node for node in bbox_graph),
    }


def main() -> None:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    results = [check_case(case) for case in payload["cases"]]
    exact_matches = sum(result["vertex_preserves_exact_query"] for result in results)
    bbox_matches = sum(result["bbox_preserves_exact_query"] for result in results)
    false_positive_cases = sum(bool(result["bbox_false_positive"]) for result in results)
    relation_matches = sum(result["relation_graph_preserves_precomputed_relation"] for result in results)
    print(json.dumps({
        "case_count": len(results),
        "seed": payload["seed"],
        "vertex_exact_matches": exact_matches,
        "bbox_exact_matches": bbox_matches,
        "bbox_false_positive_cases": false_positive_cases,
        "precomputed_relation_matches": relation_matches,
        "all_vertices_preserve": exact_matches == len(results),
        "bbox_loss_observed": false_positive_cases == len(results),
        "scope_limit": "synthetic triangles only; not a creative corpus",
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
