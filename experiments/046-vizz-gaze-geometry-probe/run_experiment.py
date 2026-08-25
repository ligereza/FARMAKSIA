"""Synthetic geometry-first probe for VIZZ; no camera and no screen mutation."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from gaze_geometry import (
    DisplayState,
    GazeObservation,
    InteractionContext,
    MonitorLayout,
    MonitorPlane,
    angular_extent_deg,
    resolve_gaze,
    visual_policy,
)


HERE = Path(__file__).parent


def direction_to(point: tuple[float, float, float], origin: tuple[float, float, float]) -> tuple[float, float, float]:
    delta = tuple(point[index] - origin[index] for index in range(3))
    length = math.sqrt(sum(value * value for value in delta))
    return tuple(value / length for value in delta)


def make_layout(version: str = "desk-2-monitor-v1", *, overlapping: bool = False) -> MonitorLayout:
    secondary_x = 0.0 if overlapping else 0.92
    return MonitorLayout(
        version=version,
        monitors=(
            MonitorPlane(
                "primary",
                origin=(0.0, 0.0, 0.72),
                horizontal_axis=(1.0, 0.0, 0.0),
                vertical_axis=(0.0, 1.0, 0.0),
                width_m=0.80,
                height_m=0.45,
                logical_rect=(0, 0, 1920, 1080),
            ),
            MonitorPlane(
                "secondary",
                origin=(secondary_x, 0.0, 0.72),
                horizontal_axis=(1.0, 0.0, 0.0),
                vertical_axis=(0.0, 1.0, 0.0),
                width_m=0.80,
                height_m=0.45,
                logical_rect=(1920, 0, 1920, 1080),
            ),
        ),
    )


def make_angled_layout() -> MonitorLayout:
    return MonitorLayout(
        version="desk-angled-monitor-v1",
        monitors=(
            MonitorPlane(
                "angled",
                origin=(0.12, 0.0, 0.72),
                horizontal_axis=(0.9396926208, 0.0, -0.3420201433),
                vertical_axis=(0.0, 1.0, 0.0),
                width_m=0.80,
                height_m=0.45,
                logical_rect=(0, 0, 1920, 1080),
            ),
        ),
    )


def observation_for(
    point: tuple[float, float, float],
    *,
    eyes: tuple[tuple[float, float, float], tuple[float, float, float]] = ((-0.032, 0.0, 0.0), (0.032, 0.0, 0.0)),
    layout_version: str = "desk-2-monitor-v1",
    confidence: float = 0.98,
    uncertainty_deg: float = 0.35,
    head_pose_valid: bool = True,
) -> GazeObservation:
    midpoint = (
        (eyes[0][0] + eyes[1][0]) / 2.0,
        (eyes[0][1] + eyes[1][1]) / 2.0,
        (eyes[0][2] + eyes[1][2]) / 2.0,
    )
    return GazeObservation(
        timestamp_capture=1.0,
        left_eye_world=eyes[0],
        right_eye_world=eyes[1],
        gaze_direction_world=direction_to(point, midpoint),
        confidence=confidence,
        uncertainty_deg=uncertainty_deg,
        layout_version=layout_version,
        fixation_state="fixation",
        head_pose_valid=head_pose_valid,
    )


def summarize_case(
    case_id: str,
    observation: GazeObservation,
    layout: MonitorLayout,
    context: InteractionContext | None = None,
    *,
    gaze_speed_deg_s: float = 0.0,
    latency_ms: float = 0.0,
) -> dict[str, Any]:
    state = resolve_gaze(
        observation,
        layout,
        gaze_speed_deg_s=gaze_speed_deg_s,
        latency_ms=latency_ms,
    )
    context = context or InteractionContext()
    policy = visual_policy(state, context, DisplayState(layout.version), task="typing" if context.keyboard_active else "unknown")
    return {
        "id": case_id,
        "state": state.as_dict(),
        "policy": policy.as_dict(),
        "mouse_is_ground_truth": policy.mouse_is_ground_truth,
    }


def main() -> None:
    layout = make_layout()
    primary_target = (0.12, -0.08, 0.72)
    secondary_target = (0.92, 0.04, 0.72)
    angled = make_angled_layout()
    angled_target = (
        angled.monitors[0].origin[0] + angled.monitors[0].horizontal_axis[0] * 0.16,
        angled.monitors[0].origin[1] + angled.monitors[0].vertical_axis[1] * 0.04,
        angled.monitors[0].origin[2] + angled.monitors[0].horizontal_axis[2] * 0.16,
    )
    cases = [
        summarize_case("primary_valid", observation_for(primary_target), layout),
        summarize_case(
            "head_translation_same_world_target",
            observation_for(primary_target, eyes=((0.08, 0.04, 0.02), (0.144, 0.04, 0.02))),
            layout,
            gaze_speed_deg_s=12.0,
            latency_ms=80.0,
        ),
        summarize_case("secondary_monitor_valid", observation_for(secondary_target), layout),
        summarize_case(
            "angled_monitor_valid",
            observation_for(angled_target, layout_version=angled.version),
            angled,
        ),
        summarize_case(
            "keyboard_context_is_not_gaze_truth",
            observation_for(primary_target),
            layout,
            InteractionContext(keyboard_active=True, keyboard_event_count=3, mouse_screen=(1730, 540)),
        ),
        summarize_case(
            "low_confidence_unknown",
            observation_for(primary_target, confidence=0.4),
            layout,
        ),
        summarize_case(
            "stale_layout_unknown",
            observation_for(primary_target, layout_version="desk-old-v0"),
            layout,
        ),
        summarize_case(
            "missing_eye_unknown",
            GazeObservation(1.0, None, (0.032, 0.0, 0.0), (0.0, 0.0, 1.0), 0.98, 0.35, layout.version),
            layout,
        ),
        summarize_case(
            "ambiguous_monitor_unknown",
            observation_for(primary_target),
            make_layout(overlapping=True),
        ),
    ]
    result = {
        "schema": "farmaxia:vizz-gaze-geometry-probe:0.1",
        "experiment": "046-vizz-gaze-geometry-probe",
        "objective": "resolve binocular gaze geometry into monitor hypotheses without mutating screen content",
        "cases": cases,
        "human_data": False,
        "camera_opened": False,
        "screen_content_mutated": False,
        "network_used": False,
        "mouse_is_ground_truth": False,
        "angular_extent_example_deg": {
            "width": angular_extent_deg(0.598, 0.72),
            "height": angular_extent_deg(0.336, 0.72),
        },
        "cpu_fallback_policy": "not applicable; synthetic geometry only",
        "scope_limit": "synthetic contract; no claim of webcam accuracy, comfort, medical benefit or human performance",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
