"""Factorize X-ANA-X inputs, questions, observables, and representations."""

from __future__ import annotations

import hashlib
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
    return [
        {
            "id": element.attrib["id"],
            "x": float(element.attrib["x"]),
            "y": float(element.attrib["y"]),
            "width": float(element.attrib["width"]),
            "height": float(element.attrib["height"]),
        }
        for element in root
        if element.tag == f"{SVG_NS}rect" and element.attrib.get("id") != "court"
    ]


def load_events() -> list[dict[str, Any]]:
    return json.loads(EVENTS.read_text(encoding="utf-8"))


def spatial(rows: list[dict[str, Any]]) -> list[str]:
    return [row["id"] for row in rows if row["x"] <= CENTER_X <= row["x"] + row["width"]]


def area(rows: list[dict[str, Any]]) -> list[str]:
    return [row["id"] for row in rows if row["width"] * row["height"] >= 8000]


def temporal(rows: list[dict[str, Any]], events: list[dict[str, Any]] | None, at: float = 0.25) -> list[str] | None:
    if events is None:
        return None
    active = {event["region"] for event in events if event["event"] == "enter" and event["time"] <= at}
    active -= {event["region"] for event in events if event["event"] == "exit" and event["time"] <= at}
    return sorted(row["id"] for row in rows if row["id"] in active and row["x"] <= CENTER_X <= row["x"] + row["width"])


def contract_signature(contract: dict[str, Any]) -> str:
    canonical = json.dumps(contract, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest().upper()


def evaluate(path: dict[str, Any], rows: list[dict[str, Any]], events: list[dict[str, Any]] | None) -> dict[str, Any]:
    question = path["question"]
    if question == "q-spatial":
        answers: list[str] | None = spatial(rows)
    elif question == "q-area":
        answers = area(rows)
    elif question == "q-temporal":
        answers = temporal(rows, events)
    else:
        raise ValueError(f"unknown question: {question}")
    contract = {
        "path": path["id"],
        "operation": path["operation"],
        "input_entities": path["input_entities"],
        "question": question,
        "observable": path["observable"],
        "representation": path["representation"],
        "authority": path["authority"],
    }
    result = {
        **contract,
        "contract_signature": contract_signature(contract),
        "status": "available" if answers is not None else "unavailable",
        "answers": answers,
    }
    if answers is None:
        result["reason"] = "events.json is required for the temporal observable"
    return result


def main() -> None:
    rows = load_regions()
    events = load_events()
    paths = [
        {"id": "baseline-static", "operation": "none", "input_entities": ["svg"], "question": "q-spatial", "observable": "static-intersection", "representation": "svg-source", "authority": "human_declared"},
        {"id": "K_table-static", "operation": "KETAMINE", "input_entities": ["svg"], "question": "q-spatial", "observable": "static-intersection", "representation": "geometry-table", "authority": "human_declared"},
        {"id": "X_query-area", "operation": "X-ANA-X", "input_entities": ["svg"], "question": "q-area", "observable": "area-threshold", "representation": "svg-source", "authority": "human_declared"},
        {"id": "X_external-temporal", "operation": "X-ANA-X", "input_entities": ["svg", "events"], "question": "q-temporal", "observable": "active-intersection-at-t-0.25", "representation": "external-augmented-source", "authority": "human_declared_plus_external_input"},
        {"id": "X_without-external", "operation": "X-ANA-X", "input_entities": ["svg"], "question": "q-temporal", "observable": "active-intersection-at-t-0.25", "representation": "svg-source", "authority": "human_declared"},
        {"id": "K_after_X-temporal", "operation": "KETAMINE_after_X-ANA-X", "input_entities": ["svg", "events"], "question": "q-temporal", "observable": "active-intersection-at-t-0.25", "representation": "temporal-table", "authority": "computed_plus_external_input"},
        {"id": "K_encoded-temporal", "operation": "KETAMINE_with_external_materialization", "input_entities": ["svg", "events"], "question": "q-temporal", "observable": "active-intersection-at-t-0.25", "representation": "temporal-index", "authority": "computed_plus_external_input"},
    ]
    results = []
    for path in paths:
        path_events = events if "events" in path["input_entities"] else None
        result = evaluate(path, rows, path_events)
        if path["id"] == "K_after_X-temporal" or path["id"] == "K_encoded-temporal":
            result["answers"] = temporal(rows, events)
            result["status"] = "available"
        results.append(result)
    same_answer = [result["path"] for result in results if result["answers"] == ["left-region"]]
    print(json.dumps({
        "paths": results,
        "same_answer_paths": same_answer,
        "kill_tests": {
            "temporal_without_events": next(result["status"] for result in results if result["path"] == "X_without-external"),
            "pure_k_temporal": "not_demonstrated",
            "contract_signatures_distinguish_same_answers": len({result["contract_signature"] for result in results if result["answers"] == ["left-region"]}) > 1,
        },
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
