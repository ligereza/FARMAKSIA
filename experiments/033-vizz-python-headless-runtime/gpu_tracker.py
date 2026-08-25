"""CUDA-only face/eye and gaze inference; no UI and no camera preview."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort

from pretrained_gaze import decode_mobileone_angles, preprocess_mobileone_face
from ray_proxy import BinocularRayProxy, build_binocular_ray_proxy


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
    # Eye-centric diagnostics are captured alongside legacy features but are
    # not yet used by the screen mapper.
    eye_centric: tuple[float, ...] | None = None
    eye_centric_distance_px: float | None = None
    eye_centric_roll_rad: float | None = None
    eye_centric_unknown_reason: str | None = None
    # Independent full-face gaze model from the GitHub yakhyo/gaze-estimation
    # MobileOne S0 release. It is diagnostic until a profile is calibrated for
    # this representation; it is never silently converted to screen pixels.
    pretrained_gaze_deg: tuple[float, float] | None = None
    pretrained_gaze_unknown_reason: str | None = None
    binocular_gaze_deg: tuple[float, float] | None = None
    raw_model_angle_delta_deg: float | None = None
    # Explicit eye-specific rays in a normalized camera proxy frame.  These
    # are not metric world rays until intrinsics, eye depth and head pose are
    # independently solved.
    binocular_ray_proxy: BinocularRayProxy | None = None
    binocular_ray_unknown_reason: str | None = None


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


def _eye_centric_geometry(
    left_points: np.ndarray, right_points: np.ndarray
) -> tuple[tuple[float, ...], float, float] | tuple[None, None, str]:
    """Return iris centroids in an interocular frame, or an UNKNOWN reason."""

    if left_points.ndim != 2 or right_points.ndim != 2 or left_points.shape[1] != 3 or right_points.shape[1] != 3:
        return None, None, "invalid_eye_point_shape"
    left_center = left_points[:32].mean(axis=0)
    right_center = right_points[:32].mean(axis=0)
    delta = right_center[:2] - left_center[:2]
    distance = float(np.linalg.norm(delta))
    if not math.isfinite(distance) or distance <= 1e-6:
        return None, None, "interocular_distance_too_small"
    roll = float(math.atan2(float(delta[1]), float(delta[0])))
    cosine = math.cos(roll)
    sine = math.sin(roll)
    midpoint = (left_center + right_center) * 0.5

    def iris_in_frame(points: np.ndarray) -> np.ndarray:
        centered = points[IRIS_IDX_481] - midpoint
        normalized = np.empty_like(centered, dtype=np.float32)
        normalized[:, 0] = cosine * centered[:, 0] + sine * centered[:, 1]
        normalized[:, 1] = -sine * centered[:, 0] + cosine * centered[:, 1]
        normalized[:, 2] = centered[:, 2]
        return normalized.mean(axis=0) / distance

    values = tuple(float(value) for value in np.concatenate((iris_in_frame(left_points), iris_in_frame(right_points))))
    if not all(math.isfinite(value) for value in values):
        return None, None, "nonfinite_eye_centric_geometry"
    return values, distance, roll


class GpuTracker:
    """Minimal model pipeline extracted from the MIT screen-eye-tracking approach."""

    def __init__(self, face_model: Path, gaze_model: Path, pretrained_gaze_model: Path | None = None) -> None:
        self.face_model_sha256 = sha256(face_model)
        self.face = create_cuda_session(face_model)
        self.gaze = create_cuda_session(gaze_model)
        self.pretrained_gaze = create_cuda_session(pretrained_gaze_model) if pretrained_gaze_model is not None else None
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
        self.pretrained_input = None
        self.pretrained_yaw_output = None
        self.pretrained_pitch_output = None
        if self.pretrained_gaze is not None:
            self.pretrained_input = self.pretrained_gaze.get_inputs()[0]
            outputs = {output.name: output for output in self.pretrained_gaze.get_outputs()}
            if list(self.pretrained_input.shape) != [1, 3, 448, 448]:
                raise GpuUnavailable("unexpected MobileOne input signature")
            if not {"yaw", "pitch"}.issubset(outputs):
                raise GpuUnavailable("unexpected MobileOne output names")
            if list(outputs["yaw"].shape) != [1, 90] or list(outputs["pitch"].shape) != [1, 90]:
                raise GpuUnavailable("unexpected MobileOne output signature")
            self.pretrained_yaw_output = outputs["yaw"]
            self.pretrained_pitch_output = outputs["pitch"]
            try:
                zero_tensor = np.zeros((1, 3, 448, 448), dtype=np.float32)
                zero_outputs = self.pretrained_gaze.run(
                    [self.pretrained_yaw_output.name, self.pretrained_pitch_output.name],
                    {self.pretrained_input.name: zero_tensor},
                )
                decode_mobileone_angles(zero_outputs[0], zero_outputs[1])
            except Exception as exc:
                raise GpuUnavailable(f"MobileOne CUDA preflight failed: {exc}") from exc

    def _predict_pretrained_gaze(
        self, frame: np.ndarray, face: Detection
    ) -> tuple[tuple[float, float] | None, str | None]:
        if self.pretrained_gaze is None or self.pretrained_input is None:
            return None, "model_not_configured"
        height, width = frame.shape[:2]
        x1 = max(0, min(width - 1, int(math.floor(face.x1))))
        y1 = max(0, min(height - 1, int(math.floor(face.y1))))
        x2 = max(x1 + 1, min(width, int(math.ceil(face.x2))))
        y2 = max(y1 + 1, min(height, int(math.ceil(face.y2))))
        try:
            face_crop = frame[y1:y2, x1:x2]
            tensor = preprocess_mobileone_face(face_crop)
            outputs = self.pretrained_gaze.run(
                [self.pretrained_yaw_output.name, self.pretrained_pitch_output.name],
                {self.pretrained_input.name: tensor},
            )
            return decode_mobileone_angles(outputs[0], outputs[1]), None
        except (ValueError, RuntimeError, cv2.error) as exc:
            return None, f"inference_unknown:{type(exc).__name__}"

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
        eye_centric, eye_centric_distance, eye_centric_roll = _eye_centric_geometry(left_points, right_points)
        pretrained_gaze_deg, pretrained_unknown_reason = self._predict_pretrained_gaze(frame, face)
        binocular_gaze_deg = ((left_yaw + right_yaw) * 0.5, (left_pitch + right_pitch) * 0.5)
        binocular_ray_proxy, binocular_ray_unknown_reason = build_binocular_ray_proxy(
            left_center_px=(float(left_center[0]), float(left_center[1])),
            right_center_px=(float(right_center[0]), float(right_center[1])),
            left_yaw_deg=left_yaw,
            left_pitch_deg=left_pitch,
            right_yaw_deg=right_yaw,
            right_pitch_deg=right_pitch,
            width=width,
            height=height,
            disagreement_deg=disagreement,
        )
        raw_model_angle_delta_deg = None
        if pretrained_gaze_deg is not None:
            raw_model_angle_delta_deg = math.hypot(
                binocular_gaze_deg[0] - pretrained_gaze_deg[0],
                binocular_gaze_deg[1] - pretrained_gaze_deg[1],
            )
        if eye_centric is None:
            return GazeSample(
                features,
                quality,
                disagreement,
                pose,
                None,
                None,
                None,
                eye_centric_roll,
                pretrained_gaze_deg,
                pretrained_unknown_reason,
                binocular_gaze_deg,
                raw_model_angle_delta_deg,
                binocular_ray_proxy,
                binocular_ray_unknown_reason,
            )
        return GazeSample(
            features,
            quality,
            disagreement,
            pose,
            eye_centric,
            eye_centric_distance,
            eye_centric_roll,
            None,
            pretrained_gaze_deg,
            pretrained_unknown_reason,
            binocular_gaze_deg,
            raw_model_angle_delta_deg,
            binocular_ray_proxy,
            binocular_ray_unknown_reason,
        )
