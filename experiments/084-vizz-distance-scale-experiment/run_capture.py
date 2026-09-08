"""Explicit P0 capture for VIZZ relative-distance scaling.

The first stage deliberately does not identify a credit card. A normal webcam
has no reliable object identity signal for a generic card. P0 is sealed
explicitly with SPACE while the GPU face detector reports one face and two eye
landmarks. Only the two facial rulers are used afterwards.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import math
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
TRACKER_DIR = HERE.parents[0] / "033-vizz-python-headless-runtime"
sys.path.insert(0, str(TRACKER_DIR))

from gpu_tracker import GpuTracker, GpuUnavailable  # noqa: E402
from scale_geometry import ScaleObservation, fuse_scale  # noqa: E402

REPO_ROOT = HERE.parents[1]
MODEL_DIR = REPO_ROOT / ".vizz-models"
DEFAULT_OUTPUT = REPO_ROOT / ".vizz-distance-scale-trace.jsonl"
WINDOW_NAME = "VIZZ 084 — escala relativa"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VIZZ 084 explicit face-geometry P0 capture")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--reference-seconds", type=float, default=2.0)
    parser.add_argument("--sample-hz", type=float, default=20.0)
    parser.add_argument("--model-dir", type=Path, default=MODEL_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--screen-width-mm", type=float, default=380.0)
    parser.add_argument("--screen-height-mm", type=float, default=210.0)
    parser.add_argument("--screen-width-px", type=int, default=2560)
    parser.add_argument("--screen-height-px", type=int, default=1440)
    parser.add_argument("--base-diameter-px", type=float, default=100.0)
    parser.add_argument("--fullscreen", action="store_true")
    return parser.parse_args()


def open_camera(index: int) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"camera could not be opened: {index}")
    return capture


def fullscreen_display_size(fallback: tuple[int, int]) -> tuple[int, int]:
    """Use the actual Windows desktop size for the visible preview."""

    try:
        user32 = ctypes.windll.user32
        width = int(user32.GetSystemMetrics(0))
        height = int(user32.GetSystemMetrics(1))
        if width > 0 and height > 0:
            return width, height
    except (AttributeError, OSError):
        pass
    return fallback


def fit_preview(frame: np.ndarray, display_size: tuple[int, int]) -> np.ndarray:
    display_width, display_height = display_size
    source_height, source_width = frame.shape[:2]
    scale = min(display_width / source_width, display_height / source_height)
    scaled_size = (max(1, round(source_width * scale)), max(1, round(source_height * scale)))
    resized = cv2.resize(frame, scaled_size, interpolation=cv2.INTER_LINEAR)
    canvas = np.full((display_height, display_width, 3), 24, dtype=np.uint8)
    offset_x = (display_width - scaled_size[0]) // 2
    offset_y = (display_height - scaled_size[1]) // 2
    canvas[offset_y : offset_y + scaled_size[1], offset_x : offset_x + scaled_size[0]] = resized
    return canvas


def observe_face(
    tracker: GpuTracker, frame: np.ndarray
) -> tuple[ScaleObservation | None, Any | None]:
    """Return the two facial rulers and raw geometry for a visual diagnostic."""

    try:
        detected = tracker.detect_face(frame)
    except (RuntimeError, ValueError, cv2.error):
        return None, None
    if detected is None:
        return None, None
    face, eyes = detected
    if len(eyes) != 2 or face.width <= 0.0:
        return None, None
    left_center = np.asarray(eyes[0].center, dtype=np.float32)
    right_center = np.asarray(eyes[1].center, dtype=np.float32)
    eye_distance = float(np.linalg.norm(right_center - left_center))
    if not math.isfinite(eye_distance) or eye_distance <= 0.0:
        return None, None
    try:
        observation = ScaleObservation(
            eye_distance_px=eye_distance,
            face_width_px=float(face.width),
            roll_deg=math.degrees(
                math.atan2(
                    float(right_center[1] - left_center[1]),
                    float(right_center[0] - left_center[0]),
                )
            ),
            eye_quality=float(face.score),
            face_quality=float(face.score),
        )
    except ValueError:
        return None, None
    return observation, (face, eyes)


def show_face_preview(
    frame: np.ndarray,
    observation: ScaleObservation | None,
    detected: Any | None,
    message: str,
    display_size: tuple[int, int],
) -> None:
    annotated = frame.copy()
    color = (0, 210, 0) if observation is not None else (0, 180, 255)
    if detected is not None:
        face, eyes = detected
        cv2.rectangle(
            annotated,
            (round(face.x1), round(face.y1)),
            (round(face.x2), round(face.y2)),
            color,
            2,
            lineType=cv2.LINE_AA,
        )
        for eye in eyes:
            center = (round(eye.center[0]), round(eye.center[1]))
            cv2.circle(annotated, center, 7, (255, 190, 0), -1, lineType=cv2.LINE_AA)
    if observation is not None:
        message = f"{message}  ojos={observation.eye_distance_px:.1f}px  cara={observation.face_width_px:.1f}px"
    cv2.putText(
        annotated,
        message,
        (16, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        color,
        2,
        lineType=cv2.LINE_AA,
    )
    cv2.putText(
        annotated,
        "P0: postura de referencia; ESPACIO = capturar; ESC = cancelar",
        (16, annotated.shape[0] - 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (255, 255, 255),
        1,
        lineType=cv2.LINE_AA,
    )
    cv2.imshow(WINDOW_NAME, fit_preview(annotated, display_size))


def draw_landolt_c(canvas: np.ndarray, diameter_px: float) -> None:
    height, width = canvas.shape[:2]
    center = (width // 2, height // 2)
    diameter = max(4, int(round(diameter_px)))
    radius = max(2, diameter // 2)
    stroke = max(1, int(round(diameter * 0.20)))
    cv2.circle(canvas, center, radius, (0, 0, 0), stroke, lineType=cv2.LINE_AA)
    gap = max(stroke, int(round(diameter * 0.20)))
    cv2.rectangle(
        canvas,
        (center[0], max(0, center[1] - gap // 2)),
        (min(width, center[0] + radius + stroke), min(height, center[1] + (gap + 1) // 2)),
        (255, 255, 255),
        -1,
    )


def render_target(
    width: int,
    height: int,
    diameter_px: float | None,
    status: str,
    fullscreen: bool,
) -> None:
    canvas = np.full((height, width, 3), 255, dtype=np.uint8)
    if diameter_px is not None:
        draw_landolt_c(canvas, diameter_px)
    cv2.putText(canvas, status, (32, 46), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (80, 80, 80), 2, lineType=cv2.LINE_AA)
    cv2.putText(canvas, "ESC = detener", (32, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 80, 80), 2, lineType=cv2.LINE_AA)
    cv2.imshow(WINDOW_NAME, canvas)
    if fullscreen:
        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


def collect_reference(
    capture: cv2.VideoCapture,
    tracker: GpuTracker,
    seconds: float,
    sample_hz: float,
    display_size: tuple[int, int],
) -> tuple[ScaleObservation, int]:
    eyes: list[float] = []
    faces: list[float] = []
    rolls: list[float] = []
    qualities: list[float] = []
    started = time.monotonic()
    next_sample = started
    while time.monotonic() - started < seconds:
        now = time.monotonic()
        if now < next_sample:
            time.sleep(min(0.005, next_sample - now))
            continue
        ok, frame = capture.read()
        next_sample = max(next_sample + 1.0 / sample_hz, time.monotonic())
        if not ok:
            continue
        observation, detected = observe_face(tracker, frame)
        show_face_preview(frame, observation, detected, "P0: capturando rostro y ojos", display_size)
        if cv2.waitKey(1) & 0xFF == 27:
            raise RuntimeError("P0 cancelled by user")
        if observation is None:
            continue
        eyes.append(observation.eye_distance_px)
        faces.append(observation.face_width_px)
        rolls.append(observation.roll_deg)
        qualities.append(observation.eye_quality)
    if len(eyes) < 3:
        raise RuntimeError(f"P0 needs at least three valid face samples; got {len(eyes)}")
    return (
        ScaleObservation(
            eye_distance_px=statistics.median(eyes),
            face_width_px=statistics.median(faces),
            roll_deg=statistics.median(rolls),
            eye_quality=max(0.05, statistics.median(qualities)),
            face_quality=max(0.05, statistics.median(qualities)),
        ),
        len(eyes),
    )


def write_json(stream: Any, payload: dict[str, Any]) -> None:
    stream.write(json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n")
    stream.flush()


def main() -> int:
    args = parse_args()
    for name, value in (
        ("duration", args.duration),
        ("reference-seconds", args.reference_seconds),
        ("sample-hz", args.sample_hz),
        ("screen-width-mm", args.screen_width_mm),
        ("screen-height-mm", args.screen_height_mm),
        ("base-diameter-px", args.base_diameter_px),
    ):
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"{name} must be finite and positive")
    if args.screen_width_px <= 0 or args.screen_height_px <= 0:
        raise ValueError("screen pixel dimensions must be positive")

    face_model = args.model_dir / "retinaface.onnx"
    tracker = GpuTracker(face_model, gaze_model=None, scale_only=True)
    capture = open_camera(args.camera)
    display_size = (
        fullscreen_display_size((args.screen_width_px, args.screen_height_px))
        if args.fullscreen
        else (640, 480)
    )
    screen_pixel_pitch_x = args.screen_width_mm / args.screen_width_px
    screen_pixel_pitch_y = args.screen_height_mm / args.screen_height_px
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    if args.fullscreen:
        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    reference: ScaleObservation | None = None
    reference_count = 0
    stream = None
    try:
        while reference is None:
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError("camera frame unavailable during P0")
            observation, detected = observe_face(tracker, frame)
            message = (
                "ROSTRO + 2 OJOS OK; ESPACIO = sellar P0"
                if observation is not None
                else "Buscando rostro y dos ojos"
            )
            show_face_preview(frame, observation, detected, message, display_size)
            key = cv2.waitKey(30) & 0xFF
            if key == 27:
                return 0
            if key == 32 and observation is not None:
                reference, reference_count = collect_reference(
                    capture, tracker, args.reference_seconds, args.sample_hz, display_size
                )
                render_target(
                    args.screen_width_px,
                    args.screen_height_px,
                    args.base_diameter_px,
                    f"P0 sellado ({reference_count} muestras); comienza el trabajo",
                    args.fullscreen,
                )
                cv2.waitKey(700)

        args.output.parent.mkdir(parents=True, exist_ok=True)
        stream = args.output.open("w", encoding="utf-8")
        write_json(
            stream,
            {
                "schema": "farmaxia:vizz-distance-scale-trace:0.3",
                "type": "header",
                "reference": reference.__dict__,
                "reference_source": "explicit_space_face_geometry",
                "card_role": "not_used_for_relative_scale",
                "screen": {
                    "width_mm": args.screen_width_mm,
                    "height_mm": args.screen_height_mm,
                    "width_px": args.screen_width_px,
                    "height_px": args.screen_height_px,
                    "pixel_pitch_x_mm": screen_pixel_pitch_x,
                    "pixel_pitch_y_mm": screen_pixel_pitch_y,
                },
                "relative_scale_only": True,
                "absolute_depth_requires_camera_intrinsics_or_measured_distance": True,
                "pose_correction": "not_available_in_current_tracker; keep_face_facing_camera",
                "raw_video": False,
                "camera_preview_during_p0": True,
                "camera_preview_after_p0": False,
                "screen_content_mutated": False,
                "input_injected": False,
                "text_persisted": False,
            },
        )
        started = time.monotonic()
        next_sample = started
        sample_count = valid_count = unknown_count = 0
        while time.monotonic() - started < args.duration:
            now = time.monotonic()
            if now < next_sample:
                if cv2.waitKey(1) & 0xFF == 27:
                    break
                time.sleep(min(0.005, next_sample - now))
                continue
            ok, frame = capture.read()
            timestamp = time.monotonic()
            next_sample = max(next_sample + 1.0 / args.sample_hz, timestamp)
            observation, _ = observe_face(tracker, frame) if ok else (None, None)
            row: dict[str, Any] = {
                "type": "sample",
                "t_monotonic": timestamp,
                "frame_read": bool(ok),
                "eye_distance_px": observation.eye_distance_px if observation else None,
                "face_width_px": observation.face_width_px if observation else None,
                "roll_deg": observation.roll_deg if observation else None,
                "quality": observation.eye_quality if observation else None,
                "scale": None,
                "target_diameter_px": None,
            }
            if observation is not None:
                estimate = fuse_scale(reference, observation)
                row["scale"] = estimate.as_dict()
                if estimate.status == "VALID":
                    valid_count += 1
                    target_diameter_px = args.base_diameter_px * float(estimate.relative_distance_ratio)
                    row["target_diameter_px"] = target_diameter_px
                    render_target(
                        args.screen_width_px,
                        args.screen_height_px,
                        target_diameter_px,
                        f"VALID  escala={estimate.fused_scale:.3f}  distancia_rel={estimate.relative_distance_ratio:.3f}",
                        args.fullscreen,
                    )
                else:
                    unknown_count += 1
                    render_target(args.screen_width_px, args.screen_height_px, None, "UNKNOWN: reglas incompatibles", args.fullscreen)
            else:
                unknown_count += 1
                render_target(args.screen_width_px, args.screen_height_px, None, "UNKNOWN: rostro no válido", args.fullscreen)
            write_json(stream, row)
            sample_count += 1
            if cv2.waitKey(1) & 0xFF == 27:
                break
        write_json(stream, {"type": "footer", "sample_count": sample_count, "valid_count": valid_count, "unknown_count": unknown_count, "raw_video": False, "screen_content_mutated": False})
    finally:
        capture.release()
        if stream is not None:
            stream.close()
        cv2.destroyAllWindows()
    print(json.dumps({"output": str(args.output), "reference_samples": reference_count, "reference_source": "explicit_space_face_geometry", "raw_video": False, "camera_preview_during_p0": True, "camera_preview_after_p0": False, "screen_content_mutated": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, GpuUnavailable, RuntimeError, ValueError) as exc:
        print(f"VIZZ_084_CAPTURE_NOT_STARTED: {exc}")
        raise SystemExit(2) from exc
