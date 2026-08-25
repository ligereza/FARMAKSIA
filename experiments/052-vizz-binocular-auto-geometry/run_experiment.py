"""Synthetic binocular auto-geometry experiment; no camera or screen mutation."""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from relative_autogeometry import BinocularRaySample, PlaneFit, fit_monitor_plane  # noqa: E402


@dataclass(frozen=True)
class SyntheticPlane:
    monitor_id: str
    center: tuple[float, float, float]
    horizontal_axis: tuple[float, float, float]
    vertical_axis: tuple[float, float, float]
    relative_width: float
    relative_height: float


def _add(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return a[0] + b[0], a[1] + b[1], a[2] + b[2]


def _scale(a: tuple[float, float, float], factor: float) -> tuple[float, float, float]:
    return a[0] * factor, a[1] * factor, a[2] * factor


def _sub(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


def _norm(a: tuple[float, float, float]) -> float:
    return math.sqrt(sum(value * value for value in a))


def _direction(point: tuple[float, float, float], origin: tuple[float, float, float]) -> tuple[float, float, float]:
    delta = _sub(point, origin)
    length = _norm(delta)
    return _scale(delta, 1.0 / length)


def _target(plane: SyntheticPlane, u: float, v: float) -> tuple[float, float, float]:
    return _add(
        plane.center,
        _add(
            _scale(plane.horizontal_axis, (u - 0.5) * plane.relative_width),
            _scale(plane.vertical_axis, (v - 0.5) * plane.relative_height),
        ),
    )


def make_planes() -> tuple[SyntheticPlane, ...]:
    return (
        SyntheticPlane("DISPLAY1", (0.0, 0.0, 11.25), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), 5.9375, 3.28125),
        SyntheticPlane(
            "DISPLAY2",
            (14.5, 0.5, 11.6),
            (0.9659258263, 0.0, -0.2588190451),
            (0.0, 1.0, 0.0),
            10.9375,
            6.09375,
        ),
    )


def make_samples(planes: tuple[SyntheticPlane, ...]) -> tuple[BinocularRaySample, ...]:
    values = (0.10, 0.50, 0.90)
    head_translations = ((0.0, 0.0, 0.0), (0.7, 0.18, 0.35), (-0.45, -0.12, 0.22))
    samples: list[BinocularRaySample] = []
    index = 0
    for plane in planes:
        for row, v in enumerate(values):
            for column, u in enumerate(values):
                head = head_translations[(row + column) % len(head_translations)]
                left_origin = _add((-0.5, 0.0, 0.0), head)
                right_origin = _add((0.5, 0.0, 0.0), head)
                point = _target(plane, u, v)
                samples.append(
                    BinocularRaySample(
                        sample_id=f"{plane.monitor_id}-{index}",
                        monitor_id=plane.monitor_id,
                        target_u=u,
                        target_v=v,
                        left_origin=left_origin,
                        left_direction=_direction(point, left_origin),
                        right_origin=right_origin,
                        right_direction=_direction(point, right_origin),
                        head_translation=head,
                    )
                )
                index += 1
    return tuple(samples)


def _summarize(fit: PlaneFit) -> dict[str, object]:
    return fit.as_dict()


def main() -> None:
    planes = make_planes()
    samples = make_samples(planes)
    metric_fits = {
        "DISPLAY1": fit_monitor_plane(samples, "DISPLAY1", edid_width_m=0.38, edid_height_m=0.21),
        "DISPLAY2": fit_monitor_plane(samples, "DISPLAY2", edid_width_m=0.70, edid_height_m=0.39),
    }
    relative_fit = fit_monitor_plane(samples, "DISPLAY1")
    result = {
        "schema": "farmaxia:vizz-binocular-auto-geometry:0.1",
        "experiment": "052-vizz-binocular-auto-geometry",
        "objective": "infer monitor planes from binocular fixation rays and natural head translation, using EDID only as optional scale",
        "sample_count": len(samples),
        "head_translation_states": 3,
        "metric_fits": {monitor_id: _summarize(fit) for monitor_id, fit in metric_fits.items()},
        "relative_fit_without_edid": _summarize(relative_fit),
        "mouse_is_ground_truth": False,
        "human_data": False,
        "camera_opened": False,
        "screen_content_mutated": False,
        "network_used": False,
        "interpretation": {
            "metric_scale_source": "consensus EDID dimensions",
            "head_motion_role": "parallax excitation; plane remains fixed",
            "failure_mode": "UNKNOWN when binocular rays, target geometry or scale are not identifiable",
        },
        "scope_limit": "synthetic reconstruction; does not validate webcam gaze accuracy or human perceptual benefit",
        "contract": "VIZZ_052_BINOCULAR_AUTO_GEOMETRY_CONTRACT_VALID",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
