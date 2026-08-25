"""Synthetic physical-monitor calibration contract; no camera or screen mutation."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "046-vizz-gaze-geometry-probe"))
from gaze_geometry import GazeObservation, resolve_gaze  # noqa: E402

from physical_calibration import (  # noqa: E402
    PhysicalCalibrationError,
    PhysicalMonitorSpec,
    build_physical_layout,
    calibration_targets,
    reject_pixel_only_layout,
)


def _direction_to(point: tuple[float, float, float], origin: tuple[float, float, float]) -> tuple[float, float, float]:
    delta = tuple(point[index] - origin[index] for index in range(3))
    length = math.sqrt(sum(value * value for value in delta))
    return tuple(value / length for value in delta)


def make_specs() -> tuple[PhysicalMonitorSpec, ...]:
    return (
        PhysicalMonitorSpec(
            monitor_id=r"\\.\DISPLAY1",
            logical_rect=(0, 0, 1707, 960),
            width_m=0.598,
            height_m=0.336,
            origin=(0.0, 0.0, 0.72),
            horizontal_axis=(1.0, 0.0, 0.0),
            vertical_axis=(0.0, 1.0, 0.0),
            scale_source="declared_fixture",
            pose_source="declared_fixture",
            measurement_id="fixture-primary-v1",
            reprojection_error_px=0.0,
            marker_count=4,
        ),
        PhysicalMonitorSpec(
            monitor_id=r"\\.\DISPLAY2",
            logical_rect=(2560, 0, 3926, 768),
            width_m=0.598,
            height_m=0.336,
            origin=(0.78, 0.02, 0.74),
            horizontal_axis=(0.9659258263, 0.0, -0.2588190451),
            vertical_axis=(0.0, 1.0, 0.0),
            scale_source="declared_fixture",
            pose_source="declared_fixture",
            measurement_id="fixture-secondary-v1",
            reprojection_error_px=0.0,
            marker_count=4,
        ),
    )


def main() -> None:
    specs = make_specs()
    layout = build_physical_layout(specs, logical_layout_version="0561e7fb0c475e42")
    eyes = ((-0.032, 0.0, 0.0), (0.032, 0.0, 0.0))
    primary_target = (0.08, 0.04, 0.72)
    midpoint = (0.0, 0.0, 0.0)
    observation = GazeObservation(
        timestamp_capture=1.0,
        left_eye_world=eyes[0],
        right_eye_world=eyes[1],
        gaze_direction_world=_direction_to(primary_target, midpoint),
        confidence=0.98,
        uncertainty_deg=0.4,
        layout_version=layout.version,
        fixation_state="fixation",
        head_pose_valid=True,
    )
    resolved = resolve_gaze(observation, layout)
    rejected = False
    rejection_reason = None
    try:
        reject_pixel_only_layout(1707, 960, source="windows_pixels")
    except PhysicalCalibrationError as exc:
        rejected = True
        rejection_reason = str(exc)

    targets = tuple(target for spec in specs for target in calibration_targets(spec.monitor_id))
    result = {
        "schema": "farmaxia:vizz-physical-monitor-calibration:0.1",
        "experiment": "051-vizz-physical-monitor-calibration",
        "objective": "convert measured monitor geometry into 046-compatible 3-D planes without pixel-to-metre inference",
        "logical_layout_version": "0561e7fb0c475e42",
        "physical_layout_version": layout.version,
        "monitors": [spec.as_dict() for spec in specs],
        "calibration_target_count": len(targets),
        "resolved_fixture_state": resolved.as_dict(),
        "pixel_only_rejected": rejected,
        "pixel_only_rejection_reason": rejection_reason,
        "human_data": False,
        "camera_opened": False,
        "screen_content_mutated": False,
        "network_used": False,
        "mouse_is_ground_truth": False,
        "scope_limit": "synthetic geometry contract; no claim of webcam accuracy, distance measurement or perceptual benefit",
        "contract": "VIZZ_051_PHYSICAL_CALIBRATION_CONTRACT_VALID",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
