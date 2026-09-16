"""Analyze one VIZZ 084 trace without claiming absolute depth or comfort.

The analyzer is intentionally standard-library only. It reports capture
integrity, agreement between the two facial rulers, relative scaling and a
coarse temporal comparison. It cannot infer physical millimetres or prove
that a person experienced less fatigue.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
DEFAULT_INPUT = REPO_ROOT / ".vizz-distance-scale-trace.jsonl"


def _quantile(values: Iterable[float], probability: float) -> float | None:
    ordered = sorted(float(value) for value in values if math.isfinite(float(value)))
    if not ordered:
        return None
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * probability)))
    return ordered[index]


def _summary(values: Iterable[float]) -> dict[str, float | None]:
    finite = [float(value) for value in values if math.isfinite(float(value))]
    if not finite:
        return {"count": 0, "min": None, "median": None, "p05": None, "p95": None, "max": None}
    return {
        "count": len(finite),
        "min": min(finite),
        "median": statistics.median(finite),
        "p05": _quantile(finite, 0.05),
        "p95": _quantile(finite, 0.95),
        "max": max(finite),
    }


def load_trace(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any] | None]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows or rows[0].get("type") != "header":
        raise ValueError("trace must begin with a header")
    header = rows[0]
    footer = rows[-1] if rows[-1].get("type") == "footer" else None
    samples = [row for row in rows if row.get("type") == "sample"]
    return header, samples, footer


def analyze_trace(
    header: dict[str, Any], samples: list[dict[str, Any]], footer: dict[str, Any] | None
) -> dict[str, Any]:
    valid = [row for row in samples if row.get("scale", {}).get("status") == "VALID"]
    unknown = [row for row in samples if row.get("scale", {}).get("status") != "VALID"]
    fused = [float(row["scale"]["fused_scale"]) for row in valid]
    distance_ratio = [float(row["scale"]["relative_distance_ratio"]) for row in valid]
    target = [float(row["target_diameter_px"]) for row in valid]
    eye_scale = [float(row["scale"]["eye_scale"]) for row in valid]
    face_scale = [float(row["scale"]["face_scale"]) for row in valid]
    disagreement = [float(row["scale"]["log_disagreement"]) for row in valid]
    eye_px = [float(row["eye_distance_px"]) for row in valid]
    face_px = [float(row["face_width_px"]) for row in valid]
    timestamps = [float(row["t_monotonic"]) for row in samples if row.get("t_monotonic") is not None]
    duration = max(timestamps) - min(timestamps) if len(timestamps) >= 2 else None
    decile = max(1, len(fused) // 10)
    first_window = fused[:decile]
    last_window = fused[-decile:]
    first_median = statistics.median(first_window) if first_window else None
    last_median = statistics.median(last_window) if last_window else None
    median_step = statistics.median(abs(second - first) for first, second in zip(fused, fused[1:])) if len(fused) > 1 else None
    safety_fields = {
        "raw_video": header.get("raw_video"),
        "screen_content_mutated": header.get("screen_content_mutated"),
        "input_injected": header.get("input_injected"),
        "text_persisted": header.get("text_persisted"),
    }
    safety_violations = [name for name, value in safety_fields.items() if value is True]
    footer_consistent = footer is None or (
        footer.get("sample_count") == len(samples)
        and footer.get("valid_count") == len(valid)
        and footer.get("unknown_count") == len(unknown)
    )
    return {
        "status": "VIZZ_TRACE_ANALYZED_EXPLORATORY",
        "evidence_scope": "one_human_trace; relative_scale_only; not_a_clinical_or_depth_measurement",
        "input": {
            "schema": header.get("schema"),
            "reference_source": header.get("reference_source"),
            "card_role": header.get("card_role"),
            "duration_s": duration,
            "sample_count": len(samples),
            "valid_count": len(valid),
            "unknown_count": len(unknown),
            "valid_rate": len(valid) / len(samples) if samples else 0.0,
        },
        "integrity": {
            "footer_present": footer is not None,
            "footer_consistent": footer_consistent,
            "safety_fields": safety_fields,
            "safety_violations": safety_violations,
        },
        "reference": header.get("reference"),
        "facial_rulers_px": {
            "eye_distance": _summary(eye_px),
            "face_width": _summary(face_px),
        },
        "relative_estimate": {
            "fused_scale": _summary(fused),
            "distance_ratio": _summary(distance_ratio),
            "target_diameter_px": _summary(target),
            "eye_scale": _summary(eye_scale),
            "face_scale": _summary(face_scale),
            "log_disagreement": _summary(disagreement),
        },
        "temporal": {
            "first_decile_fused_scale_median": first_median,
            "last_decile_fused_scale_median": last_median,
            "first_to_last_fused_scale_ratio": (
                first_median / last_median if first_median is not None and last_median not in (None, 0.0) else None
            ),
            "median_absolute_fused_scale_step": median_step,
        },
        "interpretation": {
            "rulers_agree": bool(disagreement) and (_quantile(disagreement, 0.95) is not None) and _quantile(disagreement, 0.95) <= 0.25,
            "relative_target_changed": len(set(round(value, 3) for value in target)) > 1,
            "compatible_with_moving_farther_or_closer": first_median is not None and last_median is not None and first_median != last_median,
            "human_effect": "UNKNOWN; record subjective comfort/task effect separately",
            "absolute_distance_mm": "UNKNOWN; requires camera intrinsics or one measured physical distance",
        },
        "limits": [
            "A single trace cannot prove improved comfort or visual performance.",
            "No external distance ground truth was recorded in this trace.",
            "Current tracker does not provide 3-D yaw/pitch correction.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a VIZZ 084 JSONL trace")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    header, samples, footer = load_trace(args.input)
    print(json.dumps(analyze_trace(header, samples, footer), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
