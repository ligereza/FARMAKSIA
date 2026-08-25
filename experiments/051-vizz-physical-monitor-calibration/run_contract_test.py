"""Contract tests for measured physical monitor geometry."""

from __future__ import annotations

import sys
from pathlib import Path


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "046-vizz-gaze-geometry-probe"))
sys.path.insert(0, str(HERE))

from physical_calibration import (
    PhysicalCalibrationError,
    PhysicalMonitorSpec,
    build_physical_layout,
    calibration_targets,
    reject_pixel_only_layout,
)
from run_experiment import make_specs


def main() -> None:
    failures: list[str] = []
    specs = make_specs()
    layout = build_physical_layout(specs, logical_layout_version="0561e7fb0c475e42")
    if len(layout.monitors) != 2:
        failures.append("physical layout did not preserve both monitors")
    if not layout.version:
        failures.append("physical layout version is missing")
    targets = tuple(target for spec in specs for target in calibration_targets(spec.monitor_id))
    if len(targets) != 18 or len({target["id"] for target in targets}) != 18:
        failures.append("expected nine unique presented targets per monitor")
    if any(target["mouse_is_ground_truth"] for target in targets):
        failures.append("mouse became target truth")

    try:
        reject_pixel_only_layout(1707, 960, source="windows_pixels")
    except PhysicalCalibrationError:
        pass
    else:
        failures.append("Windows pixels were accepted as physical metres")

    try:
        PhysicalMonitorSpec(
            monitor_id="pixel-only",
            logical_rect=(0, 0, 1707, 960),
            width_m=0.0,
            height_m=0.0,
            origin=(0.0, 0.0, 0.0),
            horizontal_axis=(1.0, 0.0, 0.0),
            vertical_axis=(0.0, 1.0, 0.0),
            scale_source="windows_pixels",
            pose_source="declared_fixture",
            measurement_id="invalid",
        )
    except PhysicalCalibrationError:
        pass
    else:
        failures.append("invalid physical dimensions were accepted")

    changed = list(specs)
    changed[0] = PhysicalMonitorSpec(
        monitor_id=changed[0].monitor_id,
        logical_rect=(0, 0, 1708, 960),
        width_m=changed[0].width_m,
        height_m=changed[0].height_m,
        origin=changed[0].origin,
        horizontal_axis=changed[0].horizontal_axis,
        vertical_axis=changed[0].vertical_axis,
        scale_source=changed[0].scale_source,
        pose_source=changed[0].pose_source,
        measurement_id=changed[0].measurement_id,
    )
    if changed[0].logical_rect == specs[0].logical_rect:
        failures.append("logical layout change was not visible")

    if any(state not in {"declared_fixture", "manual_measurement", "edid_verified_manual", "known_marker"} for state in (spec.scale_source for spec in specs)):
        failures.append("unsupported scale source escaped validation")

    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("VIZZ_051_PHYSICAL_CALIBRATION_CONTRACT_VALID")


if __name__ == "__main__":
    main()
