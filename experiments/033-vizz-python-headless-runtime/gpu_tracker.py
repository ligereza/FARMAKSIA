"""CUDA-only face/eye and gaze inference; no UI and no camera preview."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort


IRIS_IDX_481 = np.asarray([248, 252, 224, 228, 232, 236, 240, 244], dtype=np.int64)
GAZE_SIZE = 160


class GpuUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class Detection:
    score: float
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def center(self) -> tuple[float, float]:
        return ((self.x1 + self.x2) * 0.5, (self.y1 + self.y2) * 0.5)


@dataclass(frozen=True)
class GazeSample:
    features: tuple[float, float, float, float, float, float]
    quality: float
    disagreement_deg: float
    # Proxies derived from face/eye geometry; they are diagnostics for now and
    # are not yet fed into the screen mapper.
    pose: tuple[float, float, float, float, float, float] | None = None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def create_cuda_session(model_path: Path) -> ort.InferenceSession:
    if not model_path.is_file():
        raise FileNotFoundError(model_path)
    available = set(ort.get_available_providers())
    if "CUDAExecutionProvider" not in available:
        raise GpuUnavailable("CUDAExecutionProvider is not available")
    ort.preload_dlls()
    options = ort.SessionOptions()
    options.log_severity_level = 3
    options.add_session_config_entry("session.disable_cpu_ep_fallback", "1")
    try:
        session = ort.InferenceSession(
            str(model_path),
            sess_options=options,
            providers=["CUDAExecutionProvider"],
        )
    except Exception as exc:
        raise GpuUnavailable(f"CUDA session failed for {model_path.name}: {exc}") from exc
    if "CUDAExecutionProvider" not in session.get_providers():
        raise GpuUnavailable("session did not activate CUDAExecutionProvider")
    if session.get_session_options().get_session_config_entry("session.disable_cpu_ep_fallback") != "1":
        raise GpuUnavailable("CPU fallback was not disabled")
    return session


def _similarity_crop(image: np.ndarray, center: tuple[float, float], crop_size: float) -> tuple[np.ndarray, np.ndarray]:
    scale = GAZE_SIZE / max(1.0, crop_size)
    matrix = np.asarray(
        [
            [scale, 0.0, GAZE_SIZE * 0.5 - center[0] * scale],
            [0.0, scale, GAZE_SIZE * 0.5 - center[1] * scale],
        ],
        dtype=np.float32,
    )
    return cv2.warpAffine(image, matrix, (GAZE_SIZE, GAZE_SIZE), borderValue=0.0), matrix


def _transform_points3d(points: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    transformed = np.zeros_like(points, dtype=np.float32)
    scale = math.sqrt(float(matrix[0, 0] ** 2 + matrix[0, 1] ** 2))
    xy1 = np.concatenate([points[:, :2].astype(np.float32), np.ones((points.shape[0], 1), dtype=np.float32)], axis=1)
    transformed[:, :2] = xy1 @ matrix.T
    transformed[:, 2] = points[:, 2] * scale
    return transformed


def _angles_from_vec(vector: np.ndarray) -> tuple[float, float]:
    x, y, z = -vector[2], vector[1], -vector[0]
    theta = np.arctan2(y, x)
    phi = np.arctan2(np.sqrt(x**2 + y**2), z) - np.pi / 2
    return float(phi), float(theta)


def _angles_from_eye(eye: np.ndarray) -> tuple[float, float]:
    iris = eye[IRIS_IDX_481] - eye[:32].mean(axis=0)
    vector = iris.mean(axis=0)
    norm = np.linalg.norm(vector)
    if norm <= 1e-6:
        raise ValueError("gaze vector has zero norm")
    theta_x, theta_y = _angles_from_vec(vector / norm)
    return -theta_y * 180.0 / math.pi, theta_x * 180.0 / math.pi


class GpuTracker:
    """Minimal model pipeline extracted from the MIT screen-eye-tracking approach."""

    def __init__(self, face_model: Path, gaze_model: Path) -> None:
        self.face_model_sha256 = sha256(face_model)
        self.face = create_cuda_session(face_model)
        self.gaze = create_cuda_session(gaze_model)
        self.face_input = self.face.get_inputs()[0]
        self.face_output = self.face.get_outputs()[0]
        self.gaze_input = self.gaze.get_inputs()[0]
        self.gaze_output = self.gaze.get_outputs()[0]
        if self.face_input.name != "input" or list(self.face_input.shape) != [1, 3, 480, 640]:
            raise GpuUnavailable("unexpected RetinaFace input signature")
        if self.face_output.name != "batchno_classid_score_x1y1x2y2_landms":
            raise GpuUnavailable("unexpected RetinaFace output signature")
        if self.gaze_input.name != "input" or list(self.gaze_input.shape[1:]) != [3, 160, 160]:
            raise GpuUnavailable("unexpected gaze input signature")
        if self.gaze_output.name != "output" or list(self.gaze_output.shape[1:]) != [962, 3]:
            raise GpuUnavailable("unexpected gaze output signature")

    def detect_face(self, frame: np.ndarray) -> tuple[Detection, list[Detection]] | None:
        height, width = frame.shape[:2]
        resized = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_LINEAR)
        input_tensor = resized[..., ::-1].astype(np.float32)
        input_tensor = (input_tensor - np.asarray([104.0, 117.0, 123.0], dtype=np.float32)).transpose(2, 0, 1)[None]
        rows = self.face.run([self.face_output.name], {self.face_input.name: input_tensor})[0]
        if len(rows) == 0:
            return None
        rows = [row for row in rows if float(row[2]) >= 0.70]
        if not rows:
            return None
        row = max(rows, key=lambda item: float(item[2]))
        x1, y1, x2, y2 = [float(row[index]) for index in (3, 4, 5, 6)]
        face = Detection(
            float(row[2]),
            max(0.0, min(width - 1.0, x1 * width / 640.0)),
            max(0.0, min(height - 1.0, y1 * height / 480.0)),
            max(0.0, min(width - 1.0, x2 * width / 640.0)),
            max(0.0, min(height - 1.0, y2 * height / 480.0)),
        )
        left = (float(row[9]) * width / 640.0, float(row[10]) * height / 480.0)
        right = (float(row[7]) * width / 640.0, float(row[8]) * height / 480.0)
        eye_size = max(10.0, face.width * 0.08)
        eyes = [
            Detection(face.score, left[0] - eye_size / 2.0, left[1] - eye_size / 2.0, left[0] + eye_size / 2.0, left[1] + eye_size / 2.0),
            Detection(face.score, right[0] - eye_size / 2.0, right[1] - eye_size / 2.0, right[0] + eye_size / 2.0, right[1] + eye_size / 2.0),
        ]
        return face, sorted(eyes, key=lambda item: item.center[0])

    def sample(self, frame: np.ndarray) -> GazeSample | None:
        detected = self.detect_face(frame)
        if detected is None:
            return None
        face, eyes = detected
        left_eye, right_eye = eyes
        left_center = np.asarray(left_eye.center, dtype=np.float32)
        right_center = np.asarray(right_eye.center, dtype=np.float32)
        eye_center = tuple(((left_center + right_center) * 0.5).tolist())
        eye_distance = float(np.linalg.norm(right_center - left_center))
        crop_size = max(face.width / 1.5, eye_distance) * 1.5
        crop, matrix = _similarity_crop(frame, eye_center, crop_size)
        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        input_tensor = ((rgb.astype(np.float32).transpose(2, 0, 1)[None] / 255.0) - 0.5) / 0.5
        prediction = self.gaze.run([self.gaze_output.name], {self.gaze_input.name: input_tensor})[0][0]
        inverse = cv2.invertAffineTransform(matrix).astype(np.float32)
        points = _transform_points3d(prediction, inverse)
        left_points, right_points = points[:481].copy(), points[481:].copy()
        for eye in (left_points, right_points):
            eye[:, [0, 1]] = eye[:, [1, 0]]
        left_yaw, left_pitch = _angles_from_eye(left_points)
        right_yaw, right_pitch = _angles_from_eye(right_points)
        disagreement = math.hypot(left_yaw - right_yaw, left_pitch - right_pitch)
        if not all(math.isfinite(value) for value in (left_yaw, left_pitch, right_yaw, right_pitch)):
            return None
        if disagreement > 45.0:
            return None
        height, width = frame.shape[:2]
        quality = max(0.0, min(1.0, face.score * (1.0 - disagreement / 45.0)))
        face_center_x, face_center_y = face.center
        eye_roll = math.atan2(float(right_center[1] - left_center[1]), float(right_center[0] - left_center[0])) / math.pi
        pose = (
            face_center_x / max(1.0, width),
            face_center_y / max(1.0, height),
            face.width / max(1.0, width),
            face.height / max(1.0, height),
            eye_roll,
            eye_distance / max(1.0, width),
        )
        features = (
            (left_yaw + right_yaw) * 0.5 / 45.0,
            (left_pitch + right_pitch) * 0.5 / 30.0,
            left_yaw / 45.0,
            right_yaw / 45.0,
            eye_center[0] / max(1.0, width),
            eye_center[1] / max(1.0, height),
        )
        return GazeSample(features, quality, disagreement, pose)
