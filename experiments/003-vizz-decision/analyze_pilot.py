"""Analyze exported VIZZ pilot JSON without fabricating human observations."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
SOURCE = ROOT / "decision-state.json"
EXPECTED_CONDITIONS = {"table", "static-graph", "vizz-candidate"}


def fail(message: str) -> None:
    raise SystemExit(f"PILOT_RESULTS_INVALID: {message}")


def source_signature(state: dict[str, Any]) -> str:
    branches = sorted(state["branches"], key=lambda branch: branch["id"])
    payload = json.dumps(branches, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def validate(payload: dict[str, Any], state: dict[str, Any]) -> None:
    if payload.get("schema") != "farmaxia:vizz-pilot:0.1":
        fail("unsupported schema")
    records = payload.get("records")
    if not isinstance(records, list) or len(records) != 3:
        fail("expected exactly three trial records")
    if set(record.get("condition") for record in records) != EXPECTED_CONDITIONS:
        fail("conditions are missing or duplicated")
    order = payload.get("order")
    if not isinstance(order, list) or set(order) != EXPECTED_CONDITIONS or len(order) != 3:
        fail("order must contain each condition exactly once")
    expected_signature = source_signature(state)
    if payload.get("data_signature") != expected_signature:
        fail("data signature does not match the fixture")
    allowed_choices = {branch["id"] for branch in state["branches"]}
    for record in records:
        order_index = record.get("order_index")
        if not isinstance(order_index, int) or not 0 <= order_index < len(order):
            fail(f"invalid order index in {record.get('condition')}")
        if record.get("condition") != order[order_index]:
            fail(f"condition/order mismatch in {record.get('condition')}")
        if record.get("data_signature") != expected_signature:
            fail(f"signature mismatch in {record.get('condition')}")
        if record.get("choice") not in allowed_choices:
            fail(f"invalid choice in {record.get('condition')}")
        if not isinstance(record.get("duration_ms"), (int, float)) or record["duration_ms"] < 0:
            fail(f"invalid duration in {record.get('condition')}")
        if not isinstance(record.get("confidence"), (int, float)) or not 0 <= record["confidence"] <= 100:
            fail(f"invalid confidence in {record.get('condition')}")
        if not isinstance(record.get("explanation"), str) or not record["explanation"].strip():
            fail(f"missing explanation in {record.get('condition')}")
        if not isinstance(record.get("detected_uncertainty"), bool):
            fail(f"invalid uncertainty flag in {record.get('condition')}")


def summarize(payload: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    reference = state["evaluation_rule"]["correct_action_for_pilot"]
    by_condition = {}
    for condition in sorted(EXPECTED_CONDITIONS):
        records = [record for record in payload["records"] if record["condition"] == condition]
        accurate = [record["choice"] == reference for record in records]
        confidences = [record["confidence"] / 100 for record in records]
        by_condition[condition] = {
            "n": len(records),
            "mean_duration_ms": round(statistics.mean(record["duration_ms"] for record in records), 3),
            "accuracy_against_declared_rule": round(statistics.mean(accurate), 6),
            "mean_confidence": round(statistics.mean(confidences), 6),
            "mean_calibration_error": round(statistics.mean(abs(confidence - int(correct)) for confidence, correct in zip(confidences, accurate)), 6),
            "uncertainty_detection_rate": round(statistics.mean(record["detected_uncertainty"] for record in records), 6),
            "mean_explanation_characters": round(statistics.mean(len(record["explanation"]) for record in records), 3),
        }
    return {
        "schema": "farmaxia:vizz-pilot-analysis:0.1",
        "participant": payload.get("participant", "anonymous"),
        "source_signature": source_signature(state),
        "reference_rule": state["evaluation_rule"],
        "by_condition": by_condition,
        "human_authority_note": "Accuracy is measured against a declared analytic task, not artistic value.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, help="exported JSON from pilot.html")
    parser.add_argument("--output", type=Path, help="optional analysis JSON path")
    args = parser.parse_args()
    if args.input is None or not args.input.is_file():
        print("NO_HUMAN_DATA")
        print("No metrics computed; provide the JSON exported by pilot.html.")
        return

    state = json.loads(SOURCE.read_text(encoding="utf-8"))
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    validate(payload, state)
    analysis = summarize(payload, state)
    rendered = json.dumps(analysis, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
