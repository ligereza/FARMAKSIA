"""Offline contract checks for experiment 089."""

from __future__ import annotations

import math
from pathlib import Path
import sys

import cv2
import numpy as np


HERE = Path(__file__).resolve().parent
TRACKER_DIR = HERE.parents[1] / "experiments" / "033-vizz-python-headless-runtime"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(TRACKER_DIR))

from dual_contract import (  # noqa: E402
    CALIBRATION_POINTS,
    evaluate_leave_one_target_out,
    fit_mapping,
    fuse_estimates,
    summarize_sensor_window,
)
from gpu_tracker import extract_ir_optics  # noqa: E402
from run_dual_calibration import ReconnectingHikvisionStream, build_output  # noqa: E402
from stereo_geometry import StereoCalibration, triangulate_point  # noqa: E402


def synthetic_records(offset_x: float, offset_y: float) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for repetition in range(2):
        for target_index, (x, y) in enumerate(CALIBRATION_POINTS):
            features = [
                (x - 0.5) * 0.8,
                (y - 0.5) * 0.6,
                (x - 0.5) * 0.7,
                (x - 0.5) * 0.75,
                x + offset_x,
                y + offset_y,
            ]
            records.append(
                {
                    "trial_id": repetition * len(CALIBRATION_POINTS) + target_index,
                    "target_index": target_index,
                    "target": [x, y],
                    "features": features,
                    "quality": 0.95,
                }
            )
    return records


def test_window_summary_is_robust() -> None:
    rows = [
        {
            "frame_read": True,
            "quality": 0.95,
            "features": [0.1, 0.2, 0.1, 0.1, 0.3, 0.4],
            "pose": [0.5, 0.5, 0.25, 0.4, 0.0, 0.12],
            "eye_distance_px": 120.0,
            "face_width_px": 240.0,
            "face_height_px": 192.0,
            "pretrained_gaze_deg": [4.0, -2.0],
            "raw_model_angle_delta_deg": 1.5,
        }
        for _ in range(5)
    ]
    summary = summarize_sensor_window(rows)
    assert summary["status"] == "VALID"
    assert summary["sample_count"] == 5
    assert summary["features"] == [0.1, 0.2, 0.1, 0.1, 0.3, 0.4]
    assert summary["eye_distance_px"] == 120.0
    assert summary["eye_distance_to_face_width"] == 0.5
    assert summary["face_bbox_area_px2"] == 46080.0
    assert summary["pretrained_gaze_sample_count"] == 5
    assert summary["diagnostics"]["accepted_sample_count"] == 5


def test_ir_optical_branch_detects_synthetic_pupil_and_glint() -> None:
    frame = np.full((120, 160, 3), 140, dtype=np.uint8)
    cv2.circle(frame, (80, 60), 9, (20, 20, 20), -1)
    cv2.circle(frame, (84, 56), 2, (255, 255, 255), -1)
    features = extract_ir_optics(frame, ((80.0, 60.0), (80.0, 60.0)), roi_side_px=64.0)
    assert all(item.status == "PUPIL_GLINT" for item in features)
    assert all(item.pupil_glint_vector_px is not None for item in features)
    assert all(item.pupil_diameter_px is not None and item.pupil_diameter_px > 0.0 for item in features)


def test_ir_optical_branch_accepts_bright_pupil_response() -> None:
    frame = np.full((120, 160), 80, dtype=np.uint8)
    cv2.circle(frame, (80, 60), 9, 235, -1)
    feature = extract_ir_optics(frame, ((80.0, 60.0), (80.0, 60.0)), roi_side_px=64.0)[0]
    assert feature.status == "PUPIL_ONLY"
    assert feature.pupil_polarity == "bright"
    assert feature.pupil_diameter_px is not None and feature.pupil_diameter_px > 0.0


def test_ir_summary_is_scalar_and_separate_from_mapper() -> None:
    rows = [
        {
            "frame_read": True,
            "quality": 0.95,
            "features": [0.1, 0.2, 0.1, 0.1, 0.3, 0.4],
            "ir_optics": [
                {
                    "status": "PUPIL_GLINT",
                    "pupil_polarity": "dark",
                    "confidence": 0.8,
                    "local_contrast": 0.25,
                    "pupil_diameter_px": 12.0,
                    "pupil_glint_vector_px": [2.0, -1.0],
                },
                {
                    "status": "PUPIL_ONLY",
                    "pupil_polarity": "bright",
                    "confidence": 0.4,
                    "local_contrast": 0.20,
                    "pupil_diameter_px": 11.0,
                },
            ],
        }
        for _ in range(4)
    ]
    summary = summarize_sensor_window(rows)
    assert summary["ir_optics_status"] == "available"
    assert summary["ir_optics_sample_count"] == 4
    assert summary["ir_pupil_glint_eye_count"] == 4
    assert summary["ir_pupil_glint_pair_rate"] == 0.5
    assert summary["ir_pupil_polarity_counts"] == {"dark": 4, "bright": 4}
    assert summary["ir_pupil_glint_vector_median_px"] == [2.0, -1.0]
    assert summary["ir_pupil_glint_vector_mad_px"] == [0.0, 0.0]


def test_single_sensor_never_disappears() -> None:
    one = fuse_estimates({"webcam": (0.2, 0.3), "hikvision": None}, qualities={"webcam": 0.9})
    both = fuse_estimates(
        {"webcam": (0.2, 0.3), "hikvision": (0.4, 0.5)},
        qualities={"webcam": 0.9, "hikvision": 0.8},
    )
    none = fuse_estimates({"webcam": None, "hikvision": None})
    assert one["mode"] == "WEBCAM_ONLY"
    assert one["sensor_count"] == 1
    assert all(math.isfinite(float(value)) for value in one["screen"])
    assert both["mode"] == "STEREO_DUAL_FUSION"
    assert both["sensor_count"] == 2
    assert none["mode"] == "HOLD_LAST_ESTIMATE"
    assert none["screen"] == [0.5, 0.5]


def test_new_paired_calibration_and_grouped_cv() -> None:
    webcam = synthetic_records(0.0, 0.0)
    hikvision = synthetic_records(0.01, -0.01)
    model = fit_mapping(webcam)
    assert model.sample_count == 24
    result = evaluate_leave_one_target_out(
        {"webcam": webcam, "hikvision": hikvision},
        screen_size=(1707, 960),
    )
    assert result["target_fold_count"] == 12
    assert result["evaluation_count"] == 24
    assert result["webcam"]["count"] == 24
    assert result["hikvision"]["count"] == 24
    assert result["fused"]["count"] == 24


def test_output_contains_scoped_current_session_prediction() -> None:
    records: list[dict[str, object]] = []
    for item in synthetic_records(0.0, 0.0):
        summary = {
            "features": item["features"],
            "quality_median": item["quality"],
        }
        records.append(
            {
                "trial_id": item["trial_id"],
                "target_index": item["target_index"],
                "target": item["target"],
                "sensors": {"webcam": summary, "hikvision": summary},
            }
        )
    payload = build_output(records, 1707, 960, {}, None)
    prediction = payload["trials"][0]["current_session_prediction"]
    assert prediction["mode"] == "STEREO_DUAL_FUSION"
    assert prediction["sensor_count"] == 2
    assert prediction["evaluation_scope"] == "current_session_in_sample_diagnostic"
    assert prediction["is_held_out"] is False
    assert prediction["is_metric_3d"] is False
    assert set(prediction["per_sensor"]) == {"webcam", "hikvision"}


def test_hikvision_reconnects_after_consecutive_read_failures() -> None:
    class FakeCapture:
        def __init__(self, frames: list[bool]) -> None:
            self.frames = frames
            self.released = False

        def read(self) -> tuple[bool, object | None]:
            result = self.frames.pop(0) if self.frames else False
            return result, object() if result else None

        def isOpened(self) -> bool:
            return not self.released

        def release(self) -> None:
            self.released = True

    opened: list[FakeCapture] = []

    def opener(_url: str) -> FakeCapture:
        capture = FakeCapture([False] if not opened else [True])
        opened.append(capture)
        return capture

    stream = ReconnectingHikvisionStream("rtsp://test", opener=opener, max_consecutive_read_failures=1)
    ok_first, _ = stream.read()
    ok_second, frame_second = stream.read()
    assert ok_first is False
    assert ok_second is True
    assert frame_second is not None
    assert stream.reconnect_attempts == 1
    assert stream.reconnect_successes == 1
    stream.release()


def test_runtime_contract_is_pre_click_and_non_persistent() -> None:
    source = (HERE / "run_dual_calibration.py").read_text(encoding="utf-8")
    assert "click_time - PRE_CLICK_GUARD_SECONDS" in source
    assert "samples_are_pre_click" in source
    assert "click_is_scheduler_only" in source
    assert "cv2.imwrite" not in source
    assert "screen_content_persisted" in source
    assert "credentials_persisted" in source
    assert "open_hikvision" in source
    assert "open_webcam" in source
    assert 'cursor="arrow"' in source
    assert 'cursor="none"' not in source
    assert "pretrained_gaze_model" in source
    assert "face_bbox_area_px2" in source
    assert "enable_ir_optics=name == \"hikvision\"" in source
    assert "ir_optical_branch_used_for_mapper" in source


def test_metric_stereo_uses_relative_pose_when_supplied() -> None:
    calibration = StereoCalibration(
        webcam_k=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        hikvision_k=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        rotation_2_from_1=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        translation_2_from_1=(-1.0, 0.0, 0.0),
    )
    result = triangulate_point(calibration, (0.0, 0.0), (-0.2, 0.0))
    assert result["status"] == "METRIC_STEREO_POINT"
    assert abs(result["depth_camera_1"] - 5.0) < 1e-6


if __name__ == "__main__":
    test_window_summary_is_robust()
    test_ir_optical_branch_detects_synthetic_pupil_and_glint()
    test_ir_optical_branch_accepts_bright_pupil_response()
    test_ir_summary_is_scalar_and_separate_from_mapper()
    test_single_sensor_never_disappears()
    test_new_paired_calibration_and_grouped_cv()
    test_output_contains_scoped_current_session_prediction()
    test_hikvision_reconnects_after_consecutive_read_failures()
    test_runtime_contract_is_pre_click_and_non_persistent()
    test_metric_stereo_uses_relative_pose_when_supplied()
    print("FARMAXIA_089_DUAL_SENSOR_CONTRACT_VALID")
