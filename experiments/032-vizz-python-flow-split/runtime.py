"""Headless CUDA runtime boundary; deliberately contains no UI toolkit."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any


class CudaUnavailable(RuntimeError):
    pass


def load_cuda_onnx_session(model_path: Path) -> Any:
    """Create an ONNX session with CUDA as the only requested provider."""

    try:
        ort = importlib.import_module("onnxruntime")
    except ModuleNotFoundError as exc:
        raise CudaUnavailable("onnxruntime-gpu is not installed") from exc
    available = set(ort.get_available_providers())
    if "CUDAExecutionProvider" not in available:
        raise CudaUnavailable("CUDAExecutionProvider is unavailable")
    # ORT 1.21+ can load CUDA/cuDNN DLLs shipped in the isolated environment;
    # do this before constructing the session so a missing DLL fails closed.
    ort.preload_dlls()
    options = ort.SessionOptions()
    options.add_session_config_entry("session.disable_cpu_ep_fallback", "1")
    try:
        return ort.InferenceSession(
            str(model_path),
            sess_options=options,
            providers=["CUDAExecutionProvider"],
        )
    except Exception as exc:
        raise CudaUnavailable(f"CUDA session could not be created: {exc}") from exc


def start_headless_runtime(profile_path: Path, model_path: Path) -> Any:
    """Validate the sealed profile and prepare the GPU model without UI."""

    if not profile_path.is_file():
        raise FileNotFoundError(profile_path)
    if not model_path.is_file():
        raise FileNotFoundError(model_path)
    # Camera capture and the transparent content modifier are intentionally
    # attached only after this CUDA session succeeds.
    return load_cuda_onnx_session(model_path)
