"""Run one visible calibration, then continue as a headless content modifier."""

from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

import cv2

from content_overlay import FocusOverlay
from gpu_tracker import GpuTracker, GpuUnavailable
from interaction_trace import InteractionTrace, read_pointer_position
from keyboard_activity import KeyboardActivity
from profile_model import load_profile, load_samples_for_merge, seal_profile


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_DIR = REPO_ROOT / ".vizz-models"
DEFAULT_PROFILE = REPO_ROOT / ".vizz-calibration.json"
DEFAULT_PRETRAINED_GAZE_MODEL = DEFAULT_MODEL_DIR / "mobileone_s0_gaze.onnx"
LOG_PATH = REPO_ROOT / ".vizz-runtime.log"
CONDITION_LABELS = {
    "with_glasses": "con lentes",
    "without_glasses": "sin lentes",
}


def open_camera(index: int) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"camera could not be opened: {index}")
    return capture


def run_calibration(
    tracker: GpuTracker,
    capture: cv2.VideoCapture,
    profile_path: Path,
    conditions: tuple[tuple[str, str], ...],
    merge_existing: Path | None,
    existing_condition: str | None,
) -> None:
    # Import the UI lazily so headless execution never imports a UI toolkit.
    from calibration_ui import CalibrationWindow

    result: dict[str, object] = {}
    existing_samples: list[dict[str, object]] = []
    existing_profile: dict[str, object] | None = None
    if merge_existing is not None:
        existing_profile, existing_samples = load_samples_for_merge(
            merge_existing,
            existing_condition=existing_condition,
        )
        if existing_profile.get("model_sha256") != tracker.face_model_sha256:
            raise ValueError("existing profile was created with a different face model")

    def sample_provider():
        ok, frame = capture.read()
        if not ok:
            return None
        return tracker.sample(frame)

    def complete(samples: list[dict[str, object]], screen_size: tuple[int, int]) -> None:
        merged_samples = list(existing_samples) + list(samples)
        if existing_profile is not None:
            previous_size = tuple(int(value) for value in existing_profile["screen_size"])
            if previous_size != screen_size:
                raise ValueError("existing profile and new calibration use different screen sizes")
        seal_profile(profile_path, screen_size, merged_samples, tracker.face_model_sha256)
        result["screen_size"] = screen_size

    CalibrationWindow(sample_provider, complete, conditions=conditions).run()
    if "screen_size" not in result:
        raise RuntimeError("calibration did not seal a profile")


def run_headless(
    tracker: GpuTracker,
    capture: cv2.VideoCapture,
    profile_path: Path,
    alpha: int,
    radius: int,
    trace_path: Path | None = None,
    trace_hz: float = 20.0,
    keyboard_trace: bool = False,
) -> None:
    profile, mapper = load_profile(profile_path)
    width, height = [int(value) for value in profile["screen_size"]]
    trace = (
        InteractionTrace(trace_path, (width, height), trace_hz, keyboard_activity_only=keyboard_trace)
        if trace_path is not None
        else None
    )
    keyboard = KeyboardActivity() if trace is not None and keyboard_trace else None
    try:
        if keyboard is not None:
            keyboard.start()
        next_trace_at = time.monotonic()
        with FocusOverlay(width, height, alpha=alpha, radius_px=radius) as overlay:
            logging.info("headless runtime active; visible_interface=False")
            while True:
                now = time.monotonic()
                ok, frame = capture.read()
                if not ok:
                    overlay.hide()
                    if trace is not None and now >= next_trace_at:
                        trace.write_sample(now, None, None, read_pointer_position(), keyboard.snapshot(now) if keyboard else None)
                        next_trace_at = now + 1.0 / trace.sample_hz
                    time.sleep(0.05)
                    continue
                sample = tracker.sample(frame)
                if sample is None or sample.quality < 0.50:
                    overlay.hide()
                    if trace is not None and now >= next_trace_at:
                        trace.write_sample(now, sample, None, read_pointer_position(), keyboard.snapshot(now) if keyboard else None)
                        next_trace_at = now + 1.0 / trace.sample_hz
                    continue
                point = mapper.predict(sample.features)
                overlay.set_focus(*point)
                overlay.pump_messages()
                if trace is not None and now >= next_trace_at:
                    trace.write_sample(now, sample, point, read_pointer_position(), keyboard.snapshot(now) if keyboard else None)
                    next_trace_at = now + 1.0 / trace.sample_hz
                time.sleep(0.01)
    except KeyboardInterrupt:
        logging.info("headless runtime stopped")
    finally:
        if trace is not None:
            trace.close()
        if keyboard is not None:
            keyboard.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FARMAKSIA VIZZ Python runtime")
    parser.add_argument("--calibrate", action="store_true", help="show the one-shot calibration UI first")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument(
        "--condition",
        choices=tuple(CONDITION_LABELS),
        default="without_glasses",
        help="condition captured when --merge-existing is used",
    )
    parser.add_argument(
        "--merge-existing",
        type=Path,
        default=None,
        help="append this existing calibration and refit one combined profile",
    )
    parser.add_argument(
        "--existing-condition",
        choices=tuple(CONDITION_LABELS),
        default=None,
        help="condition represented by a legacy profile being merged",
    )
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument(
        "--pretrained-gaze-model",
        type=Path,
        default=DEFAULT_PRETRAINED_GAZE_MODEL,
        help="GitHub yakhyo MobileOne S0 ONNX model used as an independent CUDA gaze signal",
    )
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--overlay-alpha", type=int, default=30)
    parser.add_argument("--focus-radius", type=int, default=260)
    parser.add_argument("--trace", type=Path, default=None, help="opt-in timestamp trace without video or screen content")
    parser.add_argument("--trace-hz", type=float, default=20.0, help="interaction trace rate")
    parser.add_argument(
        "--keyboard-trace",
        action="store_true",
        help="opt-in count-only keyboard activity; never stores key values or text",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    face_model = args.model_dir / "retinaface.onnx"
    gaze_model = args.model_dir / "gaze.onnx"
    try:
        if args.merge_existing is not None and not args.calibrate:
            raise ValueError("--merge-existing requires --calibrate")
        if args.merge_existing is not None and args.existing_condition is None:
            raise ValueError("--existing-condition is required when merging a legacy profile")
        if not args.calibrate:
            # A headless launch with a missing/invalid profile must fail before
            # it requests camera access.
            load_profile(args.profile)
        tracker = GpuTracker(face_model, gaze_model, args.pretrained_gaze_model)
        capture = open_camera(args.camera)
        try:
            if args.calibrate:
                if args.merge_existing is None:
                    conditions = (
                        ("with_glasses", CONDITION_LABELS["with_glasses"]),
                        ("without_glasses", CONDITION_LABELS["without_glasses"]),
                    )
                else:
                    conditions = ((args.condition, CONDITION_LABELS[args.condition]),)
                run_calibration(
                    tracker,
                    capture,
                    args.profile,
                    conditions,
                    args.merge_existing,
                    args.existing_condition,
                )
            run_headless(
                tracker,
                capture,
                args.profile,
                args.overlay_alpha,
                args.focus_radius,
                args.trace,
                args.trace_hz,
                args.keyboard_trace,
            )
        finally:
            capture.release()
    except (FileNotFoundError, GpuUnavailable, RuntimeError, ValueError) as exc:
        logging.exception("VIZZ stopped before headless content modification: %s", exc)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
