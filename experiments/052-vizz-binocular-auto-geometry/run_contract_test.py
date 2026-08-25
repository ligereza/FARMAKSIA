"""Kill tests for binocular auto-geometry and EDID scale use."""

from __future__ import annotations

import sys
from pathlib import Path


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from relative_autogeometry import BinocularRaySample, fit_monitor_plane  # noqa: E402
from run_experiment import make_planes, make_samples  # noqa: E402


def main() -> None:
    failures: list[str] = []
    planes = make_planes()
    samples = make_samples(planes)
    primary_metric = fit_monitor_plane(samples, "DISPLAY1", edid_width_m=0.38, edid_height_m=0.21)
    secondary_metric = fit_monitor_plane(samples, "DISPLAY2", edid_width_m=0.70, edid_height_m=0.39)
    primary_relative = fit_monitor_plane(samples, "DISPLAY1")

    if primary_metric.status != "VALID_METRIC" or secondary_metric.status != "VALID_METRIC":
        failures.append("EDID scale did not produce metric plane fits")
    if primary_metric.scale_status != "METRIC_FROM_EDID":
        failures.append("metric scale source was not recorded as EDID")
    if primary_relative.status != "VALID_RELATIVE" or primary_relative.width_m is not None:
        failures.append("relative-only fit was incorrectly presented as metres")
    for fit in (primary_metric, secondary_metric):
        if fit.max_plane_residual is None or fit.max_plane_residual > 1e-6:
            failures.append(f"plane residual too large for {fit.monitor_id}")
        if fit.mean_ray_separation is None or fit.mean_ray_separation > 1e-6:
            failures.append(f"binocular rays did not converge for {fit.monitor_id}")
    if abs((primary_metric.width_m or 0.0) - 0.38) > 1e-6 or abs((primary_metric.height_m or 0.0) - 0.21) > 1e-6:
        failures.append("primary EDID dimensions were not recovered")
    if abs((secondary_metric.width_m or 0.0) - 0.70) > 1e-6 or abs((secondary_metric.height_m or 0.0) - 0.39) > 1e-6:
        failures.append("secondary EDID dimensions were not recovered")

    insufficient = fit_monitor_plane(samples[:2], "DISPLAY1")
    if insufficient.status != "UNKNOWN":
        failures.append("insufficient targets did not fail closed")

    parallel_sample = BinocularRaySample(
        sample_id="parallel",
        monitor_id="DISPLAY1",
        target_u=0.5,
        target_v=0.5,
        left_origin=(-0.5, 0.0, 0.0),
        left_direction=(0.0, 0.0, 1.0),
        right_origin=(0.5, 0.0, 0.0),
        right_direction=(0.0, 0.0, 1.0),
    )
    parallel = fit_monitor_plane((parallel_sample,) * 6, "DISPLAY1")
    if parallel.status != "UNKNOWN":
        failures.append("parallel binocular rays were accepted")

    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("VIZZ_052_BINOCULAR_AUTO_GEOMETRY_CONTRACT_VALID")


if __name__ == "__main__":
    main()
