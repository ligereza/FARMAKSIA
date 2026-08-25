"""Run a controlled VIZZ pose/condition validation without changing the profile."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import cv2

from gpu_tracker import GpuTracker, GpuUnavailable
from profile_model import load_profile
from validation_ui import ValidationAborted, ValidationWindow


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_DIR = REPO_ROOT / ".vizz-models"
DEFAULT_PROFILE = REPO_ROOT / ".vizz-calibration.json"
DEFAULT_OUTPUT = REPO_ROOT / ".vizz-validation.json"
LOG_PATH = REPO_ROOT / ".vizz-validation.log"
CONDITION_LABELS = {
    "with_glasses": "con lentes",
    "without_glasses": "sin lentes",
}
POSE_PROXY_NAMES = (
    "face_center_x_norm",
    "face_center_y_norm",
    "face_width_norm",
    "face_height_norm",
    "eye_roll_norm",
    "eye_distance_norm",
)


def open_camera(index: int) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"camera could not be opened: {index}")
    return capture


def run_validation(
    tracker: GpuTracker,
    capture: cv2.VideoCapture,
    profile_path: Path,
    output_path: Path,
    first_condition: str,
    repetitions: int,
) -> None:
    profile, _mapper = load_profile(profile_path)
    second_condition = "without_glasses" if first_condition == "with_glasses" else "with_glasses"
    conditions = (
        (first_condition, CONDITION_LABELS[first_condition]),
        (second_condition, CONDITION_LABELS[second_condition]),
    )
    result: dict[str, object] = {}

    def sample_provider():
        ok, frame = capture.read()
        if not ok:
            return None
        return tracker.sample(frame)

    def complete(records: list[dict[str, object]], screen_size: tuple[int, int], point_order: list[int]) -> None:
        expected_screen_size = tuple(int(value) for value in profile["screen_size"])
        if expected_screen_size != screen_size:
            raise ValueError("validation screen size differs from the calibration profile")
        payload = {
            "schema": "farmaxia:vizz-validation:0.1",
            "profile_schema": profile["schema"],
            "profile_model_sha256": profile["model_sha256"],
            "screen_size": [int(screen_size[0]), int(screen_size[1])],
            "conditions": [condition[0] for condition in conditions],
            "repetitions": repetitions,
            "point_order": point_order,
            "pose_proxy_names": list(POSE_PROXY_NAMES),
            "sample_count": len(records),
            "samples": records,
            "raw_video": False,
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = output_path.with_suffix(output_path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.replace(output_path)
        result["sample_count"] = len(records)

    ValidationWindow(sample_provider, complete, conditions, repetitions=repetitions).run()
    if "sample_count" not in result:
        raise RuntimeError("validation did not write a result")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FARMAKSIA VIZZ controlled validation")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--first-condition", choices=tuple(CONDITION_LABELS), default="with_glasses")
    parser.add_argument("--repetitions", type=int, default=3)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if args.repetitions < 1:
        logging.error("repetitions must be positive")
        return 2
    capture: cv2.VideoCapture | None = None
    try:
        face_model = args.model_dir / "retinaface.onnx"
        gaze_model = args.model_dir / "gaze.onnx"
        tracker = GpuTracker(face_model, gaze_model)
        capture = open_camera(args.camera)
        run_validation(tracker, capture, args.profile, args.output, args.first_condition, args.repetitions)
    except (FileNotFoundError, GpuUnavailable, RuntimeError, ValueError, ValidationAborted) as exc:
        logging.exception("VIZZ validation stopped: %s", exc)
        return 2
    finally:
        if capture is not None:
            capture.release()
    logging.info("VIZZ validation completed; raw_video=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
