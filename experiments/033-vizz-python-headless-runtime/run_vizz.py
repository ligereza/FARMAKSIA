"""Run one visible calibration, then continue as a headless content modifier."""

from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

import cv2

from content_overlay import FocusOverlay
from gpu_tracker import GpuTracker, GpuUnavailable
from profile_model import load_profile, seal_profile


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_DIR = REPO_ROOT / ".vizz-models"
DEFAULT_PROFILE = REPO_ROOT / ".vizz-calibration.json"
LOG_PATH = REPO_ROOT / ".vizz-runtime.log"


def open_camera(index: int) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"camera could not be opened: {index}")
    return capture


def run_calibration(tracker: GpuTracker, capture: cv2.VideoCapture, profile_path: Path) -> None:
    # Import the UI lazily so headless execution never imports a UI toolkit.
    from calibration_ui import CalibrationWindow

    result: dict[str, object] = {}

    def sample_provider():
        ok, frame = capture.read()
        if not ok:
            return None
        return tracker.sample(frame)

    def complete(samples: list[dict[str, object]], screen_size: tuple[int, int]) -> None:
        seal_profile(profile_path, screen_size, samples, tracker.face_model_sha256)
        result["screen_size"] = screen_size

    CalibrationWindow(sample_provider, complete).run()
    if "screen_size" not in result:
        raise RuntimeError("calibration did not seal a profile")


def run_headless(tracker: GpuTracker, capture: cv2.VideoCapture, profile_path: Path, alpha: int, radius: int) -> None:
    profile, mapper = load_profile(profile_path)
    width, height = [int(value) for value in profile["screen_size"]]
    with FocusOverlay(width, height, alpha=alpha, radius_px=radius) as overlay:
        logging.info("headless runtime active; visible_interface=False")
        try:
            while True:
                ok, frame = capture.read()
                if not ok:
                    overlay.hide()
                    time.sleep(0.05)
                    continue
                sample = tracker.sample(frame)
                if sample is None or sample.quality < 0.50:
                    overlay.hide()
                    continue
                point = mapper.predict(sample.features)
                overlay.set_focus(*point)
                time.sleep(0.01)
        except KeyboardInterrupt:
            logging.info("headless runtime stopped")
        finally:
            overlay.hide()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FARMAKSIA VIZZ Python runtime")
    parser.add_argument("--calibrate", action="store_true", help="show the one-shot calibration UI first")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--overlay-alpha", type=int, default=30)
    parser.add_argument("--focus-radius", type=int, default=260)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    face_model = args.model_dir / "retinaface.onnx"
    gaze_model = args.model_dir / "gaze.onnx"
    try:
        if not args.calibrate:
            # A headless launch with a missing/invalid profile must fail before
            # it requests camera access.
            load_profile(args.profile)
        tracker = GpuTracker(face_model, gaze_model)
        capture = open_camera(args.camera)
        try:
            if args.calibrate:
                run_calibration(tracker, capture, args.profile)
            run_headless(tracker, capture, args.profile, args.overlay_alpha, args.focus_radius)
        finally:
            capture.release()
    except (FileNotFoundError, GpuUnavailable, RuntimeError, ValueError) as exc:
        logging.exception("VIZZ stopped before headless content modification: %s", exc)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
