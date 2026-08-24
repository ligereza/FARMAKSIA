"""Compare curve sampling, bounding boxes, and visible-layer relations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
CASES = ROOT / "cases.json"


def cubic(segment: list[dict[str, float]], t: float) -> dict[str, float]:
    u = 1.0 - t
    return {
        "x": u**3 * segment[0]["x"] + 3 * u**2 * t * segment[1]["x"] + 3 * u * t**2 * segment[2]["x"] + t**3 * segment[3]["x"],
        "y": u**3 * segment[0]["y"] + 3 * u**2 * t * segment[1]["y"] + 3 * u * t**2 * segment[2]["y"] + t**3 * segment[3]["y"],
    }


def sample_contour(segments: list[list[dict[str, float]]], steps: int) -> list[dict[str, float]]:
    points = []
    for segment in segments:
        for index in range(steps):
            points.append(cubic(segment, index / steps))
    return points


def point_in_polygon(vertices: list[dict[str, float]], point: dict[str, float]) -> bool:
    inside = False
    previous = vertices[-1]
    for current in vertices:
        crosses = (current["y"] > point["y"]) != (previous["y"] > point["y"])
        if crosses:
            boundary_x = (previous["x"] - current["x"]) * (point["y"] - current["y"]) / (previous["y"] - current["y"]) + current["x"]
            if point["x"] < boundary_x:
                inside = not inside
        previous = current
    return inside


def sample_shape(shape: dict[str, Any], steps: int) -> list[list[dict[str, float]]]:
    return [sample_contour(contour, steps) for contour in shape["contours"]]


def contains_shape(shape: dict[str, Any], point: dict[str, float], steps: int) -> bool:
    contours = sample_shape(shape, steps)
    if not point_in_polygon(contours[0], point):
        return False
    if shape["fill_rule"] == "evenodd" and any(point_in_polygon(contour, point) for contour in contours[1:]):
        return False
    return True


def shape_bbox(shape: dict[str, Any], steps: int) -> dict[str, float]:
    points = [point for contour in sample_shape(shape, steps) for point in contour]
    return {"min_x": min(point["x"] for point in points), "max_x": max(point["x"] for point in points), "min_y": min(point["y"] for point in points), "max_y": max(point["y"] for point in points)}


def bbox_contains(box: dict[str, float], point: dict[str, float]) -> bool:
    return box["min_x"] <= point["x"] <= box["max_x"] and box["min_y"] <= point["y"] <= box["max_y"]


def visible_exact(shapes: list[dict[str, Any]], point: dict[str, float], steps: int) -> dict[str, str] | None:
    candidates = [shape for shape in shapes if contains_shape(shape, point, steps)]
    if not candidates:
        return None
    top = max(candidates, key=lambda shape: shape["layer"])
    return {"id": top["id"], "style": top["style"]}


def visible_sampled(shapes: list[dict[str, Any]], point: dict[str, float]) -> dict[str, str] | None:
    candidates = []
    for shape in shapes:
        contours = shape["contours"]
        if not point_in_polygon(contours[0], point):
            continue
        if shape["fill_rule"] == "evenodd" and any(point_in_polygon(contour, point) for contour in contours[1:]):
            continue
        candidates.append(shape)
    if not candidates:
        return None
    top = max(candidates, key=lambda shape: shape["layer"])
    return {"id": top["id"], "style": top["style"]}


def check_case(case: dict[str, Any], steps: int) -> dict[str, Any]:
    point = case["query_point"]
    shapes = case["shapes"]
    exact = visible_exact(shapes, point, steps)
    curve_table = [{"id": shape["id"], "style": shape["style"], "layer": shape["layer"], "fill_rule": shape["fill_rule"], "contours": sample_shape(shape, steps)} for shape in shapes]
    bbox_graph = [{"id": shape["id"], "style": shape["style"], "layer": shape["layer"], "bbox": shape_bbox(shape, steps)} for shape in shapes]
    bbox_candidates = [node for node in bbox_graph if bbox_contains(node["bbox"], point)]
    bbox_top = max(bbox_candidates, key=lambda node: node["layer"]) if bbox_candidates else None
    relation_graph = {"visible": exact}
    table_exact = visible_sampled(curve_table, point)
    return {
        "exact": exact,
        "table": table_exact,
        "bbox": None if bbox_top is None else {"id": bbox_top["id"], "style": bbox_top["style"]},
        "relation": relation_graph["visible"],
        "table_preserves_visible": table_exact == exact,
        "bbox_preserves_visible": (None if bbox_top is None else {"id": bbox_top["id"], "style": bbox_top["style"]}) == exact,
        "bbox_hole_false_positive": bbox_top is not None and bbox_top["id"] == "donut-curve" and exact is not None and exact["id"] == "solid-curve",
        "relation_preserves_precomputed_visible": relation_graph["visible"] == exact,
        "layer_preserved_in_table": all(node["layer"] == shape["layer"] for node, shape in zip(curve_table, shapes)),
    }


def main() -> None:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    results = [check_case(case, payload["sample_steps"]) for case in payload["cases"]]
    print(json.dumps({
        "case_count": len(results),
        "seed": payload["seed"],
        "table_visible_matches": sum(result["table_preserves_visible"] for result in results),
        "bbox_visible_matches": sum(result["bbox_preserves_visible"] for result in results),
        "bbox_hole_false_positive_cases": sum(result["bbox_hole_false_positive"] for result in results),
        "relation_visible_matches": sum(result["relation_preserves_precomputed_visible"] for result in results),
        "layer_table_matches": sum(result["layer_preserved_in_table"] for result in results),
        "scope_limit": "synthetic cubic ellipses and layers only; not a creative corpus",
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
