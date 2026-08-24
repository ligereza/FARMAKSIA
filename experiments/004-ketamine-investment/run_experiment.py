"""Measure query-specific representation investment without external packages."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).parent
SOURCE = (ROOT / ".." / "001-representation-boundary" / "input.svg").resolve()
EVENTS = (ROOT / ".." / "001-representation-boundary" / "events.json").resolve()
SVG_NS = "{http://www.w3.org/2000/svg}"
CENTER_X = 200.0


def load_regions() -> list[dict[str, Any]]:
    root = ET.parse(SOURCE).getroot()
    regions = []
    for element in root:
        if element.tag != f"{SVG_NS}rect" or element.attrib.get("id") == "court":
            continue
        regions.append({
            "id": element.attrib["id"],
            "x": float(element.attrib["x"]),
            "y": float(element.attrib["y"]),
            "width": float(element.attrib["width"]),
            "height": float(element.attrib["height"]),
            "stroke": element.attrib.get("stroke", ""),
        })
    return regions


def load_events() -> list[dict[str, Any]]:
    return json.loads(EVENTS.read_text(encoding="utf-8"))


def intersects(region: dict[str, Any]) -> bool:
    return region["x"] <= CENTER_X <= region["x"] + region["width"]


def query_scan(regions: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool]) -> tuple[list[str], int]:
    answers = []
    work = 0
    for region in regions:
        work += 1
        if predicate(region):
            answers.append(region["id"])
    return answers, work


def build_table(regions: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "kind": "geometry_table",
        "rows": [{key: region[key] for key in ("id", "x", "y", "width", "height")} for region in regions],
    }


def build_indexed_table(regions: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [dict(region) for region in regions]
    return {
        "kind": "indexed_geometry_table",
        "rows": rows,
        "indexes": {
            "by_stroke": {
                stroke: [region["id"] for region in rows if region["stroke"] == stroke]
                for stroke in sorted({region["stroke"] for region in rows})
            },
            "center_intersections": [region["id"] for region in rows if intersects(region)],
        },
    }


def build_graph(regions: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "kind": "relation_graph",
        "nodes": [{"id": region["id"]} for region in regions],
        "edges": [{"from": region["id"], "to": "center-line", "relation": "intersects"} for region in regions if intersects(region)],
    }


def build_temporal(regions: list[dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, Any]:
    starts = {event["region"]: event["time"] for event in events if event["event"] == "enter"}
    ends = {event["region"]: event["time"] for event in events if event["event"] == "exit"}
    return {
        "kind": "temporal_geometry",
        "rows": [
            {**region, "active_from": starts[region["id"]], "active_to": ends[region["id"]]}
            for region in regions
        ],
    }


def query_representation(name: str, representation: dict[str, Any], query: str) -> tuple[list[str], int] | None:
    if name == "geometry-table" and query == "q2":
        return None
    if name in {"svg-source", "geometry-table", "temporal-state"}:
        rows = representation["rows"]
        predicates = {
            "q0": intersects,
            "q1": lambda region: region["width"] * region["height"] >= 8000,
            "q2": lambda region: region.get("stroke") == "red",
            "q3": intersects,
        }
        if query in predicates:
            return query_scan(rows, predicates[query])
        if name == "temporal-state" and query == "q-time":
            return query_scan(rows, lambda region: float(region["active_from"]) <= 0.25 < float(region["active_to"]))
    if name == "indexed-table":
        if query in {"q0", "q3"}:
            return representation["indexes"]["center_intersections"], 1
        if query == "q2":
            return representation["indexes"]["by_stroke"].get("red", []), 1
        if query == "q1":
            return query_scan(representation["rows"], lambda region: region["width"] * region["height"] >= 8000)
    if name == "relation-graph" and query in {"q0", "q3"}:
        answers = [edge["from"] for edge in representation["edges"] if edge["relation"] == "intersects"]
        return answers, len(representation["edges"])
    return None


def serialized_size(value: Any) -> int:
    return len(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def main() -> None:
    regions = load_regions()
    events = load_events()
    representations = {
        "svg-source": {"kind": "svg_source", "rows": regions},
        "geometry-table": build_table(regions),
        "indexed-table": build_indexed_table(regions),
        "relation-graph": build_graph(regions),
        "temporal-state": build_temporal(regions, events),
    }
    setup_units = {
        "svg-source": len(regions) + 2,
        "geometry-table": len(regions) * 5,
        "indexed-table": len(regions) * 6 + 2,
        "relation-graph": len(regions) + len(build_graph(regions)["edges"]),
        "temporal-state": len(regions) + len(events),
    }
    external_inputs = {
        "svg-source": [str(SOURCE)],
        "geometry-table": [str(SOURCE)],
        "indexed-table": [str(SOURCE)],
        "relation-graph": [str(SOURCE)],
        "temporal-state": [str(SOURCE), str(EVENTS)],
    }
    residue = {
        "svg-source": [],
        "geometry-table": ["style and original SVG tags"],
        "indexed-table": ["original SVG tags; indexes are workload-specific materializations"],
        "relation-graph": ["coordinates, dimensions, arbitrary geometric predicates"],
        "temporal-state": ["time is external to SVG and is not preserved by conversion alone"],
    }
    queries = ["q0", "q1", "q2", "q3", "q-time"]
    workloads = {
        "spatial-core": ["q0", "q1", "q3"],
        "relation-heavy": ["q0", "q3", "q0", "q3", "q0", "q3"],
        "repeat-indexed": ["q0", "q2", "q3"] * 6,
        "style-heavy": ["q2"] * 12,
        "full-mixed": queries,
    }
    classification = {
        "svg-source": "baseline",
        "geometry-table": "KETAMINE-candidate",
        "indexed-table": "KETAMINE-existing-index-materialized-view",
        "relation-graph": "KETAMINE-or-cache-boundary",
        "temporal-state": "X-ANA-X-candidate-with-external-input",
    }
    report = []
    for name, representation in representations.items():
        query_report = {}
        query_units = 0
        unavailable = []
        for query in queries:
            result = query_representation(name, representation, query)
            if result is None:
                unavailable.append(query)
                query_report[query] = {"status": "unavailable"}
            else:
                answers, work = result
                query_units += work
                query_report[query] = {"status": "available", "answers": answers, "work_units": work}
        workload_costs = {}
        for workload_name, workload_queries in workloads.items():
            workload_results = [query_representation(name, representation, query) for query in workload_queries]
            if any(result is None for result in workload_results):
                workload_costs[workload_name] = {"status": "unavailable"}
            else:
                workload_costs[workload_name] = {
                    "status": "available",
                    "total_work_units": setup_units[name] + sum(result[1] for result in workload_results),
                }
        report.append({
            "representation": name,
            "classification": classification[name],
            "serialized_bytes": serialized_size(representation),
            "setup_work_units": setup_units[name],
            "query_work_units_available": query_units,
            "workload_total_if_available": None if unavailable else setup_units[name] + query_units,
            "unavailable_queries": unavailable,
            "queries": query_report,
            "workloads": workload_costs,
            "external_inputs": external_inputs[name],
            "residue": residue[name],
            "reversibility": "full_for_source_rows" if name == "svg-source" else "query_specific",
        })
    print(json.dumps({"source": str(SOURCE), "events": str(EVENTS), "workload": queries, "representations": report}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
