"""Small ONNX adapter for the GitHub yakhyo MobileOne S0 gaze model."""

from __future__ import annotations

import math

import cv2
import numpy as np


MODEL_SOURCE = "https://github.com/yakhyo/gaze-estimation"
MODEL_RELEASE = "https://github.com/yakhyo/gaze-estimation/releases/download/weights/mobileone_s0_gaze.onnx"
INPUT_SIZE = 448
BIN_COUNT = 90
BIN_WIDTH_DEG = 4.0
ANGLE_OFFSET_DEG = 180.0


def preprocess_mobileone_face(face_bgr: np.ndarray) -> np.ndarray:
    """Prepare one BGR face crop using the upstream ImageNet preprocessing."""

    if face_bgr.ndim != 3 or face_bgr.shape[2] != 3 or face_bgr.shape[0] < 2 or face_bgr.shape[1] < 2:
        raise ValueError("MobileOne requires a non-empty BGR face crop")
    image = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (INPUT_SIZE, INPUT_SIZE), interpolation=cv2.INTER_LINEAR)
    image = image.astype(np.float32) / 255.0
    mean = np.asarray([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.asarray([0.229, 0.224, 0.225], dtype=np.float32)
    return ((image - mean) / std).transpose(2, 0, 1)[None]


def decode_mobileone_angles(yaw_logits: np.ndarray, pitch_logits: np.ndarray) -> tuple[float, float]:
    """Decode upstream 90-bin logits to finite yaw/pitch degrees."""

    def decode(logits: np.ndarray) -> float:
        values = np.asarray(logits, dtype=np.float32)
        if values.size != BIN_COUNT or not np.all(np.isfinite(values)):
            raise ValueError("MobileOne logits must contain 90 finite values")
        values = values.reshape(1, BIN_COUNT)
        values = values - np.max(values, axis=1, keepdims=True)
        probabilities = np.exp(values)
        probabilities /= np.sum(probabilities, axis=1, keepdims=True)
        bins = np.arange(BIN_COUNT, dtype=np.float32)[None, :]
        angle = float(np.sum(probabilities * bins) * BIN_WIDTH_DEG - ANGLE_OFFSET_DEG)
        if not math.isfinite(angle):
            raise ValueError("MobileOne decoded a non-finite angle")
        return angle

    return decode(yaw_logits), decode(pitch_logits)
