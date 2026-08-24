"""Aggregate validated VIZZ 0.2 exports without making causal claims."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from analyze_pilot import state, validate


def fail(message: str) -> None:
    raise SystemExit(f"BALANCED_AGGREGATE_INVALID: {message}")


def collect_inputs(paths: list[Path], directory: Path | None) -> list[Path]:
    collected = list(paths)
    if directory is not None:
        collected.extend(sorted(directory.glob("*.json")))
    unique = sorted({path.resolve() for path in collected})
    return [path for path in unique if path.is_file()]


def mean(values: list[float]) -> float:
    return round(statistics.mean(values), 6) if values else 0.0


def summarize(payloads: list[dict[str, Any]], fixture: dict[str, Any]) -> dict[str, Any]:
    reference = fixture["evaluation_rule"]["correct_action"]
    condition_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    assignment_counts: Counter[str] = Counter()
    order_counts: Counter[str] = Counter()
    participants = []
    for payload in payloads:
        participant = payload.get("participant")
        participants.append(participant)
        for record in payload["records"]:
            record = {**record, "participant": participant}
            condition_records[record["condition"]].append(record)
            assignment_counts[f"{record['condition']}::{record['set_id']}"] += 1
            order_counts[f"{record['condition']}::{record['order_index']}"] += 1

    assignment_values = list(assignment_counts.values())
    balance_status = "BALANCED_DESIGN" if assignment_values and len(set(assignment_values)) == 1 else "UNBALANCED_DESIGN"
    by_condition = {}
    for condition in sorted(condition_records):
        records = condition_records[condition]
        correct = [record["choice"] == reference for record in records]
        confidence = [record["confidence"] / 100 for record in records]
        by_condition[condition] = {
            "n": len(records),
            "mean_duration_ms": mean([record["duration_ms"] for record in records]),
            "accuracy_against_declared_rule": mean([int(value) for value in correct]),
            "mean_confidence": mean(confidence),
            "mean_calibration_error": mean([abs(value - int(is_correct)) for value, is_correct in zip(confidence, correct)]),
            "uncertainty_detection_rate": mean([int(record["detected_uncertainty"]) for record in records]),
            "mean_explanation_characters": mean([len(record["explanation"]) for record in records]),
        }

    paired_deltas = {}
    by_participant = defaultdict(dict)
    for payload in payloads:
        for record in payload["records"]:
            by_participant[payload["participant"]][record["condition"]] = record
    for condition in sorted(set(condition_records) - {"static-graph"}):
        duration_deltas = []
        accuracy_deltas = []
        for records in by_participant.values():
            if condition not in records or "static-graph" not in records:
                continue
            duration_deltas.append(records[condition]["duration_ms"] - records["static-graph"]["duration_ms"])
            accuracy_deltas.append(int(records[condition]["choice"] == reference) - int(records["static-graph"]["choice"] == reference))
        paired_deltas[condition] = {
            "n_pairs": len(duration_deltas),
            "mean_duration_delta_ms_vs_static": mean(duration_deltas),
            "mean_accuracy_delta_vs_static": mean(accuracy_deltas),
        }

    return {
        "schema": "farmaxia:vizz-pilot-aggregate:0.1",
        "participant_count": len(payloads),
        "participants": participants,
        "balance_status": balance_status,
        "assignment_counts": dict(sorted(assignment_counts.items())),
        "order_counts": dict(sorted(order_counts.items())),
        "by_condition": by_condition,
        "paired_deltas_vs_static": paired_deltas,
        "inference_status": "DESCRIPTIVE_ONLY",
        "human_authority_note": "Accuracy is measured against a declared analytic task, not artistic value; no causal conclusion is emitted automatically.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", type=Path)
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    files = collect_inputs(args.inputs, args.directory)
    if not files:
        print("NO_HUMAN_DATA")
        print("No aggregate metrics computed; provide one or more exported pilot JSON files.")
        return
    fixture = state()
    payloads = []
    participant_ids = set()
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail(f"cannot read {path}: {exc}")
        validate(payload, fixture)
        participant = payload.get("participant")
        if not isinstance(participant, str) or not participant.strip() or participant == "anonymous":
            fail(f"{path.name}: explicit non-anonymous participant code required for aggregation")
        if participant in participant_ids:
            fail(f"duplicate participant code: {participant}")
        participant_ids.add(participant)
        payloads.append(payload)
    rendered = json.dumps(summarize(payloads, fixture), indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
