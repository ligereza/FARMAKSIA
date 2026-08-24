"""Small, dependency-free measurement harness for Experiment 001.

This is an experiment, not an implementation of any FARMAKSIA operator.
It deliberately keeps the representations explicit so that loss and residue
can be inspected rather than hidden behind a framework.
"""

from __future__ import annotations

import json
import statistics
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable


SVG_NS = "{http://www.w3.org/2000/svg}"
ROOT = Path(__file__).parent
SOURCE = ROOT / "input.svg"
EVENTS = ROOT / "events.json"
CENTER_X = 200.0


def read_regions() -> list[dict[str, Any]]:
    root = ET.parse(SOURCE).getroot()
    regions = []
    for element in root:
        if element.tag != f"{SVG_NS}rect" or element.attrib.get("id") == "court":
            continue
        regions.append(
            {
                "id": element.attrib["id"],
                "x": float(element.attrib["x"]),
                "y": float(element.attrib["y"]),
                "width": float(element.attrib["width"]),
                "height": float(element.attrib["height"]),
            }
        )
    return regions


def intersects_center(region: dict[str, Any]) -> bool:
    return region["x"] <= CENTER_X <= region["x"] + region["width"]


def query_spatial(regions: list[dict[str, Any]]) -> list[str]:
    return [region["id"] for region in regions if intersects_center(region)]


def build_table(regions: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "kind": "geometry_table",
        "center_x": CENTER_X,
        "rows": [dict(region) for region in regions],
    }


def query_table(table: dict[str, Any]) -> list[str]:
    return query_spatial(table["rows"])


def build_graph(regions: list[dict[str, Any]]) -> dict[str, Any]:
    nodes = [{"id": region["id"], "kind": "region"} for region in regions]
    edges = [
        {"from": region["id"], "to": "center-line", "relation": "intersects"}
        for region in regions
        if intersects_center(region)
    ]
    nodes.append({"id": "center-line", "kind": "query_reference"})
    return {"kind": "relation_graph", "nodes": nodes, "edges": edges}


def query_graph(graph: dict[str, Any]) -> list[str]:
    return [edge["from"] for edge in graph["edges"] if edge["relation"] == "intersects"]


def read_events() -> list[dict[str, Any]]:
    return json.loads(EVENTS.read_text(encoding="utf-8"))


def build_temporal_state(
    regions: list[dict[str, Any]], events: list[dict[str, Any]]
) -> dict[str, Any]:
    intervals: dict[str, tuple[float, float]] = {}
    enters: dict[str, float] = {}
    for event in events:
        region = event["region"]
        if event["event"] == "enter":
            enters[region] = float(event["time"])
        elif event["event"] == "exit" and region in enters:
            intervals[region] = (enters.pop(region), float(event["time"]))
    if enters or set(intervals) != {region["id"] for region in regions}:
        raise ValueError("event log does not provide a complete interval per region")
    return {
        "kind": "temporal_geometry",
        "center_x": CENTER_X,
        "time_domain": [0.0, 1.0],
        "rows": [
            {**region, "active_from": intervals[region["id"]][0], "active_to": intervals[region["id"]][1]}
            for region in regions
        ],
    }


def build_temporal_control(regions: list[dict[str, Any]]) -> dict[str, Any]:
    """Null control: adds a time field without differentiating the regions."""
    return {
        "kind": "temporal_control",
        "center_x": CENTER_X,
        "time_domain": [0.0, 1.0],
        "rows": [
            {**region, "active_from": 0.0, "active_to": 1.0}
            for region in regions
        ],
    }


def query_temporal_spatial(state: dict[str, Any]) -> list[str]:
    return query_spatial(state["rows"])


def query_active(state: dict[str, Any], timestamp: float) -> list[str]:
    return [
        region["id"]
        for region in state["rows"]
        if region["active_from"] <= timestamp < region["active_to"]
    ]


def encoded_size(value: Any) -> int:
    return len(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def benchmark(function: Callable[[], Any], repeats: int = 200) -> float:
    samples = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        function()
        samples.append(time.perf_counter_ns() - start)
    return statistics.median(samples) / 1_000_000


def main() -> None:
    source_regions = read_regions()
    events = read_events()
    table = build_table(source_regions)
    graph = build_graph(source_regions)
    temporal = build_temporal_state(source_regions, events)
    temporal_control = build_temporal_control(source_regions)
    expected = query_spatial(source_regions)

    representations = [
        {
            "name": "svg-derived-source",
            "value": {"kind": "svg_regions", "center_x": CENTER_X, "rows": source_regions},
            "query": lambda: query_spatial(source_regions),
            "new_queries": [],
            "loss": ["SVG element/style/root metadata not represented in derived baseline"],
            "reconstruction": "spatial_regions_only",
        },
        {
            "name": "geometry-table",
            "value": table,
            "query": lambda: query_table(table),
            "new_queries": ["filter regions by numeric geometry"],
            "loss": ["original SVG ordering/style/element tags"],
            "reconstruction": "spatial_regions_only",
        },
        {
            "name": "relation-graph",
            "value": graph,
            "query": lambda: query_graph(graph),
            "new_queries": ["traverse declared relations"],
            "loss": ["coordinates, dimensions, and ability to recompute other geometric queries"],
            "reconstruction": "not_reconstructible",
        },
        {
            "name": "temporal-geometry",
            "value": temporal,
            "query": lambda: query_temporal_spatial(temporal),
            "new_queries": ["active_at(0.25)", "active_at(0.75)"],
            "loss": ["time was not present in source; intervals are an added model assumption"],
            "reconstruction": "spatial_regions_plus_added_time",
        },
        {
            "name": "temporal-control",
            "value": temporal_control,
            "query": lambda: query_temporal_spatial(temporal_control),
            "new_queries": ["active_at(t) (constant result; no new distinction)"],
            "loss": ["time field is present but carries no source-derived distinction"],
            "reconstruction": "spatial_regions_plus_redundant_time",
        },
    ]

    results = []
    for item in representations:
        answer = item["query"]()
        results.append(
            {
                "representation": item["name"],
                "bytes_json": encoded_size(item["value"]),
                "query_median_ms": round(benchmark(item["query"]), 6),
                "q0_answer": answer,
                "q0_preserved": answer == expected,
                "new_queries": item["new_queries"],
                "loss": item["loss"],
                "reconstruction": item["reconstruction"],
            }
        )

    print(json.dumps({
        "source": str(SOURCE),
        "events": str(EVENTS),
        "event_count": len(events),
        "expected_q0": expected,
        "temporal_q_at_025": query_active(temporal, 0.25),
        "temporal_q_at_075": query_active(temporal, 0.75),
        "temporal_control_q_at_025": query_active(temporal_control, 0.25),
        "temporal_control_q_at_075": query_active(temporal_control, 0.75),
        "representations": results,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
