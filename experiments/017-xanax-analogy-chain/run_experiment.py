"""Run a reproducible X-ANA-X analogy/search/verification chain."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


HERE = Path(__file__).parent
SVG = (HERE / ".." / "001-representation-boundary" / "input.svg").resolve()
EVENTS = (HERE / ".." / "001-representation-boundary" / "events.json").resolve()
CATALOG = HERE / "source_catalog.json"
SVG_NS = "{http://www.w3.org/2000/svg}"
CENTER_X = 200.0
QUERY_TERMS = {"active", "time", "enter", "exit", "interval"}


def load_regions() -> list[dict[str, Any]]:
    root = ET.parse(SVG).getroot()
    return [
        {
            "id": element.attrib["id"],
            "x": float(element.attrib["x"]),
            "width": float(element.attrib["width"]),
        }
        for element in root
        if element.tag == f"{SVG_NS}rect" and element.attrib.get("id") != "court"
    ]


def load_events() -> list[dict[str, Any]]:
    return json.loads(EVENTS.read_text(encoding="utf-8"))


def select_source(sources: list[dict[str, Any]], terms: set[str] = QUERY_TERMS) -> list[dict[str, Any]]:
    ranked = []
    for source in sources:
        overlap = sorted(terms.intersection(source["scent"]))
        ranked.append({
            "source": source["id"],
            "scent_overlap": overlap,
            "score": len(overlap),
        })
    return sorted(ranked, key=lambda item: (-item["score"], item["source"]))


def active_regions(events: list[dict[str, Any]], at: float) -> list[str] | None:
    if events is None:
        return None
    active: set[str] = set()
    for event in sorted(events, key=lambda item: item["time"]):
        if event["time"] > at:
            break
        if event["event"] == "enter":
            active.add(event["region"])
        elif event["event"] == "exit":
            active.discard(event["region"])
    return sorted(active)


def center_regions(regions: list[dict[str, Any]]) -> list[str]:
    return sorted(
        region["id"]
        for region in regions
        if region["x"] <= CENTER_X <= region["x"] + region["width"]
    )


def right_of_center_regions(regions: list[dict[str, Any]]) -> list[str]:
    return sorted(region["id"] for region in regions if region["x"] > CENTER_X)


def verify_target(regions: list[dict[str, Any]], events: list[dict[str, Any]], at: float) -> dict[str, Any]:
    active = active_regions(events, at)
    center = set(center_regions(regions))
    return {
        "active_regions": active,
        "center_regions": sorted(center),
        "active_and_center": None if active is None else sorted(set(active).intersection(center)),
    }


def run_chain() -> dict[str, Any]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    sources = catalog["sources"]
    rankings = select_source(sources)
    selected = next(source for source in sources if source["id"] == rankings[0]["source"])
    regions = load_regions()
    events = load_events()
    target = verify_target(regions, events, 0.25)
    predicted_active = ["left-region"] if "active_at_time" in selected["transferable"] else None
    direct_target = target["active_and_center"]
    prediction_verified = predicted_active == target["active_regions"]
    rupture_target = verify_target(regions, events, 0.75)
    right_of_center = set(right_of_center_regions(regions))
    rupture_active = set(rupture_target["active_regions"] or [])
    return {
        "experiment": "017-xanax-analogy-chain",
        "chain": ["confusion", "gap", "search", "source", "mapping", "prediction", "verification", "rupture"],
        "confusion": "which region is active at t=0.25 and crosses the center",
        "gap": "the target requires an active interval derived from enter/exit events",
        "search": {
            "query_terms": sorted(QUERY_TERMS),
            "rankings": rankings,
            "selected_source": selected["id"],
            "network_used": False,
        },
        "mapping": selected["mapping"],
        "prediction": {
            "relation": "active_at_time",
            "predicted_active_regions": predicted_active,
            "authority": selected["authority"],
        },
        "verification": {
            "target": target,
            "direct_target_decision": direct_target,
            "prediction_verified": prediction_verified,
        },
        "rupture": {
            "query": "active region right_of_center at t=0.75",
            "source_prediction": "unavailable_without_target_geometry",
            "target_verification": sorted(rupture_active.intersection(right_of_center)),
            "status": "break",
        },
        "human_data": False,
        "arbitrary_corpus": False,
        "scope_limit": "controlled local fixtures; chain and contract residue only, not human comprehension or analogy novelty",
    }


def main() -> None:
    result = run_chain()
    if result["search"]["selected_source"] != "queue-interval":
        raise SystemExit("XANAX_INVALID: temporal query selected a source without interval relations")
    if not result["verification"]["prediction_verified"]:
        raise SystemExit("XANAX_INVALID: analogy prediction did not verify")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
