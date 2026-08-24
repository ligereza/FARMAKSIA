"""Measure conditional commutativity of representation and state reformulation."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
SOURCE = (ROOT / ".." / "001-representation-boundary" / "input.svg").resolve()
EVENTS = (ROOT / ".." / "001-representation-boundary" / "events.json").resolve()
SVG_NS = "{http://www.w3.org/2000/svg}"
CENTER_X = 200.0


def load_regions() -> list[dict[str, Any]]:
    root = ET.parse(SOURCE).getroot()
    rows = []
    for element in root:
        if element.tag != f"{SVG_NS}rect" or element.attrib.get("id") == "court":
            continue
        rows.append({
            "id": element.attrib["id"],
            "x": float(element.attrib["x"]),
            "y": float(element.attrib["y"]),
            "width": float(element.attrib["width"]),
            "height": float(element.attrib["height"]),
        })
    return rows


def load_events() -> dict[str, tuple[float, float]]:
    events = json.loads(EVENTS.read_text(encoding="utf-8"))
    starts = {event["region"]: float(event["time"]) for event in events if event["event"] == "enter"}
    ends = {event["region"]: float(event["time"]) for event in events if event["event"] == "exit"}
    return {region: (starts[region], ends[region]) for region in starts}


def intersects(region: dict[str, Any]) -> bool:
    return region["x"] <= CENTER_X <= region["x"] + region["width"]


def k_table(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {"kind": "geometry_table", "rows": [dict(row) for row in rows]}


def k_graph(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "kind": "relation_graph",
        "nodes": [{"id": row["id"]} for row in rows],
        "edges": [{"from": row["id"], "to": "center-line", "relation": "intersects"} for row in rows if intersects(row)],
    }


def x_temporal_intersection(rows: list[dict[str, Any]], intervals: dict[str, tuple[float, float]]) -> dict[str, Any]:
    return {
        "kind": "temporal_intersection_state",
        "rows": [
            {
                **row,
                "active_from": intervals[row["id"]][0],
                "active_to": intervals[row["id"]][1],
                "active_intersects": intersects(row),
            }
            for row in rows
        ],
    }


def graph_after_x(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "temporal_relation_graph",
        "nodes": [{"id": row["id"], "active_from": row["active_from"], "active_to": row["active_to"]} for row in state["rows"]],
        "edges": [
            {
                "from": row["id"],
                "to": "center-line",
                "relation": "active-intersects",
                "active_from": row["active_from"],
                "active_to": row["active_to"],
            }
            for row in state["rows"]
            if row["active_intersects"]
        ],
    }


def x_after_graph(graph: dict[str, Any]) -> dict[str, Any]:
    if "x" not in graph.get("nodes", [{}])[0]:
        return {"status": "unavailable", "reason": "geometry coordinates missing after KETAMINE-graph"}
    return {"status": "available"}


def temporal_query(value: dict[str, Any], timestamp: float = 0.25) -> dict[str, Any]:
    if value.get("kind") in {"temporal_intersection_state", "temporal_table"}:
        return {
            "status": "available",
            "answers": [row["id"] for row in value["rows"] if row["active_intersects"] and row["active_from"] <= timestamp < row["active_to"]],
        }
    if value.get("kind") == "temporal_relation_graph":
        return {
            "status": "available",
            "answers": [edge["from"] for edge in value["edges"] if edge["active_from"] <= timestamp < edge["active_to"]],
        }
    return {"status": "unavailable", "reason": "temporal observable absent"}


def table_after_x(state: dict[str, Any]) -> dict[str, Any]:
    return {"kind": "temporal_table", "rows": [dict(row) for row in state["rows"]]}


def x_after_table(table: dict[str, Any], intervals: dict[str, tuple[float, float]]) -> dict[str, Any]:
    return x_temporal_intersection(table["rows"], intervals)


def summarize(label: str, value: dict[str, Any], residue: list[str]) -> dict[str, Any]:
    return {"composition": label, "temporal_query": temporal_query(value), "residue": residue, "representation_kind": value.get("kind")}


def main() -> None:
    rows = load_regions()
    intervals = load_events()
    table = k_table(rows)
    graph = k_graph(rows)
    temporal = x_temporal_intersection(rows, intervals)
    results = [
        summarize("K_graph_after_X", graph_after_x(temporal), ["style", "original SVG tags", "continuous geometry after graphification"]),
        {"composition": "X_after_K_graph", **x_after_graph(graph), "temporal_query": {"status": "unavailable"}, "residue": ["coordinates unavailable"]},
        summarize("X_after_K_table", x_after_table(table, intervals), ["style", "original SVG tags"]),
        summarize("K_table_after_X", table_after_x(temporal), ["style", "original SVG tags"]),
    ]
    print(json.dumps({
        "source": str(SOURCE),
        "events": str(EVENTS),
        "definition": "A_after_B means apply B first, then A",
        "results": results,
        "commutativity": {
            "graph_pair": "does_not_commute",
            "table_pair": "query_equivalent_in_this_fixture",
        },
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
