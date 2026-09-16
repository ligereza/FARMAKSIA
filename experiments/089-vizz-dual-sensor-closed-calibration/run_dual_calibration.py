"""One-session VIZZ calibration with a webcam and an oblique Hikvision stream.

The click closes a pre-click observation window.  It never starts sampling and
it is never used as gaze ground truth.  Both sensors run in one process and
the output keeps a numerical estimate even when one sensor is temporarily
unavailable.
"""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import random
import threading
import time
import tkinter as tk
from typing import Any, Callable

import cv2

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
TRACKER_DIR = REPO_ROOT / "experiments" / "033-vizz-python-headless-runtime"
import sys

sys.path.insert(0, str(TRACKER_DIR))
sys.path.insert(0, str(HERE))

from dual_contract import (  # noqa: E402
    CALIBRATION_POINTS,
    DEFAULT_RIDGE_LAMBDA,
    DualContractError,
    FEATURE_COUNT,
    MappingModel,
    evaluate_leave_one_target_out,
    fit_mapping,
    fuse_estimates,
    summarize_sensor_window,
)
from gpu_tracker import GpuTracker, GpuUnavailable  # noqa: E402
from stereo_geometry import StereoCalibration, StereoGeometryError, triangulate_point  # noqa: E402


DEFAULT_MODEL_DIR = REPO_ROOT / ".vizz-models"
DEFAULT_PRIOR = REPO_ROOT / ".vizz-calibration.json"
DEFAULT_PRETRAINED_GAZE = DEFAULT_MODEL_DIR / "mobileone_s0_gaze.onnx"
DEFAULT_OUTPUT_DIR = HERE / "output"
DEFAULT_SCREEN_WIDTH = 1707
DEFAULT_SCREEN_HEIGHT = 960
TARGET_RADIUS_PX = 92
SETTLE_SECONDS = 0.45
PRE_CLICK_WINDOW_SECONDS = 0.55
PRE_CLICK_GUARD_SECONDS = 0.18
MIN_TRIAL_AGE_SECONDS = 0.85
MIN_SENSOR_SAMPLES = 4
MAX_PAIR_SKEW_MS = 140.0
SAMPLE_HZ = 10.0
REPETITIONS = 2


@dataclass(frozen=True)
class SourceSpec:
    name: str
    label: str
    kind: str


SOURCE_SPECS = (
    SourceSpec("webcam", "webcam_visible", "webcam"),
    SourceSpec("hikvision", "hikvision_ir", "rtsp"),
)


def _finite(value: Any, fallback: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    return number if math.isfinite(number) else fallback


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--pretrained-gaze-model", type=Path, default=DEFAULT_PRETRAINED_GAZE, help="independent GitHub gaze model used as a GPU diagnostic")
    parser.add_argument("--disable-pretrained-gaze", action="store_true", help="do not load the independent gaze model")
    parser.add_argument("--prior-calibration", type=Path, default=DEFAULT_PRIOR)
    parser.add_argument("--stereo-calibration", type=Path, default=None, help="optional solved K/R/t JSON for metric eye triangulation")
    parser.add_argument("--output", type=Path, default=None, help="JSON output path; default is a timestamped file in this experiment's output folder")
    parser.add_argument("--webcam-index", type=int, default=0)
    parser.add_argument("--webcam-width", type=int, default=1280)
    parser.add_argument("--webcam-height", type=int, default=720)
    parser.add_argument("--sample-hz", type=float, default=SAMPLE_HZ)
    parser.add_argument("--repetitions", type=int, default=REPETITIONS)
    parser.add_argument("--seed", type=int, default=20260829)
    parser.add_argument("--screen-width", type=int, default=DEFAULT_SCREEN_WIDTH)
    parser.add_argument("--screen-height", type=int, default=DEFAULT_SCREEN_HEIGHT)
    parser.add_argument("--ir-state", choices=("on", "off", "unknown"), default="on")
    parser.add_argument("--optical-state", choices=("no_glasses", "with_glasses", "unknown"), default="no_glasses")
    parser.add_argument("--dry-run", action="store_true", help="print the contract without opening a camera or window")
    return parser.parse_args()


def default_output_path() -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    return DEFAULT_OUTPUT_DIR / f"vizz-dual-closed-calibration-{stamp}.json"


def rtsp_url_from_environment() -> str:
    direct = os.environ.get("VIZZ_RTSP_URL", "").strip()
    if direct:
        return direct
    host = os.environ.get("VIZZ_CAMERA_HOST", "").strip()
    user = os.environ.get("VIZZ_CAMERA_USER", "").strip()
    password = os.environ.get("VIZZ_CAMERA_PASSWORD", "")
    if not host or not user or not password:
        raise RuntimeError("define VIZZ_RTSP_URL or VIZZ_CAMERA_HOST/VIZZ_CAMERA_USER/VIZZ_CAMERA_PASSWORD")
    return f"rtsp://{user}:{password}@{host}:554/Streaming/Channels/101"


def open_webcam(index: int, width: int, height: int) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"webcam could not be opened: {index}")
    return capture


def _open_hikvision_capture(url: str) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError("Hikvision RTSP stream could not be opened")
    return capture


class ReconnectingHikvisionStream:
    """Keep an RTSP source alive without persisting its URL or video."""

    def __init__(
        self,
        url: str,
        *,
        opener: Callable[[str], Any] | None = None,
        max_consecutive_read_failures: int = 2,
    ) -> None:
        if not url or max_consecutive_read_failures < 1:
            raise ValueError("a non-empty URL and a positive failure threshold are required")
        self.url = url
        self._opener = opener or _open_hikvision_capture
        self.max_consecutive_read_failures = max_consecutive_read_failures
        self.capture: Any | None = None
        self.consecutive_read_failures = 0
        self.read_failures = 0
        self.reconnect_attempts = 0
        self.reconnect_successes = 0
        self.reconnect_failures = 0
        self.last_error: str | None = None
        self._open_initial()

    def _open_initial(self) -> None:
        try:
            self.capture = self._opener(self.url)
        except Exception as exc:
            self.last_error = type(exc).__name__
            raise

    def _reconnect(self) -> bool:
        self.reconnect_attempts += 1
        old_capture = self.capture
        self.capture = None
        if old_capture is not None:
            try:
                old_capture.release()
            except Exception:
                pass
        try:
            candidate = self._opener(self.url)
            if hasattr(candidate, "isOpened") and not candidate.isOpened():
                candidate.release()
                raise RuntimeError("Hikvision RTSP reconnect returned a closed stream")
            self.capture = candidate
            self.reconnect_successes += 1
            self.consecutive_read_failures = 0
            self.last_error = None
            return True
        except Exception as exc:
            self.reconnect_failures += 1
            self.last_error = type(exc).__name__
            return False

    def read(self) -> tuple[bool, Any | None]:
        if self.capture is None and not self._reconnect():
            self.read_failures += 1
            return False, None
        try:
            ok, frame = self.capture.read()
        except Exception as exc:
            self.last_error = type(exc).__name__
            ok, frame = False, None
        if ok and frame is not None:
            self.consecutive_read_failures = 0
            return True, frame
        self.read_failures += 1
        self.consecutive_read_failures += 1
        if self.consecutive_read_failures >= self.max_consecutive_read_failures:
            self._reconnect()
        return False, None

    def release(self) -> None:
        capture = self.capture
        self.capture = None
        if capture is not None:
            capture.release()

    def diagnostics(self) -> dict[str, Any]:
        return {
            "read_failures": self.read_failures,
            "consecutive_read_failures": self.consecutive_read_failures,
            "reconnect_attempts": self.reconnect_attempts,
            "reconnect_successes": self.reconnect_successes,
            "reconnect_failures": self.reconnect_failures,
            "last_error": self.last_error,
            "max_consecutive_read_failures": self.max_consecutive_read_failures,
        }


def open_hikvision() -> ReconnectingHikvisionStream:
    return ReconnectingHikvisionStream(rtsp_url_from_environment())


def _sample_payload(sample: Any, *, frame_width: int, frame_height: int, frame_read: bool, reason: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "frame_read": bool(frame_read),
        "quality": 0.0,
        "reason": reason,
        "features": None,
        "pose": None,
        "eye_distance_px": None,
        "eye_distance_to_face_width": None,
        "face_width_px": None,
        "face_height_px": None,
        "face_bbox_area_px2": None,
        "eye_center_norm": None,
        "eye_roll_norm": None,
        "binocular_gaze_deg": None,
        "pretrained_gaze_deg": None,
        "pretrained_gaze_unknown_reason": None,
        "raw_model_angle_delta_deg": None,
        "binocular_ray_proxy": None,
        "ir_optics": None,
        "eye_centers_px": None,
        "frame_size": [int(frame_width), int(frame_height)],
    }
    if sample is None:
        return payload
    try:
        features = [float(value) for value in sample.features]
        if len(features) != 6 or not all(math.isfinite(value) for value in features):
            return payload | {"reason": "invalid_features"}
        pose = [float(value) for value in sample.pose] if sample.pose is not None else None
        if pose is not None and (len(pose) != 6 or not all(math.isfinite(value) for value in pose)):
            pose = None
        ray = sample.binocular_ray_proxy.as_dict() if sample.binocular_ray_proxy is not None else None
        eye_centers_px = None
        if ray is not None and frame_width > 0 and frame_height > 0:
            scale = float(max(frame_width, frame_height))
            eye_centers_px = [
                [float(ray["left_origin"][0]) * scale + frame_width * 0.5, float(ray["left_origin"][1]) * scale + frame_height * 0.5],
                [float(ray["right_origin"][0]) * scale + frame_width * 0.5, float(ray["right_origin"][1]) * scale + frame_height * 0.5],
            ]
        payload.update(
            {
                "quality": _finite(sample.quality),
                "reason": reason,
                "features": features,
                "pose": pose,
                "eye_distance_px": pose[5] * frame_width if pose is not None else None,
                "eye_distance_to_face_width": (
                    (pose[5] / pose[2])
                    if pose is not None and pose[2] > 0.0
                    else None
                ),
                "face_width_px": pose[2] * frame_width if pose is not None else None,
                "face_height_px": pose[3] * frame_height if pose is not None else None,
                "face_bbox_area_px2": (
                    pose[2] * frame_width * pose[3] * frame_height
                    if pose is not None
                    else None
                ),
                "eye_center_norm": [features[4], features[5]],
                "eye_roll_norm": pose[4] if pose is not None else None,
                "binocular_gaze_deg": list(sample.binocular_gaze_deg) if sample.binocular_gaze_deg is not None else None,
                "pretrained_gaze_deg": list(sample.pretrained_gaze_deg) if sample.pretrained_gaze_deg is not None else None,
                "pretrained_gaze_unknown_reason": sample.pretrained_gaze_unknown_reason,
                "raw_model_angle_delta_deg": sample.raw_model_angle_delta_deg,
                "binocular_ray_proxy": ray,
                "ir_optics": [item.as_dict() for item in sample.ir_optics] if sample.ir_optics is not None else None,
                "eye_centers_px": eye_centers_px,
            }
        )
    except (AttributeError, TypeError, ValueError):
        return payload | {"reason": "sample_serialization_error"}
    return payload


class DualSampler:
    """Read both streams in one worker and retain only scalar summaries."""

    def __init__(self, tracker: GpuTracker, webcam: cv2.VideoCapture, hikvision: cv2.VideoCapture, sample_hz: float) -> None:
        if sample_hz <= 0.0 or not math.isfinite(sample_hz):
            raise ValueError("sample-hz must be finite and positive")
        self.tracker = tracker
        self.sources = {"webcam": webcam, "hikvision": hikvision}
        self.period = 1.0 / sample_hz
        self.buffer: deque[dict[str, Any]] = deque(maxlen=12000)
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.error: str | None = None

    def start(self) -> None:
        if self.thread is not None:
            raise RuntimeError("dual sampler already started")
        self.thread = threading.Thread(target=self._run, name="vizz-dual-sampler", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=3.0)

    def window(self, start: float, end: float) -> list[dict[str, Any]]:
        with self.lock:
            return [
                item
                for item in self.buffer
                if start <= float(item["t_monotonic"]) <= end
                and float(item["pair_skew_ms"]) <= MAX_PAIR_SKEW_MS
            ]

    def latest(self) -> dict[str, Any] | None:
        with self.lock:
            return dict(self.buffer[-1]) if self.buffer else None

    def diagnostics(self) -> dict[str, Any]:
        hikvision = self.sources.get("hikvision")
        return {
            "sampler_error": self.error,
            "hikvision": hikvision.diagnostics() if hasattr(hikvision, "diagnostics") else None,
        }

    def _read_sensor(self, name: str, capture: cv2.VideoCapture) -> tuple[float, dict[str, Any]]:
        timestamp = time.monotonic()
        ok, frame = capture.read()
        if not ok or frame is None:
            return timestamp, _sample_payload(None, frame_width=0, frame_height=0, frame_read=False, reason="frame_unavailable")
        height, width = frame.shape[:2]
        try:
            sample = self.tracker.sample(frame, enable_ir_optics=name == "hikvision")
            return timestamp, _sample_payload(sample, frame_width=width, frame_height=height, frame_read=True)
        except (RuntimeError, ValueError, cv2.error) as exc:
            return timestamp, _sample_payload(None, frame_width=width, frame_height=height, frame_read=True, reason=f"inference_{type(exc).__name__}")

    def _run(self) -> None:
        next_tick = time.monotonic()
        try:
            while not self.stop_event.is_set():
                now = time.monotonic()
                if now < next_tick:
                    self.stop_event.wait(min(0.01, next_tick - now))
                    continue
                webcam_t, webcam = self._read_sensor("webcam", self.sources["webcam"])
                hikvision_t, hikvision = self._read_sensor("hikvision", self.sources["hikvision"])
                record = {
                    "type": "paired_sample",
                    "t_monotonic": max(webcam_t, hikvision_t),
                    "pair_skew_ms": abs(webcam_t - hikvision_t) * 1000.0,
                    "sensors": {"webcam": webcam, "hikvision": hikvision},
                }
                with self.lock:
                    self.buffer.append(record)
                next_tick = max(next_tick + self.period, time.monotonic())
        except BaseException as exc:
            self.error = f"sampler_{type(exc).__name__}"


def _target_pixel(point: tuple[float, float], width: int, height: int) -> tuple[float, float]:
    return point[0] * width, point[1] * height


class DualCalibrationWindow:
    def __init__(self, sampler: DualSampler, *, width: int, height: int, repetitions: int, seed: int, output: Path, metadata: dict[str, Any], prior_mapper: Any | None, stereo_calibration: StereoCalibration | None) -> None:
        if repetitions < 1:
            raise ValueError("repetitions must be positive")
        self.sampler = sampler
        self.width = width
        self.height = height
        self.repetitions = repetitions
        self.output = output
        self.metadata = metadata
        self.prior_mapper = prior_mapper
        self.stereo_calibration = stereo_calibration
        self.rng = random.Random(seed)
        self.order = [(rep, index) for rep in range(1, repetitions + 1) for index in range(len(CALIBRATION_POINTS))]
        self.rng.shuffle(self.order)
        self.order_index = -1
        self.started = False
        self.state = "landing"
        self.presented_at = 0.0
        self.status_id: int | None = None
        self.target_ids: tuple[int, int] | None = None
        self.records: list[dict[str, Any]] = []
        self.root = tk.Tk()
        self.root.title("VIZZ — calibración dual")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#080808")
        self.root.protocol("WM_DELETE_WINDOW", self.abort)
        self.root.bind("<Escape>", lambda _event: self.abort())
        self.root.bind("<space>", lambda _event: self.start())
        # The cursor is a visible confirmation aid and remains interaction
        # input only; it is never used as gaze ground truth.
        self.canvas = tk.Canvas(self.root, bg="#080808", highlightthickness=0, cursor="arrow")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)
        self._draw_landing()

    def run(self) -> None:
        self.root.mainloop()

    def abort(self) -> None:
        self.state = "aborted"
        if self.root.winfo_exists():
            self.root.destroy()
        raise RuntimeError("dual calibration cancelled")

    def _on_resize(self, event: tk.Event[tk.Misc]) -> None:
        self.width = max(1, int(event.width))
        self.height = max(1, int(event.height))

    def _draw_landing(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_text(self.width // 2, self.height // 2 - 120, text="VIZZ · calibración dual", fill="#ffffff", font=("Segoe UI", 28, "bold"))
        self.canvas.create_text(self.width // 2, self.height // 2 - 65, text="Webcam + Hikvision IR · sin lentes · una sola sesión", fill="#c6c6c6", font=("Segoe UI", 16))
        self.canvas.create_text(self.width // 2, self.height // 2 - 25, text="Mira el punto durante un segundo y haz clic sobre él.", fill="#c6c6c6", font=("Segoe UI", 16))
        self.canvas.create_text(self.width // 2, self.height // 2 + 18, text="El clic cierra la medición anterior; no es la etiqueta de mirada.", fill="#8f8f8f", font=("Segoe UI", 13))
        self.canvas.create_text(self.width // 2, self.height // 2 + 88, text="ESPACIO = iniciar    ESC = cancelar", fill="#ffffff", font=("Segoe UI", 15, "bold"))

    def start(self) -> None:
        if self.started:
            return
        self.started = True
        self.state = "waiting_for_click"
        self.sampler.start()
        self._advance()

    def _advance(self) -> None:
        self.order_index += 1
        if self.order_index >= len(self.order):
            self._finish()
            return
        self.state = "waiting_for_click"
        self.presented_at = time.monotonic()
        self.canvas.delete("all")
        rep, target_index = self.order[self.order_index]
        point = CALIBRATION_POINTS[target_index]
        x, y = _target_pixel(point, self.width, self.height)
        self.target_ids = (
            self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="#d62027", outline="#ffffff", width=2),
            self.canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill="#ffffff", outline=""),
        )
        self.status_id = self.canvas.create_text(
            18,
            18,
            anchor="nw",
            text=f"mira el punto · repetición {rep}/{self.repetitions} · {self.order_index + 1}/{len(self.order)}",
            fill="#a8a8a8",
            font=("Segoe UI", 12),
        )

    def _on_click(self, event: tk.Event[tk.Misc]) -> None:
        if self.state != "waiting_for_click" or self.order_index < 0:
            return
        rep, target_index = self.order[self.order_index]
        target = CALIBRATION_POINTS[target_index]
        target_x, target_y = _target_pixel(target, self.width, self.height)
        click_distance = math.hypot(event.x - target_x, event.y - target_y)
        if click_distance > TARGET_RADIUS_PX:
            if self.status_id is not None:
                self.canvas.itemconfig(self.status_id, text="haz clic sobre el punto rojo")
            return
        click_time = time.monotonic()
        if click_time - self.presented_at < MIN_TRIAL_AGE_SECONDS:
            if self.status_id is not None:
                self.canvas.itemconfig(self.status_id, text="espera un segundo mirando el punto")
            return
        self.state = "processing"
        window_start = max(self.presented_at + SETTLE_SECONDS, click_time - PRE_CLICK_WINDOW_SECONDS - PRE_CLICK_GUARD_SECONDS)
        window_end = click_time - PRE_CLICK_GUARD_SECONDS
        paired = self.sampler.window(window_start, window_end)
        sensor_summaries: dict[str, dict[str, Any]] = {}
        for source in ("webcam", "hikvision"):
            rows = [pair["sensors"][source] for pair in paired]
            sensor_summaries[source] = summarize_sensor_window(rows, min_samples=MIN_SENSOR_SAMPLES)
        record: dict[str, Any] = {
            "type": "trial",
            "trial_id": self.order_index,
            "repetition": rep,
            "target_index": target_index,
            "target": [target[0], target[1]],
            "target_px": [target_x, target_y],
            "click_px": [int(event.x), int(event.y)],
            "click_error_px": click_distance,
            "presented_at": self.presented_at,
            "clicked_at": click_time,
            "pre_click_window": {
                "start": window_start,
                "end": window_end,
                "settle_seconds": SETTLE_SECONDS,
                "guard_seconds": PRE_CLICK_GUARD_SECONDS,
                "sample_count": len(paired),
                "max_pair_skew_ms": MAX_PAIR_SKEW_MS,
                "observed_pair_skew_ms": {
                    "median": _median_or_none([float(item["pair_skew_ms"]) for item in paired]),
                    "max": max((float(item["pair_skew_ms"]) for item in paired), default=None),
                },
            },
            "sensors": sensor_summaries,
            # This is a camera-space eye-centre diagnostic.  It must not be
            # mistaken for a screen-gaze prediction or metric stereo point.
            "eye_center_proxy": self._eye_center_proxy_for_trial(sensor_summaries),
            "stereo_geometry": self._stereo_for_trial(paired),
        }
        if self.prior_mapper is not None and sensor_summaries["webcam"].get("features") is not None:
            prior_point = self.prior_mapper.predict(sensor_summaries["webcam"]["features"])
            record["prior_webcam_prediction"] = {
                "screen": list(prior_point),
                "error_px": math.hypot((prior_point[0] - target[0]) * self.width, (prior_point[1] - target[1]) * self.height),
            }
        self.records.append(record)
        self._draw_acknowledged(record)
        self.root.after(180, self._advance)

    @staticmethod
    def _eye_center_proxy_for_trial(sensor_summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
        estimates: dict[str, tuple[float, float] | None] = {}
        qualities: dict[str, float] = {}
        for source, summary in sensor_summaries.items():
            features = summary.get("features")
            if features is None:
                estimates[source] = None
                continue
            estimates[source] = (float(features[4]), float(features[5]))
            qualities[source] = float(summary.get("quality_median", 0.5))
        fused = fuse_estimates(estimates, qualities=qualities)
        return {
            "mode": fused["mode"],
            "sensor_count": fused["sensor_count"],
            "eye_center_norm": fused["screen"],
            "confidence": fused["confidence"],
            "disagreement_norm": fused["disagreement"],
            "is_screen_prediction": False,
            "is_metric_3d": False,
        }

    def _stereo_for_trial(self, paired: list[dict[str, Any]]) -> dict[str, Any]:
        if self.stereo_calibration is None:
            return {
                "status": "FUSION_ONLY",
                "point_count": 0,
                "metric_depth_available": False,
                "reason": "stereo_calibration_not_configured",
            }
        depths: list[float] = []
        points: list[list[float]] = []
        for pair in paired:
            webcam_eyes = pair["sensors"]["webcam"].get("eye_centers_px")
            hikvision_eyes = pair["sensors"]["hikvision"].get("eye_centers_px")
            if not (isinstance(webcam_eyes, list) and isinstance(hikvision_eyes, list) and len(webcam_eyes) == 2 and len(hikvision_eyes) == 2):
                continue
            for eye_index in range(2):
                try:
                    result = triangulate_point(self.stereo_calibration, webcam_eyes[eye_index], hikvision_eyes[eye_index])
                except (StereoGeometryError, TypeError, ValueError, cv2.error):
                    continue
                depths.append(float(result["depth_camera_1"]))
                points.append(list(result["point_camera_1"]))
        if not depths:
            return {
                "status": "DEGRADED",
                "point_count": 0,
                "metric_depth_available": False,
                "reason": "no_valid_corresponding_eye_points",
            }
        return {
            "status": "METRIC_STEREO",
            "point_count": len(points),
            "metric_depth_available": True,
            "median_eye_depth_camera_1": _median_or_none(depths),
            "median_eye_point_camera_1": [
                _median_or_none([point[index] for point in points]) for index in range(3)
            ],
        }

    def _draw_acknowledged(self, record: dict[str, Any]) -> None:
        self.canvas.delete("all")
        target_x, target_y = record["target_px"]
        self.canvas.create_oval(target_x - 20, target_y - 20, target_x + 20, target_y + 20, fill="#e6a200", outline="#ffffff", width=2)
        self.canvas.create_oval(target_x - 6, target_y - 6, target_x + 6, target_y + 6, fill="#ffffff", outline="")

    def _finish(self) -> None:
        self.state = "finished"
        if self.root.winfo_exists():
            self.root.destroy()
        output_metadata = dict(self.metadata)
        output_metadata["sampler_diagnostics"] = self.sampler.diagnostics()
        payload = build_output(self.records, self.width, self.height, output_metadata, self.prior_mapper)
        self.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.output.with_suffix(self.output.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(self.output)
        print(json.dumps({"output": str(self.output), "trial_count": len(self.records), "analysis": payload["analysis"]}, ensure_ascii=False))


def _load_prior_mapper(path: Path, model_sha256: str, screen_size: tuple[int, int]) -> tuple[Any | None, dict[str, Any]]:
    if not path.is_file():
        return None, {"status": "not_found", "path": str(path)}
    try:
        from profile_model import ScreenMapper  # noqa: PLC0415

        profile = json.loads(path.read_text(encoding="utf-8"))
        compatible = (
            profile.get("schema") == "farmaxia:vizz-calibration-profile:0.4"
            and profile.get("raw_video") is False
            and profile.get("model_sha256") == model_sha256
            and isinstance(profile.get("mapping"), dict)
        )
        if not compatible:
            return None, {"status": "baseline_only_incompatible", "path": str(path), "sample_count": profile.get("sample_count")}
        return ScreenMapper(profile), {
            "status": "loaded_as_webcam_baseline",
            "path": str(path),
            "schema": profile.get("schema"),
            "sample_count": profile.get("sample_count"),
            "conditions": profile.get("calibration_conditions"),
            "reuse_policy": "comparison_only; current dual session is primary",
        }
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return None, {"status": "baseline_unreadable", "path": str(path), "reason": type(exc).__name__}


def _load_stereo_calibration(path: Path | None) -> tuple[StereoCalibration | None, dict[str, Any]]:
    if path is None:
        return None, {"status": "not_configured", "metric_triangulation": False}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        calibration = StereoCalibration.from_dict(payload)
        calibration.matrices()
        return calibration, {"status": "loaded", "path": str(path), "metric_triangulation": True}
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError, StereoGeometryError) as exc:
        return None, {"status": "invalid", "path": str(path), "reason": type(exc).__name__, "metric_triangulation": False}


def _sensor_records(records: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    materialized: list[dict[str, Any]] = []
    for record in records:
        summary = record.get("sensors", {}).get(source, {})
        features = summary.get("features")
        if not isinstance(features, list) or len(features) != 6:
            continue
        materialized.append(
            {
                "trial_id": int(record["trial_id"]),
                "target_index": int(record["target_index"]),
                "target": list(record["target"]),
                "features": features,
                "quality": float(summary.get("quality_median", 0.5)),
            }
        )
    return materialized


def _prior_metrics(records: list[dict[str, Any]], screen_size: tuple[int, int]) -> dict[str, Any]:
    errors = [float(record["prior_webcam_prediction"]["error_px"]) for record in records if "prior_webcam_prediction" in record]
    if not errors:
        return {"status": "not_available", "count": 0}
    import numpy as np

    return {
        "status": "measured_against_current_points",
        "count": len(errors),
        "median_error_px": float(np.median(errors)),
        "p95_error_px": float(np.percentile(errors, 95)),
        "screen_size": list(screen_size),
    }


def build_output(records: list[dict[str, Any]], width: int, height: int, metadata: dict[str, Any], prior_mapper: Any | None) -> dict[str, Any]:
    by_sensor = {source: _sensor_records(records, source) for source in ("webcam", "hikvision")}
    try:
        analysis = evaluate_leave_one_target_out(by_sensor, screen_size=(width, height), ridge_lambda=DEFAULT_RIDGE_LAMBDA)
    except DualContractError as exc:
        analysis = {"status": "degraded", "reason": str(exc), "screen_size": [width, height]}
    analysis["prior_webcam"] = _prior_metrics(records, (width, height))
    models: dict[str, Any] = {}
    fitted_models: dict[str, MappingModel] = {}
    for source, sensor_records in by_sensor.items():
        try:
            fitted = fit_mapping(sensor_records, ridge_lambda=DEFAULT_RIDGE_LAMBDA)
            fitted_models[source] = fitted
            models[source] = fitted.as_dict()
        except DualContractError as exc:
            models[source] = {"status": "degraded", "reason": str(exc), "sample_count": len(sensor_records)}
    annotated_trials = [_attach_current_session_prediction(record, fitted_models) for record in records]
    return {
        "schema": "farmaxia:vizz-dual-sensor-closed-calibration:0.2",
        "experiment": "089-vizz-dual-sensor-closed-calibration",
        "metadata": metadata,
        "screen": {"width_px": width, "height_px": height, "target_layout": "same_12_points_as_vizz_033"},
        "protocol": {
            "sources": ["webcam_visible", "hikvision_ir"],
            "new_calibration_for_each_sensor": True,
            "click_is_scheduler_only": True,
            "samples_are_pre_click": True,
            "raw_video": False,
            "screen_content_persisted": False,
            "input_injected": False,
            "always_numeric_output": True,
            "ir_optical_branch": "pupil_glint_diagnostic_on_hikvision",
            "ir_optical_branch_used_for_mapper": False,
            "triangulation_stage": "dual_calibration_and_cross_sensor_fusion; metric_stereo_requires_intrinsics_and_extrinsics",
        },
        "prior_calibration": metadata.get("prior_calibration"),
        "trials": annotated_trials,
        "sensor_models_current_session": models,
        "analysis": analysis,
        "unknowns": [
            "The current session does not yet contain a physical stereo-board solve for K/R/t; fusion is not metric 3-D triangulation.",
            "The IR pupil/glint branch is diagnostic and heuristic; it is not yet a calibrated gaze or depth measurement.",
            "Camera motion can be diagnosed by paired disagreement, but absolute camera drift requires a scene anchor or stereo recalibration.",
        ],
    }


def _attach_current_session_prediction(
    record: dict[str, Any],
    fitted_models: dict[str, MappingModel],
) -> dict[str, Any]:
    """Attach a numeric current-session screen diagnostic without hiding scope."""

    annotated = dict(record)
    estimates: dict[str, tuple[float, float] | None] = {}
    qualities: dict[str, float] = {}
    per_sensor: dict[str, dict[str, Any]] = {}
    sensors = record.get("sensors", {})
    for source, model in fitted_models.items():
        summary = sensors.get(source, {})
        features = summary.get("features")
        if not isinstance(features, list) or len(features) != FEATURE_COUNT:
            estimates[source] = None
            continue
        point = model.predict(features)
        estimates[source] = point
        quality = float(summary.get("quality_median", 0.5))
        qualities[source] = quality
        per_sensor[source] = {
            "screen": list(point),
            "quality": quality,
            "model_scope": "current_session_in_sample",
        }
    fused = fuse_estimates(estimates, qualities=qualities)
    annotated["current_session_prediction"] = {
        "screen": list(fused["screen"]),
        "mode": fused["mode"],
        "sensor_count": fused["sensor_count"],
        "confidence": fused["confidence"],
        "disagreement": fused["disagreement"],
        "per_sensor": per_sensor,
        "evaluation_scope": "current_session_in_sample_diagnostic",
        "is_held_out": False,
        "is_metric_3d": False,
    }
    return annotated


def _median_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    values = sorted(values)
    middle = len(values) // 2
    if len(values) % 2:
        return values[middle]
    return (values[middle - 1] + values[middle]) * 0.5


def dry_run_payload(args: argparse.Namespace) -> dict[str, Any]:
    order = [(rep, index) for rep in range(1, args.repetitions + 1) for index in range(len(CALIBRATION_POINTS))]
    random.Random(args.seed).shuffle(order)
    return {
        "schema": "farmaxia:vizz-dual-sensor-closed-calibration:0.2",
        "status": "DRY_RUN_NO_CAMERA",
        "target_count": len(CALIBRATION_POINTS),
        "trial_count": len(order),
        "order": order,
        "sources": ["webcam_visible", "hikvision_ir"],
        "samples_before_click": True,
        "click_is_scheduler_only": True,
        "always_numeric_output": True,
        "ir_optical_branch": "pupil_glint_diagnostic_on_hikvision",
        "ir_optical_branch_used_for_mapper": False,
        "raw_video": False,
        "screen_content_persisted": False,
        "input_injected": False,
    }


def main() -> int:
    args = parse_args()
    if args.repetitions < 1 or args.sample_hz <= 0.0:
        raise ValueError("repetitions and sample-hz must be positive")
    if args.screen_width <= 0 or args.screen_height <= 0:
        raise ValueError("screen dimensions must be positive")
    if args.dry_run:
        print(json.dumps(dry_run_payload(args), indent=2, ensure_ascii=False))
        return 0

    cv2.setNumThreads(1)
    face_model = args.model_dir / "retinaface.onnx"
    gaze_model = args.model_dir / "gaze.onnx"
    pretrained_gaze_model = None if args.disable_pretrained_gaze else args.pretrained_gaze_model
    tracker = GpuTracker(face_model, gaze_model, pretrained_gaze_model=pretrained_gaze_model)
    prior_mapper, prior_info = _load_prior_mapper(args.prior_calibration, tracker.face_model_sha256, (args.screen_width, args.screen_height))
    stereo_calibration, stereo_info = _load_stereo_calibration(args.stereo_calibration)
    webcam = open_webcam(args.webcam_index, args.webcam_width, args.webcam_height)
    hikvision = open_hikvision()
    sampler = DualSampler(tracker, webcam, hikvision, args.sample_hz)
    output = args.output or default_output_path()
    metadata = {
        "optical_state": args.optical_state,
        "ir_state": args.ir_state,
        "camera_layout": "hikvision_oblique_plus_laptop_webcam",
        "camera_stream": "hikvision_main_101",
        "sample_hz": args.sample_hz,
        "repetitions": args.repetitions,
        "seed": args.seed,
        "model_sha256": tracker.face_model_sha256,
        "pretrained_gaze_model": (
            str(args.pretrained_gaze_model)
            if not args.disable_pretrained_gaze
            else None
        ),
        "prior_calibration": prior_info,
        "stereo_calibration": stereo_info,
        "ir_optical_branch": "pupil_glint_diagnostic_on_hikvision",
        "ir_optical_branch_used_for_mapper": False,
        "credentials_persisted": False,
    }
    try:
        DualCalibrationWindow(
            sampler,
            width=args.screen_width,
            height=args.screen_height,
            repetitions=args.repetitions,
            seed=args.seed,
            output=output,
            metadata=metadata,
            prior_mapper=prior_mapper,
            stereo_calibration=stereo_calibration,
        ).run()
    finally:
        sampler.stop()
        webcam.release()
        hikvision.release()
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, GpuUnavailable, RuntimeError, ValueError, DualContractError) as exc:
        print(f"VIZZ_089_NOT_STARTED: {exc}")
        raise SystemExit(2) from exc
