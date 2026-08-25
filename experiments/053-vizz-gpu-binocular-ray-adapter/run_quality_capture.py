"""Passive CUDA quality capture; no calibration UI, preview or screen mutation."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import cv2

TRACKER_DIR = Path(__file__).resolve().parents[1] / "033-vizz-python-headless-runtime"
sys.path.insert(0, str(TRACKER_DIR))

from gpu_tracker import GpuTracker, GpuUnavailable
from interaction_trace import read_pointer_position
from keyboard_activity import KeyboardActivity


REPO_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_ROOT / ".vizz-models"
DEFAULT_OUTPUT = REPO_ROOT / ".vizz-binocular-quality.jsonl"


def open_camera(index: int, width: int, height: int) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"camera could not be opened: {index}")
    return capture


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VIZZ passive binocular quality capture")
    parser.add_argument("--seconds", type=float, default=30.0)
    parser.add_argument("--sample-hz", type=float, default=20.0)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--model-dir", type=Path, default=MODEL_DIR)
    parser.add_argument("--pretrained-gaze-model", type=Path, default=MODEL_DIR / "mobileone_s0_gaze.onnx")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pointer", action="store_true", help="store OS pointer position as an auxiliary covariate")
    parser.add_argument("--keyboard", action="store_true", help="count keyboard activity without storing key identity or text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.seconds <= 0.0 or args.sample_hz <= 0.0:
        raise ValueError("seconds and sample-hz must be positive")
    if args.width <= 0 or args.height <= 0:
        raise ValueError("capture dimensions must be positive")

    face_model = args.model_dir / "retinaface.onnx"
    gaze_model = args.model_dir / "gaze.onnx"
    # Construct CUDA sessions before opening the camera: unavailable GPU
    # fails without requesting camera permission or starting capture.
    tracker = GpuTracker(face_model, gaze_model, args.pretrained_gaze_model)
    capture = open_camera(args.camera, args.width, args.height)
    keyboard = KeyboardActivity() if args.keyboard else None
    try:
        if keyboard is not None:
            keyboard.start()
    except BaseException:
        capture.release()
        raise
    args.output.parent.mkdir(parents=True, exist_ok=True)
    stream = args.output.open("w", encoding="utf-8")
    started = time.monotonic()
    deadline = started + args.seconds
    next_sample = started
    sample_count = 0
    valid_count = 0
    ray_valid_count = 0
    ray_unknown_count = 0
    keyboard_event_count_total = 0
    keyboard_active_sample_count = 0
    stream.write(
        json.dumps(
            {
                "schema": "farmaxia:vizz-binocular-quality-trace:0.2",
                "type": "header",
                "sample_hz": args.sample_hz,
                "camera_size": [args.width, args.height],
                "pointer_recorded": bool(args.pointer),
                "keyboard_activity_only": bool(args.keyboard),
                "raw_video": False,
                "screen_content": False,
                "screen_content_mutated": False,
                "mouse_is_ground_truth": False,
                "key_values_persisted": False,
                "text_persisted": False,
            },
            separators=(",", ":"),
        )
        + "\n"
    )
    stream.flush()
    try:
        while time.monotonic() < deadline:
            now = time.monotonic()
            if now < next_sample:
                time.sleep(min(0.005, next_sample - now))
                continue
            ok, frame = capture.read()
            timestamp = time.monotonic()
            next_sample = max(next_sample + 1.0 / args.sample_hz, timestamp)
            sample = tracker.sample(frame) if ok else None
            ray = getattr(sample, "binocular_ray_proxy", None) if sample is not None else None
            ray_payload = ray.as_dict() if ray is not None else None
            ray_reason = getattr(sample, "binocular_ray_unknown_reason", None) if sample is not None else "camera_frame_unavailable"
            if sample is not None:
                valid_count += 1
            if ray_payload is not None:
                ray_valid_count += 1
            else:
                ray_unknown_count += 1
            keyboard_state = keyboard.snapshot(timestamp) if keyboard is not None else {
                "keyboard_event_count": 0,
                "keyboard_active": False,
                "keyboard_last_event_age_ms": None,
            }
            keyboard_event_count_total += int(keyboard_state["keyboard_event_count"])
            keyboard_active_sample_count += int(bool(keyboard_state["keyboard_active"]))
            payload = {
                "type": "sample",
                "t_monotonic": timestamp,
                "frame_read": bool(ok),
                "quality": float(sample.quality) if sample is not None else None,
                "disagreement_deg": float(sample.disagreement_deg) if sample is not None else None,
                "pose": list(sample.pose) if sample is not None and sample.pose is not None else None,
                "eye_centric_distance_px": (
                    float(sample.eye_centric_distance_px)
                    if sample is not None and sample.eye_centric_distance_px is not None
                    else None
                ),
                "binocular_gaze_deg": list(sample.binocular_gaze_deg) if sample is not None and sample.binocular_gaze_deg is not None else None,
                "binocular_ray_proxy": ray_payload,
                "binocular_ray_unknown_reason": ray_reason,
                "mouse_screen": list(read_pointer_position()) if args.pointer else None,
                "keyboard_event_count": keyboard_state["keyboard_event_count"],
                "keyboard_active": keyboard_state["keyboard_active"],
                "keyboard_last_event_age_ms": keyboard_state["keyboard_last_event_age_ms"],
            }
            stream.write(json.dumps(payload, separators=(",", ":")) + "\n")
            stream.flush()
            sample_count += 1
    except KeyboardInterrupt:
        pass
    finally:
        capture.release()
        if keyboard is not None:
            keyboard.close()
        stream.write(
            json.dumps(
                {
                    "type": "footer",
                    "sample_count": sample_count,
                    "valid_sample_count": valid_count,
                    "ray_valid_count": ray_valid_count,
                    "ray_unknown_count": ray_unknown_count,
                    "keyboard_event_count_total": keyboard_event_count_total,
                    "keyboard_active_sample_count": keyboard_active_sample_count,
                    "keyboard_activity_only": bool(args.keyboard),
                    "raw_video": False,
                    "screen_content_mutated": False,
                },
                separators=(",", ":"),
            )
            + "\n"
        )
        stream.close()
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sample_count": sample_count,
                "valid_sample_count": valid_count,
                "ray_valid_count": ray_valid_count,
                "ray_unknown_count": ray_unknown_count,
                "keyboard_event_count_total": keyboard_event_count_total,
                "keyboard_active_sample_count": keyboard_active_sample_count,
                "keyboard_activity_only": bool(args.keyboard),
                "raw_video": False,
                "screen_content_mutated": False,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, GpuUnavailable, RuntimeError, ValueError) as exc:
        print(f"VIZZ_CAPTURE_NOT_STARTED: {exc}")
        raise SystemExit(2) from exc
