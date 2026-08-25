"""Offline audit for VIZZ binocular quality traces; no camera or screen access."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


def _number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _quantile(values: Iterable[float], probability: float) -> float | None:
    ordered = sorted(float(value) for value in values if math.isfinite(float(value)))
    if not ordered:
        return None
    index = int(math.floor((len(ordered) - 1) * probability))
    return round(ordered[index], 6)


def _count(values: Iterable[Any], predicate: Any) -> int:
    return sum(1 for value in values if predicate(value))


@dataclass(frozen=True)
class DisplayLayout:
    """Logical x-ranges obtained from the Windows display probe."""

    primary_right: int = 1707
    secondary_left: int = 2560
    secondary_right: int = 3926

    def region(self, x: int) -> str:
        if 0 <= x < self.primary_right:
            return "DISPLAY1"
        if self.primary_right <= x < self.secondary_left:
            return "GAP_OR_UNMAPPED"
        if self.secondary_left <= x < self.secondary_right:
            return "DISPLAY2"
        return "OUTSIDE_KNOWN_LAYOUT"


@dataclass(frozen=True)
class TraceSummary:
    path: str
    schema: str
    duration_seconds: float | None
    observed_hz: float | None
    sample_count: int
    valid_sample_count: int
    ray_valid_count: int
    ray_unknown_count: int
    quality_min: float | None
    quality_p05: float | None
    quality_median: float | None
    quality_below_0_5: int
    disagreement_p50_deg: float | None
    disagreement_p95_deg: float | None
    disagreement_max_deg: float | None
    disagreement_gt_15_deg: int
    disagreement_gt_30_deg: int
    eye_distance_p50_px: float | None
    eye_distance_p05_px: float | None
    eye_distance_p95_px: float | None
    keyboard_events_total: int
    keyboard_active_sample_count: int
    pointer_regions: dict[str, int]
    unknown_reasons: dict[str, int]
    blink_signal_available: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "schema": self.schema,
            "duration_seconds": self.duration_seconds,
            "observed_hz": self.observed_hz,
            "sample_count": self.sample_count,
            "valid_sample_count": self.valid_sample_count,
            "ray_valid_count": self.ray_valid_count,
            "ray_unknown_count": self.ray_unknown_count,
            "quality": {
                "min": self.quality_min,
                "p05": self.quality_p05,
                "median": self.quality_median,
                "below_0_5": self.quality_below_0_5,
            },
            "binocular_disagreement_deg": {
                "p50": self.disagreement_p50_deg,
                "p95": self.disagreement_p95_deg,
                "max": self.disagreement_max_deg,
                "above_15": self.disagreement_gt_15_deg,
                "above_30": self.disagreement_gt_30_deg,
            },
            "eye_distance_px": {
                "p05": self.eye_distance_p05_px,
                "p50": self.eye_distance_p50_px,
                "p95": self.eye_distance_p95_px,
            },
            "keyboard": {
                "events_total": self.keyboard_events_total,
                "active_sample_count": self.keyboard_active_sample_count,
            },
            "pointer_regions": self.pointer_regions,
            "unknown_reasons": self.unknown_reasons,
            "blink_signal_available": self.blink_signal_available,
        }


def _load_rows(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"trace file not found: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON at line {line_number}: {path}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"trace row is not an object at line {line_number}: {path}")
        rows.append(row)
    headers = [row for row in rows if row.get("type") == "header"]
    footers = [row for row in rows if row.get("type") == "footer"]
    if len(headers) != 1 or len(footers) != 1:
        raise ValueError("trace must contain exactly one header and one footer")
    header, footer = headers[0], footers[0]
    schema = header.get("schema")
    if not isinstance(schema, str) or not schema.startswith("farmaxia:vizz-binocular-quality-trace:"):
        raise ValueError("unsupported quality trace schema")
    if header.get("raw_video") is not False or header.get("screen_content") is not False:
        raise ValueError("trace violates raw-video or screen-content policy")
    if footer.get("raw_video") is not False or footer.get("screen_content_mutated") is not False:
        raise ValueError("trace footer violates persistence policy")
    return header, [row for row in rows if row.get("type") == "sample"], footer


def summarize_trace(path: Path, layout: DisplayLayout = DisplayLayout()) -> TraceSummary:
    header, samples, footer = _load_rows(path)
    sample_count = len(samples)
    if int(footer.get("sample_count", -1)) != sample_count:
        raise ValueError("footer sample count does not match trace rows")
    timestamps = [_number(row.get("t_monotonic")) for row in samples]
    times = [value for value in timestamps if value is not None]
    duration = max(times) - min(times) if len(times) >= 2 else None
    observed_hz = sample_count / duration if duration and duration > 0.0 else None
    qualities = [_number(row.get("quality")) for row in samples]
    quality_values = [value for value in qualities if value is not None]
    disagreements = [_number(row.get("disagreement_deg")) for row in samples]
    disagreement_values = [value for value in disagreements if value is not None]
    eye_distances = [_number(row.get("eye_centric_distance_px")) for row in samples]
    eye_distance_values = [value for value in eye_distances if value is not None and value > 0.0]
    unknown_reasons: dict[str, int] = {}
    pointer_regions = {"DISPLAY1": 0, "DISPLAY2": 0, "GAP_OR_UNMAPPED": 0, "OUTSIDE_KNOWN_LAYOUT": 0}
    for row in samples:
        ray = row.get("binocular_ray_proxy")
        if ray is None:
            reason = row.get("binocular_ray_unknown_reason") or "missing_ray_without_reason"
            unknown_reasons[str(reason)] = unknown_reasons.get(str(reason), 0) + 1
        pointer = row.get("mouse_screen")
        if isinstance(pointer, list) and len(pointer) == 2:
            x = _number(pointer[0])
            if x is not None:
                pointer_regions[layout.region(int(x))] += 1
    valid_sample_count = _count(qualities, lambda value: value is not None)
    ray_valid_count = _count((row.get("binocular_ray_proxy") for row in samples), lambda value: value is not None)
    ray_unknown_count = sample_count - ray_valid_count
    blink_signal_available = any("blink" in row or "blink_state" in row for row in samples)
    return TraceSummary(
        path=str(path),
        schema=str(header["schema"]),
        duration_seconds=round(duration, 6) if duration is not None else None,
        observed_hz=round(observed_hz, 6) if observed_hz is not None else None,
        sample_count=sample_count,
        valid_sample_count=valid_sample_count,
        ray_valid_count=ray_valid_count,
        ray_unknown_count=ray_unknown_count,
        quality_min=round(min(quality_values), 6) if quality_values else None,
        quality_p05=_quantile(quality_values, 0.05),
        quality_median=_quantile(quality_values, 0.50),
        quality_below_0_5=_count(quality_values, lambda value: value < 0.5),
        disagreement_p50_deg=_quantile(disagreement_values, 0.50),
        disagreement_p95_deg=_quantile(disagreement_values, 0.95),
        disagreement_max_deg=round(max(disagreement_values), 6) if disagreement_values else None,
        disagreement_gt_15_deg=_count(disagreement_values, lambda value: value > 15.0),
        disagreement_gt_30_deg=_count(disagreement_values, lambda value: value > 30.0),
        eye_distance_p50_px=_quantile(eye_distance_values, 0.50),
        eye_distance_p05_px=_quantile(eye_distance_values, 0.05),
        eye_distance_p95_px=_quantile(eye_distance_values, 0.95),
        keyboard_events_total=int(footer.get("keyboard_event_count_total", 0)),
        keyboard_active_sample_count=int(footer.get("keyboard_active_sample_count", 0)),
        pointer_regions=pointer_regions,
        unknown_reasons=unknown_reasons,
        blink_signal_available=blink_signal_available,
    )


def compare_traces(with_glasses: TraceSummary, without_glasses: TraceSummary) -> dict[str, object]:
    def difference(left: float | None, right: float | None) -> float | None:
        if left is None or right is None:
            return None
        return round(right - left, 6)

    return {
        "condition_order": "without_glasses_minus_with_glasses",
        "quality_median_delta": difference(with_glasses.quality_median, without_glasses.quality_median),
        "quality_p05_delta": difference(with_glasses.quality_p05, without_glasses.quality_p05),
        "disagreement_p95_delta_deg": difference(with_glasses.disagreement_p95_deg, without_glasses.disagreement_p95_deg),
        "eye_distance_p50_delta_px": difference(with_glasses.eye_distance_p50_px, without_glasses.eye_distance_p50_px),
        "ray_coverage_delta": difference(
            with_glasses.ray_valid_count / max(1, with_glasses.sample_count),
            without_glasses.ray_valid_count / max(1, without_glasses.sample_count),
        ),
        "interpretation": [
            "Condition is confounded with session, posture, distance and task history.",
            "Naturalistic traces are quality evidence, not gaze-to-monitor ground truth.",
            "No blink count is identifiable because the capture schema has no blink detector.",
        ],
    }


def audit_files(with_glasses_path: Path, without_glasses_path: Path, layout: DisplayLayout = DisplayLayout()) -> dict[str, object]:
    with_glasses = summarize_trace(with_glasses_path, layout)
    without_glasses = summarize_trace(without_glasses_path, layout)
    return {
        "schema": "farmaxia:vizz-naturalistic-quality-audit:0.1",
        "sessions": {
            "with_glasses": with_glasses.as_dict(),
            "without_glasses": without_glasses.as_dict(),
        },
        "comparison": compare_traces(with_glasses, without_glasses),
        "trace_source": "local_trace_files_supplied_for_offline_audit",
        "raw_video": False,
        "screen_content": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline VIZZ quality trace audit")
    parser.add_argument("--with-glasses", required=True, type=Path)
    parser.add_argument("--without-glasses", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--primary-right", type=int, default=1707)
    parser.add_argument("--secondary-left", type=int, default=2560)
    parser.add_argument("--secondary-right", type=int, default=3926)
    args = parser.parse_args()
    layout = DisplayLayout(args.primary_right, args.secondary_left, args.secondary_right)
    result = audit_files(args.with_glasses, args.without_glasses, layout)
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
