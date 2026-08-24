"""Compare controlled representation losses using only the standard library."""

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
    regions: list[dict[str, Any]] = []
    for element in root:
        if element.tag != f"{SVG_NS}rect" or element.attrib.get("id") == "court":
            continue
        regions.append({
            "id": element.attrib["id"],
            "tag": element.tag.rsplit("}", 1)[-1],
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


def scan(rows: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool]) -> tuple[list[str], int]:
    answers: list[str] = []
    work = 0
    for row in rows:
        work += 1
        if predicate(row):
            answers.append(row["id"])
    return answers, work


def build_representations(regions: list[dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    geometry_rows = [
        {key: region[key] for key in ("id", "x", "y", "width", "height")}
        for region in regions
    ]
    attribute_rows = [dict(region) for region in regions]
    indexed_rows = [dict(region) for region in regions]
    return {
        "source": {"kind": "svg_source", "rows": regions},
        "geometry-table": {"kind": "geometry_table", "rows": geometry_rows},
        "attribute-table": {"kind": "attribute_table", "rows": attribute_rows},
        "indexed-table": {
            "kind": "indexed_geometry_table",
            "rows": indexed_rows,
            "indexes": {
                "center": [row["id"] for row in indexed_rows if intersects(row)],
                "red": [row["id"] for row in indexed_rows if row["stroke"] == "red"],
            },
        },
        "relation-graph": {
            "kind": "relation_graph",
            "nodes": [{"id": region["id"]} for region in regions],
            "edges": [{"from": region["id"], "to": "center-line", "relation": "intersects"}
                      for region in regions if intersects(region)],
        },
        "attributed-graph": {
            "kind": "attributed_relation_graph",
            "nodes": [{key: region[key] for key in ("id", "x", "y", "width", "height")} for region in regions],
            "edges": [{"from": region["id"], "to": "center-line", "relation": "intersects"}
                      for region in regions if intersects(region)],
        },
        "temporal-state": {
            "kind": "temporal_state_with_external_input",
            "rows": [dict(region) for region in regions],
            "events": events,
        },
    }


def query(name: str, representation: dict[str, Any], query_name: str) -> tuple[list[str], int] | None:
    if name == "indexed-table":
        if query_name == "q-spatial":
            return representation["indexes"]["center"], 1
        if query_name == "q-style":
            return representation["indexes"]["red"], 1

    if name in {"relation-graph", "attributed-graph"} and query_name == "q-relation":
        edges = representation["edges"]
        return [edge["from"] for edge in edges], len(edges)

    if name == "temporal-state" and query_name == "q-temporal":
        active = {event["region"] for event in representation["events"]
                  if event["event"] == "enter" and event["time"] <= 0.75}
        active -= {event["region"] for event in representation["events"]
                   if event["event"] == "exit" and event["time"] <= 0.75}
        return sorted(active), len(representation["events"])

    rows = representation.get("rows")
    if name == "attributed-graph":
        rows = representation.get("nodes")
    if not isinstance(rows, list):
        return None
    predicates: dict[str, Callable[[dict[str, Any]], bool]] = {
        "q-spatial": intersects,
        "q-area": lambda row: row["width"] * row["height"] >= 8000,
        "q-style": lambda row: row.get("stroke") == "red",
        "q-tag": lambda row: row.get("tag") == "rect",
    }
    predicate = predicates.get(query_name)
    if predicate is None:
        return None
    required = {
        "q-spatial": {"x", "width"},
        "q-area": {"width", "height"},
        "q-style": {"stroke"},
        "q-tag": {"tag"},
    }[query_name]
    if any(required_item not in rows[0] for required_item in required):
        return None
    return scan(rows, predicate)


def serialized_size(value: Any) -> int:
    return len(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def main() -> None:
    regions = load_regions()
    events = load_events()
    representations = build_representations(regions, events)
    queries = ["q-spatial", "q-area", "q-style", "q-tag", "q-relation", "q-temporal"]
    workloads = {
        "single-spatial": ["q-spatial"],
        "repeat-spatial": ["q-spatial"] * 20,
        "style-heavy": ["q-style"] * 12,
        "mixed-static": ["q-spatial", "q-area", "q-style", "q-tag", "q-relation"],
        "temporal": ["q-temporal"],
    }
    setup = {
        "source": len(regions) + 4,
        "geometry-table": len(regions) * 5,
        "attribute-table": len(regions) * 7,
        "indexed-table": len(regions) * 8 + 2,
        "relation-graph": len(regions) + 2,
        "attributed-graph": len(regions) * 5 + 2,
        "temporal-state": len(regions) * 7 + len(events),
    }
    residue = {
        "source": [],
        "geometry-table": ["style", "SVG tags", "SVG syntax"],
        "attribute-table": ["SVG syntax"],
        "indexed-table": ["SVG syntax", "index maintenance and invalidation"],
        "relation-graph": ["coordinates", "dimensions", "style", "tags", "arbitrary geometry"],
        "attributed-graph": ["style", "tags", "SVG syntax", "continuous geometry beyond bounding boxes"],
        "temporal-state": ["SVG syntax"],
    }
    classification = {
        "source": "baseline",
        "geometry-table": "representation-loss",
        "attribute-table": "representation-loss-with-attributes",
        "indexed-table": "known-index-or-materialized-view-control",
        "relation-graph": "lossy-relation-cache-control",
        "attributed-graph": "lossy-graph-with-geometric-summary",
        "temporal-state": "X-ANA-X-candidate-with-external-input",
    }
    report: list[dict[str, Any]] = []
    for name, representation in representations.items():
        query_report: dict[str, Any] = {}
        unavailable: list[str] = []
        for query_name in queries:
            result = query(name, representation, query_name)
            if result is None:
                unavailable.append(query_name)
                query_report[query_name] = {"status": "unavailable"}
            else:
                answers, work = result
                query_report[query_name] = {"status": "available", "answers": answers, "work_units": work}
        workload_report: dict[str, Any] = {}
        for workload_name, workload_queries in workloads.items():
            results = [query(name, representation, query_name) for query_name in workload_queries]
            if any(result is None for result in results):
                workload_report[workload_name] = {"status": "unavailable"}
            else:
                workload_report[workload_name] = {
                    "status": "available",
                    "total_work_units": setup[name] + sum(result[1] for result in results),
                }
        report.append({
            "representation": name,
            "classification": classification[name],
            "serialized_bytes": serialized_size(representation),
            "setup_work_units": setup[name],
            "queries": query_report,
            "unavailable_queries": unavailable,
            "workloads": workload_report,
            "residue": residue[name],
            "external_inputs": [str(SOURCE), str(EVENTS)] if name == "temporal-state" else [str(SOURCE)],
        })
    print(json.dumps({"source": str(SOURCE), "events": str(EVENTS), "queries": queries, "representations": report}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
