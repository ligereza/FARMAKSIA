"""Run metamorphic preservation and composition checks on synthetic cases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
CASES = ROOT / "cases.json"


def spatial(rows: list[dict[str, Any]], center_x: float) -> list[str]:
    return [row["id"] for row in rows if row["x"] <= center_x <= row["x"] + row["width"]]


def area(rows: list[dict[str, Any]], threshold: float) -> list[str]:
    return [row["id"] for row in rows if row["width"] * row["height"] >= threshold]


def style(rows: list[dict[str, Any]]) -> list[str]:
    return [row["id"] for row in rows if row.get("stroke") == "red"]


def temporal(rows: list[dict[str, Any]], events: list[dict[str, Any]] | None, center_x: float, at: float) -> list[str] | None:
    if events is None:
        return None
    active = {event["region"] for event in events if event["event"] == "enter" and event["time"] <= at}
    active -= {event["region"] for event in events if event["event"] == "exit" and event["time"] <= at}
    return [row["id"] for row in rows if row["id"] in active and row["x"] <= center_x <= row["x"] + row["width"]]


def check_case(case: dict[str, Any], center_x: float, at: float, threshold: float) -> dict[str, bool]:
    source = case["regions"]
    geometry_table = [{key: row[key] for key in ("id", "x", "y", "width", "height")} for row in source]
    indexed_table = {
        "rows": source,
        "center": spatial(source, center_x),
        "red": style(source),
    }
    relation_graph = {"nodes": [{"id": row["id"]} for row in source], "edges": spatial(source, center_x)}
    attributed_graph = {"nodes": geometry_table, "edges": spatial(source, center_x)}
    temporal_state = {"rows": source, "events": case["events"]}

    source_spatial = spatial(source, center_x)
    source_area = area(source, threshold)
    source_style = style(source)
    source_temporal = temporal(source, case["events"], center_x, at)
    x_after_k_graph = None
    k_graph_after_x = source_temporal
    return {
        "geometry_preserves_spatial": spatial(geometry_table, center_x) == source_spatial,
        "geometry_preserves_area": area(geometry_table, threshold) == source_area,
        "geometry_loses_style": all("stroke" not in row for row in geometry_table),
        "indexed_preserves_spatial": indexed_table["center"] == source_spatial,
        "indexed_preserves_style": indexed_table["red"] == source_style,
        "relation_preserves_relation": relation_graph["edges"] == source_spatial,
        "relation_lacks_area": "width" not in relation_graph["nodes"][0],
        "relation_lacks_style": "stroke" not in relation_graph["nodes"][0],
        "attributed_preserves_spatial": spatial(attributed_graph["nodes"], center_x) == source_spatial,
        "attributed_preserves_area": area(attributed_graph["nodes"], threshold) == source_area,
        "attributed_loses_style": "stroke" not in attributed_graph["nodes"][0],
        "temporal_preserves_external": temporal(temporal_state["rows"], temporal_state["events"], center_x, at) == source_temporal,
        "temporal_requires_events": temporal(source, None, center_x, at) is None,
        "graph_composition_noncommutes": k_graph_after_x != x_after_k_graph,
        "table_compositions_equivalent": source_temporal == temporal(geometry_table, case["events"], center_x, at),
    }


def main() -> None:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    cases = payload["cases"]
    property_names = list(check_case(cases[0], payload["center_x"], payload["time"], payload["area_threshold"]))
    totals = {name: 0 for name in property_names}
    violations = []
    for case in cases:
        checks = check_case(case, payload["center_x"], payload["time"], payload["area_threshold"])
        for name, passed in checks.items():
            totals[name] += int(passed)
            if not passed:
                violations.append({"case": case["id"], "property": name})
    print(json.dumps({
        "case_count": len(cases),
        "seed": payload["seed"],
        "property_pass_counts": totals,
        "violations": violations,
        "all_properties_hold": not violations,
        "scope_limit": "synthetic axis-aligned rectangles only; not a creative corpus",
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
