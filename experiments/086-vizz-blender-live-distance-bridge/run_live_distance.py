"""Stream consented webcam distance geometry to the Blender 085 scene.

The process writes one local JSON state atomically. It does not use sockets,
network access, input injection, raw-video persistence or external assets.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import cv2


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
CAPTURE_DIR = REPO_ROOT / "experiments" / "084-vizz-distance-scale-experiment"
TRACKER_DIR = REPO_ROOT / "experiments" / "033-vizz-python-headless-runtime"
MODEL_DIR = REPO_ROOT / ".vizz-models"
DEFAULT_CONTROL = HERE / "output" / "vizz-blender-control.json"
DEFAULT_TRACE = HERE / "output" / "vizz-blender-distance-trace.jsonl"
DEFAULT_REFERENCE_DISTANCE_M = 0.60
DEFAULT_FOCUS_MODE = "locked"
SCHEMA = "farmaxia:vizz-blender-live-distance:0.1"

sys.path.insert(0, str(TRACKER_DIR))
sys.path.insert(0, str(CAPTURE_DIR))

from gpu_tracker import GpuTracker, GpuUnavailable  # noqa: E402
from scale_geometry import ScaleObservation, ScaleContractError, fuse_scale  # noqa: E402


def load_capture_helpers() -> Any:
    spec = importlib.util.spec_from_file_location("vizz084_capture_helpers", CAPTURE_DIR / "run_capture.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load VIZZ 084 capture helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VIZZ webcam to Blender local distance bridge")
    parser.add_argument(
        "--reference-distance-m",
        type=float,
        default=DEFAULT_REFERENCE_DISTANCE_M,
        help="virtual Blender baseline in meters; not a physical measurement (default: 0.60)",
    )
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument(
        "--focus-mode",
        choices=("locked", "screen"),
        default=DEFAULT_FOCUS_MODE,
        help="locked keeps the virtual focus at P0 to show defocus; screen follows the monitor",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="optional bounded runtime in seconds; omit it to run until Ctrl+C",
    )
    parser.add_argument("--reference-seconds", type=float, default=2.0)
    parser.add_argument("--sample-hz", type=float, default=20.0)
    parser.add_argument("--model-dir", type=Path, default=MODEL_DIR)
    parser.add_argument("--control-file", type=Path, default=DEFAULT_CONTROL)
    parser.add_argument("--trace-file", type=Path, default=DEFAULT_TRACE)
    parser.add_argument("--no-trace", action="store_true")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    for name, value in (
        ("reference-distance-m", args.reference_distance_m),
        ("reference-seconds", args.reference_seconds),
        ("sample-hz", args.sample_hz),
    ):
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"{name} must be finite and positive")
    if args.duration is not None and (not math.isfinite(args.duration) or args.duration <= 0.0):
        raise ValueError("duration must be finite and positive when provided")


def open_camera(index: int) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"camera could not be opened: {index}")
    return capture


def atomic_write(path: Path, payload: dict[str, Any]) -> bool:
    """Replace the state atomically, tolerating transient Windows file locks."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    serialized = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    for attempt in range(20):
        try:
            temporary.write_text(serialized, encoding="utf-8")
            temporary.replace(path)
            return True
        except PermissionError:
            if attempt == 19:
                try:
                    temporary.unlink()
                except FileNotFoundError:
                    pass
                return False
            time.sleep(0.025)
    return False


def append_trace(stream: Any | None, payload: dict[str, Any]) -> None:
    if stream is not None:
        stream.write(json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n")
        stream.flush()


def stable_reference(
    capture: cv2.VideoCapture,
    tracker: GpuTracker,
    helpers: Any,
    seconds: float,
    sample_hz: float,
) -> tuple[ScaleObservation, int]:
    cv2.namedWindow(helpers.WINDOW_NAME, cv2.WINDOW_NORMAL)
    display_size = helpers.fullscreen_display_size((640, 480))
    eye_values: list[float] = []
    face_values: list[float] = []
    roll_values: list[float] = []
    quality_values: list[float] = []
    deadline = time.monotonic() + seconds
    next_sample = time.monotonic()
    while time.monotonic() < deadline:
        now = time.monotonic()
        if now < next_sample:
            time.sleep(min(0.005, next_sample - now))
            continue
        ok, frame = capture.read()
        next_sample = max(next_sample + 1.0 / sample_hz, time.monotonic())
        if not ok:
            continue
        observation, detected = helpers.observe_face(tracker, frame)
        helpers.show_face_preview(frame, observation, detected, "P0: capturando referencia estable", display_size)
        if cv2.waitKey(1) & 0xFF == 27:
            raise RuntimeError("P0 cancelled by user")
        if observation is not None:
            eye_values.append(observation.eye_distance_px)
            face_values.append(observation.face_width_px)
            roll_values.append(observation.roll_deg)
            quality_values.append(observation.eye_quality)
    if len(eye_values) < 3:
        raise RuntimeError(f"P0 needs at least three valid samples; got {len(eye_values)}")
    return (
        ScaleObservation(
            eye_distance_px=statistics.median(eye_values),
            face_width_px=statistics.median(face_values),
            roll_deg=statistics.median(roll_values),
            eye_quality=max(0.05, statistics.median(quality_values)),
            face_quality=max(0.05, statistics.median(quality_values)),
        ),
        len(eye_values),
    )


def make_state(
    timestamp: float,
    status: str,
    reference_distance_m: float,
    *,
    focus_mode: str,
    estimate: Any | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    valid = status == "VALID" and estimate is not None and estimate.relative_distance_ratio is not None
    distance = reference_distance_m * float(estimate.relative_distance_ratio) if valid else None
    focus_distance = reference_distance_m if valid and focus_mode == "locked" else distance
    if distance is not None and (not math.isfinite(distance) or not 0.20 <= distance <= 3.00):
        valid = False
        status = "UNKNOWN"
        reason = "distance_outside_safe_bridge_domain"
        distance = None
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "type": "state",
        "timestamp_monotonic": timestamp,
        "status": status,
        "unknown_reason": reason,
        "source": "gpu_face_geometry_relative_scale",
        "reference_distance_m": reference_distance_m,
        "observer_distance_m": distance,
        "focus_mode": focus_mode,
        "focus_distance_m": focus_distance,
        "focus_offset_m": 0.0 if valid else None,
        "input_injected": False,
        "network_used": False,
        "raw_video": False,
    }
    if estimate is not None:
        payload["scale"] = estimate.as_dict()
    return payload


def main() -> int:
    args = parse_args()
    validate_args(args)
    helpers = load_capture_helpers()
    face_model = args.model_dir / "retinaface.onnx"
    tracker = GpuTracker(face_model, gaze_model=None, scale_only=True)
    capture = open_camera(args.camera)
    trace = None
    reference: ScaleObservation | None = None
    reference_count = 0
    try:
        cv2.namedWindow(helpers.WINDOW_NAME, cv2.WINDOW_NORMAL)
        while reference is None:
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError("camera frame unavailable during P0")
            observation, detected = helpers.observe_face(tracker, frame)
            message = "ROSTRO + 2 OJOS OK; ESPACIO = sellar P0" if observation is not None else "Buscando rostro y dos ojos"
            helpers.show_face_preview(frame, observation, detected, message, helpers.fullscreen_display_size((640, 480)))
            key = cv2.waitKey(30) & 0xFF
            if key == 27:
                return 0
            if key == 32 and observation is not None:
                reference, reference_count = stable_reference(
                    capture, tracker, helpers, args.reference_seconds, args.sample_hz
                )
        cv2.destroyWindow(helpers.WINDOW_NAME)
        if not args.no_trace:
            args.trace_file.parent.mkdir(parents=True, exist_ok=True)
            trace = args.trace_file.open("w", encoding="utf-8")
        header = {
            "schema": SCHEMA,
            "type": "header",
            "reference": reference.__dict__,
            "reference_samples": reference_count,
            "reference_distance_m": args.reference_distance_m,
            "control_file": str(args.control_file.resolve()),
            "raw_video": False,
            "network_used": False,
            "input_injected": False,
        }
        append_trace(trace, header)
        atomic_write(args.control_file, {
            **header,
            "type": "state",
            "status": "READY",
            "observer_distance_m": args.reference_distance_m,
            "focus_mode": args.focus_mode,
            "focus_distance_m": args.reference_distance_m,
            "focus_offset_m": 0.0,
            "unknown_reason": None,
        })
        started = time.monotonic()
        next_sample = started
        sample_count = valid_count = unknown_count = 0
        control_write_failures = 0
        deadline = None if args.duration is None else started + args.duration
        while deadline is None or time.monotonic() < deadline:
            now = time.monotonic()
            if now < next_sample:
                time.sleep(min(0.005, next_sample - now))
                continue
            ok, frame = capture.read()
            timestamp = time.monotonic()
            next_sample = max(next_sample + 1.0 / args.sample_hz, timestamp)
            observation, _ = helpers.observe_face(tracker, frame) if ok else (None, None)
            estimate = None
            status = "UNKNOWN"
            reason = "face_observation_missing"
            if observation is not None:
                try:
                    estimate = fuse_scale(reference, observation)
                    status = estimate.status
                    reason = None if status == "VALID" else "facial_rulers_disagree"
                except ScaleContractError as exc:
                    reason = str(exc)
            state = make_state(
                timestamp,
                status,
                args.reference_distance_m,
                focus_mode=args.focus_mode,
                estimate=estimate,
                reason=reason,
            )
            if atomic_write(args.control_file, state):
                if control_write_failures:
                    print("VIZZ_086_CONTROL_WRITE_RECOVERED")
                control_write_failures = 0
            else:
                control_write_failures += 1
                if control_write_failures == 1:
                    print("VIZZ_086_CONTROL_WRITE_LOCKED_RETRYING")
            append_trace(trace, state)
            sample_count += 1
            if state["status"] == "VALID":
                valid_count += 1
            else:
                unknown_count += 1
        footer = {
            "schema": SCHEMA,
            "type": "footer",
            "sample_count": sample_count,
            "valid_count": valid_count,
            "unknown_count": unknown_count,
            "raw_video": False,
            "network_used": False,
            "input_injected": False,
        }
        append_trace(trace, footer)
        print(json.dumps({"status": "VIZZ_BLENDER_LIVE_DISTANCE_FINISHED", **footer}, ensure_ascii=False))
        return 0
    finally:
        capture.release()
        cv2.destroyAllWindows()
        if trace is not None:
            trace.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("VIZZ_086_STOPPED_BY_USER")
    except (FileNotFoundError, GpuUnavailable, RuntimeError, ValueError) as exc:
        print(f"VIZZ_086_NOT_STARTED: {exc}")
        raise SystemExit(2) from exc
