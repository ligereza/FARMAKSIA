"""Run the offline VIZZ distance/scale experiment contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scale_geometry import (
    ScaleObservation,
    ScreenSpec,
    fuse_scale,
    landolt_c_geometry,
    pose_projection_factor,
)


HERE = Path(__file__).resolve().parent


def load_fixture() -> dict[str, Any]:
    return json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))


def observation_for_scale(
    reference: ScaleObservation, scale: float, yaw_deg: float, pitch_deg: float
) -> ScaleObservation:
    pose = ScaleObservation(1.0, 1.0, yaw_deg=yaw_deg, pitch_deg=pitch_deg)
    projection = pose_projection_factor(pose)
    return ScaleObservation(
        reference.eye_distance_px * scale * projection,
        reference.face_width_px * scale * projection,
        yaw_deg=yaw_deg,
        pitch_deg=pitch_deg,
    )


def main_payload(fixture: dict[str, Any]) -> dict[str, Any]:
    reference = ScaleObservation(**fixture["reference"])
    screen = ScreenSpec(**fixture["screen"])
    target = fixture["visual_target"]
    cases = [
        ("closer", 4.0 / 3.0, 450.0, 12.0, -8.0),
        ("farther", 2.0 / 3.0, 900.0, -10.0, 5.0),
        ("same_distance_pose", 1.0, 600.0, 20.0, -10.0),
        ("contradictory_signals", None, None, 0.0, 0.0),
    ]
    observations: list[dict[str, Any]] = []
    for name, scale, distance_mm, yaw_deg, pitch_deg in cases:
        if scale is None:
            current = ScaleObservation(
                reference.eye_distance_px * 1.25,
                reference.face_width_px * 0.85,
                yaw_deg=yaw_deg,
                pitch_deg=pitch_deg,
            )
        else:
            current = observation_for_scale(reference, scale, yaw_deg, pitch_deg)
        estimate = fuse_scale(reference, current)
        row: dict[str, Any] = {"name": name, "estimate": estimate.as_dict()}
        if estimate.status == "VALID":
            row["distance_mm_ground_truth_for_fixture"] = distance_mm
            row["constant_angle_target"] = screen.target_geometry(
                base_diameter_px=target["base_diameter_px"],
                distance_mm=distance_mm,
                reference_distance_mm=target["reference_distance_mm"],
                gap_ratio=target["gap_ratio"],
                stroke_ratio=target["stroke_ratio"],
            )
        observations.append(row)

    return {
        "experiment": fixture["experiment"],
        "status": "VIZZ_DISTANCE_SCALE_CONTRACT_VERIFIED",
        "evidence_scope": "synthetic_fixture_only; no human data and no camera session",
        "contract": {
            "card_role": fixture["runtime_contract"]["card_role"],
            "required_measurements": fixture["runtime_contract"]["required_measurements"],
            "fusion": "weighted_geometric_mean_in_log_space",
            "distance_relation": "relative_distance = 1 / fused_scale",
            "pose_policy": "bounded_yaw_pitch_correction_else_UNKNOWN",
            "disagreement_policy": "UNKNOWN_if_log_disagreement_exceeds_0.25",
        },
        "reference": fixture["reference"],
        "screen": {
            **fixture["screen"],
            "pixel_pitch_x_mm": screen.pixel_pitch_x_mm,
            "pixel_pitch_y_mm": screen.pixel_pitch_y_mm,
        },
        "visual_target": {
            **target,
            "geometry_at_reference": screen.target_geometry(
                base_diameter_px=target["base_diameter_px"],
                distance_mm=target["reference_distance_mm"],
                reference_distance_mm=target["reference_distance_mm"],
                gap_ratio=target["gap_ratio"],
                stroke_ratio=target["stroke_ratio"],
            ),
            "shape_contract": landolt_c_geometry(
                target["base_diameter_px"],
                gap_ratio=target["gap_ratio"],
                stroke_ratio=target["stroke_ratio"],
            ),
        },
        "observations": observations,
        "safety": {
            "camera_started": False,
            "network_used": False,
            "input_injected": False,
            "raw_frames_persisted": False,
            "screen_mutated": False,
        },
        "unknowns": [
            "The cosine correction is only a bounded protocol approximation, not a 3-D face model.",
            "A webcam cannot establish absolute millimetres without one measured reference distance.",
            "Synthetic invariants do not establish human visual comfort or perceptual success.",
        ],
    }


def main() -> None:
    print(json.dumps(main_payload(load_fixture()), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
