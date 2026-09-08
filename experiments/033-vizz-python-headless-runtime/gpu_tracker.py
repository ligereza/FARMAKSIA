"""CUDA-only face/eye and gaze inference; no UI and no camera preview."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

try:
    import onnxruntime as ort
except ModuleNotFoundError:  # pragma: no cover - exercised by offline consumers
    ort = None  # type: ignore[assignment]

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
class IREyeFeature:
    """Small scalar-only pupil/glint measurement from an IR-looking frame.

    This is deliberately a diagnostic optical branch, not a calibrated gaze
    estimator.  It records where dark-pupil and bright-glint candidates were
    found in an eye ROI, while retaining an explicit status when either
    feature is absent.  No image pixels are retained.
    """

    eye_center_px: tuple[float, float]
    pupil_center_px: tuple[float, float] | None
    glint_center_px: tuple[float, float] | None
    pupil_diameter_px: float | None
    glint_area_px2: float | None
    pupil_glint_vector_px: tuple[float, float] | None
    pupil_mean_intensity: float | None
    glint_mean_intensity: float | None
    local_contrast: float
    confidence: float
    status: str
    pupil_polarity: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "eye_center_px": list(self.eye_center_px),
            "pupil_center_px": list(self.pupil_center_px) if self.pupil_center_px is not None else None,
            "glint_center_px": list(self.glint_center_px) if self.glint_center_px is not None else None,
            "pupil_diameter_px": self.pupil_diameter_px,
            "glint_area_px2": self.glint_area_px2,
            "pupil_glint_vector_px": list(self.pupil_glint_vector_px) if self.pupil_glint_vector_px is not None else None,
            "pupil_mean_intensity": self.pupil_mean_intensity,
            "glint_mean_intensity": self.glint_mean_intensity,
            "local_contrast": self.local_contrast,
            "confidence": self.confidence,
            "status": self.status,
            "pupil_polarity": self.pupil_polarity,
        }


def _gray_image(image: np.ndarray) -> np.ndarray:
    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("IR image must be a non-empty numpy array")
    if image.ndim == 2:
        return image
    if image.ndim == 3 and image.shape[2] == 1:
        return image[..., 0]
    if image.ndim == 3 and image.shape[2] >= 3:
        return cv2.cvtColor(image[..., :3], cv2.COLOR_BGR2GRAY)
    raise ValueError("IR image must be grayscale or BGR")


def _eye_roi(gray: np.ndarray, center_px: tuple[float, float], roi_side_px: float) -> tuple[np.ndarray, int, int]:
    height, width = gray.shape[:2]
    if height < 1 or width < 1:
        raise ValueError("IR image has no pixels")
    if not math.isfinite(float(roi_side_px)) or float(roi_side_px) <= 0.0:
        raise ValueError("IR eye ROI size must be finite and positive")
    side = max(24, int(round(float(roi_side_px))))
    cx, cy = float(center_px[0]), float(center_px[1])
    if not math.isfinite(cx) or not math.isfinite(cy):
        raise ValueError("IR eye centre must be finite")
    x1 = max(0, min(width - 1, int(round(cx - side * 0.5))))
    y1 = max(0, min(height - 1, int(round(cy - side * 0.5))))
    x2 = min(width, x1 + side)
    y2 = min(height, y1 + side)
    roi = gray[y1:y2, x1:x2]
    if roi.size == 0:
        raise ValueError("IR eye ROI is empty")
    return roi, x1, y1


def _candidate_blobs(
    mask: np.ndarray,
    roi: np.ndarray,
    *,
    dark: bool,
    max_area_fraction: float | None = None,
    compact_only: bool | None = None,
) -> list[tuple[float, float, float, float, float]]:
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    height, width = roi.shape[:2]
    roi_area = float(max(1, height * width))
    candidates: list[tuple[float, float, float, float, float]] = []
    max_area_fraction = max_area_fraction if max_area_fraction is not None else (0.22 if dark else 0.035)
    compact_only = compact_only if compact_only is not None else not dark
    for label in range(1, count):
        area = float(stats[label, cv2.CC_STAT_AREA])
        box_width = float(stats[label, cv2.CC_STAT_WIDTH])
        box_height = float(stats[label, cv2.CC_STAT_HEIGHT])
        if area < (2.0 if dark else 1.0) or area > roi_area * max_area_fraction:
            continue
        if box_width <= 0.0 or box_height <= 0.0:
            continue
        aspect = min(box_width, box_height) / max(box_width, box_height)
        if dark and aspect < 0.22:
            continue
        if compact_only and not dark and max(box_width, box_height) > max(5.0, width * 0.24):
            continue
        x, y = [float(value) for value in centroids[label]]
        center_distance = math.hypot((x - width * 0.5) / max(1.0, width * 0.5), (y - height * 0.5) / max(1.0, height * 0.5))
        if center_distance > 1.25:
            continue
        values = roi[labels == label].astype(np.float32)
        mean_intensity = float(np.mean(values)) if values.size else 0.0
        compactness = min(1.0, (area / max(1.0, box_width * box_height)) * 1.5)
        center_score = max(0.0, 1.0 - center_distance / 1.25)
        if dark:
            intensity_score = max(0.0, min(1.0, 1.0 - mean_intensity / 180.0))
        else:
            intensity_score = max(0.0, min(1.0, mean_intensity / 255.0))
        score = 0.45 * intensity_score + 0.35 * center_score + 0.20 * compactness
        candidates.append((score, x, y, area, mean_intensity))
    return sorted(candidates, reverse=True)


def _extract_ir_eye_feature_gray(
    gray: np.ndarray,
    eye_center_px: tuple[float, float],
    *,
    roi_side_px: float,
) -> IREyeFeature:
    roi, origin_x, origin_y = _eye_roi(gray, eye_center_px, roi_side_px)
    roi_float = roi.astype(np.float32)
    local_contrast = float(np.std(roi_float) / 255.0)
    q25, q75 = [float(value) for value in np.percentile(roi_float, [25.0, 75.0])]
    mean = float(np.mean(roi_float))
    std = float(np.std(roi_float))

    # Dark-pupil candidate: use an adaptive low threshold so exposure changes
    # do not turn the branch into a fixed-camera brightness test.
    dark_cut = max(12.0, min(105.0, q25 + 10.0, mean - 0.35 * std))
    dark_mask = (roi_float <= dark_cut).astype(np.uint8)
    dark_pupil_candidates = _candidate_blobs(dark_mask, roi, dark=True)

    # Active IR can also produce a bright-pupil response.  Search that
    # polarity separately so the branch does not silently fail when the
    # illuminator/camera geometry differs from the usual dark-pupil case.
    bright_pupil_cut = max(150.0, q75 + max(10.0, std * 0.25))
    bright_pupil_cut = min(252.0, bright_pupil_cut)
    bright_pupil_mask = (roi_float >= bright_pupil_cut).astype(np.uint8)
    bright_pupil_candidates = _candidate_blobs(
        bright_pupil_mask,
        roi,
        dark=False,
        max_area_fraction=0.22,
        compact_only=False,
    )

    def pupil_rank(candidate: tuple[float, float, float, float, float]) -> float:
        expected_diameter = max(4.0, roi.shape[1] * 0.18)
        diameter = math.sqrt(4.0 * candidate[3] / math.pi)
        size_score = math.exp(-abs(math.log(max(1.0, diameter) / expected_diameter)))
        return 0.55 * candidate[0] + 0.45 * size_score

    pupil_options = [(pupil_rank(candidate), candidate, "dark") for candidate in dark_pupil_candidates]
    pupil_options.extend((pupil_rank(candidate), candidate, "bright") for candidate in bright_pupil_candidates)
    pupil_option = max(pupil_options, key=lambda item: item[0]) if pupil_options else None
    pupil = pupil_option[1] if pupil_option is not None else None
    pupil_polarity = pupil_option[2] if pupil_option is not None else None

    # Corneal reflection candidate: a small high-intensity blob near the eye
    # centre (and, when available, near the pupil).  This is intentionally
    # conservative because a monochrome stream may contain many bright areas.
    bright_cut = max(170.0, q75 + max(18.0, std * 0.75))
    bright_cut = min(254.0, bright_cut)
    bright_mask = (roi_float >= bright_cut).astype(np.uint8)
    glint_candidates = _candidate_blobs(bright_mask, roi, dark=False)
    glint = None
    if glint_candidates:
        if pupil is None:
            glint = glint_candidates[0]
        else:
            pupil_x, pupil_y = pupil[1], pupil[2]
            ranked: list[tuple[float, tuple[float, float, float, float, float]]] = []
            for candidate in glint_candidates:
                distance = math.hypot(candidate[1] - pupil_x, candidate[2] - pupil_y)
                proximity = max(0.0, 1.0 - distance / max(1.0, roi.shape[1] * 0.55))
                ranked.append((0.65 * candidate[0] + 0.35 * proximity, candidate))
            glint = max(ranked, key=lambda item: item[0])[1]

    pupil_center = None
    pupil_diameter = None
    pupil_intensity = None
    if pupil is not None:
        pupil_center = (origin_x + pupil[1], origin_y + pupil[2])
        pupil_diameter = math.sqrt(4.0 * pupil[3] / math.pi)
        pupil_intensity = pupil[4]
    glint_center = None
    glint_area = None
    glint_intensity = None
    if glint is not None:
        glint_center = (origin_x + glint[1], origin_y + glint[2])
        glint_area = glint[3]
        glint_intensity = glint[4]
    vector = None
    if pupil_center is not None and glint_center is not None:
        vector = (glint_center[0] - pupil_center[0], glint_center[1] - pupil_center[1])

    if pupil is not None and glint is not None:
        status = "PUPIL_GLINT"
        confidence = 0.5 * pupil[0] + 0.5 * glint[0]
    elif pupil is not None:
        status = "PUPIL_ONLY"
        confidence = 0.55 * pupil[0]
    elif glint is not None:
        status = "GLINT_ONLY"
        confidence = 0.45 * glint[0]
    else:
        status = "NO_FEATURES"
        confidence = 0.0
    return IREyeFeature(
        eye_center_px=(float(eye_center_px[0]), float(eye_center_px[1])),
        pupil_center_px=pupil_center,
        glint_center_px=glint_center,
        pupil_diameter_px=float(pupil_diameter) if pupil_diameter is not None else None,
        glint_area_px2=float(glint_area) if glint_area is not None else None,
        pupil_glint_vector_px=vector,
        pupil_mean_intensity=float(pupil_intensity) if pupil_intensity is not None else None,
        glint_mean_intensity=float(glint_intensity) if glint_intensity is not None else None,
        local_contrast=max(0.0, local_contrast),
        confidence=max(0.0, min(1.0, confidence)),
        status=status,
        pupil_polarity=pupil_polarity,
    )


def extract_ir_optics(
    frame: np.ndarray,
    eye_centers_px: tuple[tuple[float, float], tuple[float, float]],
    *,
    roi_side_px: float,
) -> tuple[IREyeFeature, IREyeFeature]:
    """Extract two scalar pupil/glint diagnostics from one IR frame."""

    gray = _gray_image(frame)
    return tuple(
        _extract_ir_eye_feature_gray(gray, center, roi_side_px=roi_side_px)
        for center in eye_centers_px
    )  # type: ignore[return-value]


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
    # IR-specific pupil/glint diagnostics.  Kept separate from the gaze
    # mapper until a calibration proves that this signal improves held-out
    # predictions rather than merely tracking exposure or camera position.
    ir_optics: tuple[IREyeFeature, IREyeFeature] | None = None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def create_cuda_session(model_path: Path) -> ort.InferenceSession:
    if ort is None:
        raise GpuUnavailable("onnxruntime-gpu is not installed")
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

    def __init__(
        self,
        face_model: Path,
        gaze_model: Path | None,
        pretrained_gaze_model: Path | None = None,
        *,
        scale_only: bool = False,
    ) -> None:
        self.face_model_sha256 = sha256(face_model)
        self.face = create_cuda_session(face_model)
        self.face_input = self.face.get_inputs()[0]
        self.face_output = self.face.get_outputs()[0]
        if self.face_input.name != "input" or list(self.face_input.shape) != [1, 3, 480, 640]:
            raise GpuUnavailable("unexpected RetinaFace input signature")
        if self.face_output.name != "batchno_classid_score_x1y1x2y2_landms":
            raise GpuUnavailable("unexpected RetinaFace output signature")
        self.gaze = None
        self.gaze_input = None
        self.gaze_output = None
        self.pretrained_gaze = None
        self.pretrained_input = None
        self.pretrained_yaw_output = None
        self.pretrained_pitch_output = None
        if scale_only:
            return
        if gaze_model is None:
            raise FileNotFoundError("gaze model is required outside scale_only mode")
        self.gaze = create_cuda_session(gaze_model)
        self.pretrained_gaze = create_cuda_session(pretrained_gaze_model) if pretrained_gaze_model is not None else None
        self.gaze_input = self.gaze.get_inputs()[0]
        self.gaze_output = self.gaze.get_outputs()[0]
        if self.gaze_input.name != "input" or list(self.gaze_input.shape[1:]) != [3, 160, 160]:
            raise GpuUnavailable("unexpected gaze input signature")
        if self.gaze_output.name != "output" or list(self.gaze_output.shape[1:]) != [962, 3]:
            raise GpuUnavailable("unexpected gaze output signature")
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

    def sample(self, frame: np.ndarray, *, enable_ir_optics: bool = False) -> GazeSample | None:
        if self.gaze is None or self.gaze_input is None or self.gaze_output is None:
            raise RuntimeError("gaze sampling is unavailable in scale_only mode")
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
        ir_optics = None
        if enable_ir_optics:
            try:
                ir_optics = extract_ir_optics(
                    frame,
                    (tuple(left_center.tolist()), tuple(right_center.tolist())),
                    roi_side_px=max(28.0, face.width * 0.22),
                )
            except (TypeError, ValueError, cv2.error):
                # The gaze sample remains usable; the optical branch carries
                # its own missingness through a null value in the scalar log.
                ir_optics = None
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
                ir_optics,
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
            ir_optics,
        )
