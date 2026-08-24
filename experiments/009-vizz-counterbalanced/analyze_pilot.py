"""Analyze one counterbalanced VIZZ export without fabricating human data."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
SOURCE = ROOT / "trial_sets.json"
CONDITIONS = {"table", "static-graph", "vizz-candidate"}


def fail(message: str) -> None:
    raise SystemExit(f"BALANCED_RESULTS_INVALID: {message}")


def signature(branches: list[dict[str, Any]]) -> str:
    payload = json.dumps(branches, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def state() -> dict[str, Any]:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def validate(payload: dict[str, Any], fixture: dict[str, Any]) -> None:
    if payload.get("schema") != "farmaxia:vizz-pilot:0.2":
        fail("unsupported schema")
    sets = {item["id"]: item for item in fixture["sets"]}
    signatures = {set_id: signature(item["branches"]) for set_id, item in sets.items()}
    records = payload.get("records")
    plan = payload.get("plan")
    if not isinstance(records, list) or len(records) != 3 or not isinstance(plan, list) or len(plan) != 3:
        fail("expected three records and three plan items")
    if {item.get("condition") for item in records} != CONDITIONS:
        fail("conditions are missing or duplicated")
    if {item.get("set_id") for item in records} != set(sets):
        fail("sets are missing or duplicated")
    if not isinstance(payload.get("assignment_index"), int) or not 0 <= payload["assignment_index"] < 3:
        fail("invalid assignment index")
    seen_order = set()
    for index, (record, item) in enumerate(zip(records, plan)):
        if record.get("order_index") != index or item.get("order_index") != index:
            fail("order index mismatch")
        if record.get("condition") != item.get("condition") or record.get("set_id") != item.get("set_id"):
            fail("record and plan mismatch")
        if record["set_id"] in seen_order:
            fail("repeated set")
        seen_order.add(record["set_id"])
        if record.get("set_signature") != signatures.get(record["set_id"]):
            fail("set signature mismatch")
        if record.get("choice") not in {branch["id"] for branch in sets[record["set_id"]]["branches"]}:
            fail("invalid choice")
        if not isinstance(record.get("duration_ms"), (int, float)) or record["duration_ms"] < 0:
            fail("invalid duration")
        if not isinstance(record.get("confidence"), (int, float)) or not 0 <= record["confidence"] <= 100:
            fail("invalid confidence")
        if not isinstance(record.get("detected_uncertainty"), bool):
            fail("invalid uncertainty flag")
        if not isinstance(record.get("explanation"), str) or not record["explanation"].strip():
            fail("missing explanation")


def summarize(payload: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    reference = fixture["evaluation_rule"]["correct_action"]
    by_condition = {}
    for condition in sorted(CONDITIONS):
        record = next(item for item in payload["records"] if item["condition"] == condition)
        correct = record["choice"] == reference
        confidence = record["confidence"] / 100
        by_condition[condition] = {
            "set_id": record["set_id"],
            "duration_ms": record["duration_ms"],
            "accuracy_against_declared_rule": int(correct),
            "confidence": confidence,
            "calibration_error": round(abs(confidence - int(correct)), 6),
            "detected_uncertainty": record["detected_uncertainty"],
            "explanation_characters": len(record["explanation"]),
        }
    return {
        "schema": "farmaxia:vizz-pilot-analysis:0.2",
        "participant": payload.get("participant", "anonymous"),
        "assignment_index": payload["assignment_index"],
        "by_condition": by_condition,
        "human_authority_note": "Accuracy is measured against a declared analytic task, not artistic value.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.input is None or not args.input.is_file():
        print("NO_HUMAN_DATA")
        print("No metrics computed; provide the JSON exported by the counterbalanced pilot.")
        return
    fixture = state()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    validate(payload, fixture)
    rendered = json.dumps(summarize(payload, fixture), indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
