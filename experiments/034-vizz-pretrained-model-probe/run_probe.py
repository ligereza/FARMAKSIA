"""Probe pretrained gaze assets without opening a camera or storing frames."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / ".vizz-models"
DEFAULT_OUTPUT = ROOT / ".vizz-pretrained-probe.json"


class ProbeFailure(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def json_shape(shape: Any) -> list[Any]:
    if shape is None:
        return []
    return [int(value) if isinstance(value, (int, np.integer)) else str(value) for value in shape]


def tensor_shape(shape: Any) -> tuple[int, ...]:
    values: list[int] = []
    for value in shape:
        if isinstance(value, (int, np.integer)) and int(value) > 0:
            values.append(int(value))
        else:
            values.append(1)
    return tuple(values)


def run_nvidia_smi() -> dict[str, Any]:
    executable = shutil.which("nvidia-smi")
    if executable is None:
        return {"available": False, "reason": "nvidia-smi-not-found"}
    command = [
        executable,
        "--query-gpu=name,driver_version,memory.total,memory.used,temperature.gpu",
        "--format=csv,noheader,nounits",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return {"available": False, "reason": completed.stderr.strip()[-500:] or "nvidia-smi-failed"}
    devices = []
    for line in completed.stdout.splitlines():
        fields = [field.strip() for field in line.split(",")]
        if len(fields) == 5:
            devices.append(
                {
                    "name": fields[0],
                    "driver": fields[1],
                    "memory_total_mib": fields[2],
                    "memory_used_mib": fields[3],
                    "temperature_c": fields[4],
                }
            )
    return {"available": bool(devices), "devices": devices}


def cuda_session(path: Path, profile_prefix: Path) -> ort.InferenceSession:
    if not path.is_file():
        raise ProbeFailure(f"missing model: {path}")
    providers = set(ort.get_available_providers())
    if "CUDAExecutionProvider" not in providers:
        raise ProbeFailure("CUDAExecutionProvider is not available")
    if hasattr(ort, "preload_dlls"):
        ort.preload_dlls()
    options = ort.SessionOptions()
    options.log_severity_level = 3
    options.enable_profiling = True
    options.profile_file_prefix = str(profile_prefix)
    options.add_session_config_entry("session.disable_cpu_ep_fallback", "1")
    try:
        session = ort.InferenceSession(
            str(path),
            sess_options=options,
            providers=["CUDAExecutionProvider"],
        )
    except Exception as exc:  # pragma: no cover - depends on local CUDA installation
        raise ProbeFailure(f"CUDA session failed for {path.name}: {exc}") from exc
    if "CUDAExecutionProvider" not in session.get_providers():
        raise ProbeFailure(f"CUDA was not activated for {path.name}")
    active = session.get_session_options().get_session_config_entry("session.disable_cpu_ep_fallback")
    if active != "1":
        raise ProbeFailure(f"CPU fallback was not disabled for {path.name}")
    return session


def describe_io(session: ort.InferenceSession) -> dict[str, Any]:
    return {
        "inputs": [
            {"name": item.name, "shape": json_shape(item.shape), "type": item.type}
            for item in session.get_inputs()
        ],
        "outputs": [
            {"name": item.name, "shape": json_shape(item.shape), "type": item.type}
            for item in session.get_outputs()
        ],
    }


def profiled_providers(profile_path: Path) -> dict[str, int]:
    if not profile_path.is_file():
        raise ProbeFailure("ONNX Runtime did not emit an execution profile")
    events = json.loads(profile_path.read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    for event in events:
        provider = event.get("args", {}).get("provider")
        if provider:
            counts[provider] = counts.get(provider, 0) + 1
    if not counts:
        raise ProbeFailure("execution profile contained no provider assignments")
    return counts


def smoke_inference(session: ort.InferenceSession) -> dict[str, Any]:
    inputs = session.get_inputs()
    if len(inputs) != 1:
        raise ProbeFailure("probe expects one-input ONNX assets")
    input_meta = inputs[0]
    shape = tensor_shape(input_meta.shape)
    if input_meta.type not in {"tensor(float)", "tensor(float16)"}:
        raise ProbeFailure(f"unsupported synthetic input type: {input_meta.type}")
    dtype = np.float16 if input_meta.type == "tensor(float16)" else np.float32
    synthetic = np.zeros(shape, dtype=dtype)
    feed = {input_meta.name: synthetic}
    session.run(None, feed)
    durations: list[float] = []
    outputs: list[np.ndarray] = []
    for _ in range(3):
        started = time.perf_counter()
        outputs = session.run(None, feed)
        durations.append((time.perf_counter() - started) * 1000.0)
    finite_values = []
    output_shapes = []
    for output in outputs:
        array = np.asarray(output)
        output_shapes.append(list(array.shape))
        finite_values.append(float(np.isfinite(array).mean()) if array.size else 1.0)
    return {
        "input_shape": list(shape),
        "output_shapes": output_shapes,
        "output_finite_ratio": finite_values,
        "median_latency_ms": round(median(durations), 3),
        "latency_ms": [round(value, 3) for value in durations],
        "human_data": False,
    }


def probe_model(name: str, path: Path) -> dict[str, Any]:
    item: dict[str, Any] = {
        "name": name,
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size if path.is_file() else 0,
        "sha256": sha256(path) if path.is_file() else None,
        "status": "UNKNOWN",
    }
    with tempfile.TemporaryDirectory(prefix="farmaxia-vizz-probe-") as directory:
        profile_prefix = Path(directory) / path.stem
        session = cuda_session(path, profile_prefix)
        item["registered_providers"] = session.get_providers()
        item["requested_providers"] = ["CUDAExecutionProvider"]
        item["cpu_fallback_config"] = session.get_session_options().get_session_config_entry(
            "session.disable_cpu_ep_fallback"
        )
        item["io"] = describe_io(session)
        item["smoke"] = smoke_inference(session)
        profile_path = Path(session.end_profiling())
        assignments = profiled_providers(profile_path)
        item["profiled_provider_assignments"] = assignments
        if set(assignments) != {"CUDAExecutionProvider"}:
            raise ProbeFailure(f"non-CUDA execution assignment for {path.name}: {assignments}")
    item["status"] = "CUDA_SMOKE_VALID"
    return item


def candidate_catalog() -> list[dict[str, str]]:
    return [
        {
            "name": "screen-eye-tracking current baseline",
            "status": "installed-and-probed",
            "role": "RetinaFace plus binocular gaze ONNX baseline",
            "source": "https://github.com/PINTO0309/screen-eye-tracking",
        },
        {
            "name": "ptgaze / ETH-XGaze",
            "status": "researched-not-installed",
            "role": "GPU gaze vector with normalized eye/head inputs",
            "source": "https://github.com/hysts/pytorch_mpiigaze_demo",
        },
        {
            "name": "MobileGaze",
            "status": "researched-not-installed",
            "role": "small ONNX/CUDA deployment candidate",
            "source": "https://github.com/yakhyo/gaze-estimation",
        },
        {
            "name": "MediaPipe Iris",
            "status": "researched-not-installed",
            "role": "iris landmarks and metric-distance frontend; not gaze inference",
            "source": "https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/iris.md",
        },
        {
            "name": "6DRepNet",
            "status": "researched-not-installed",
            "role": "independent head-rotation estimator",
            "source": "https://github.com/thohemp/6DRepNet",
        },
        {
            "name": "UniGaze",
            "status": "research-quarantine",
            "role": "cross-domain gaze representation; license and cost require separate review",
            "source": "https://github.com/ut-vision/UniGaze",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    result: dict[str, Any] = {
        "schema": "farmaxia:vizz-pretrained-model-probe:0.1",
        "python": sys.version,
        "onnxruntime": ort.__version__,
        "available_providers": ort.get_available_providers(),
        "gpu": run_nvidia_smi(),
        "human_data": False,
        "camera_opened": False,
        "raw_frames_persisted": False,
        "candidates": candidate_catalog(),
        "models": [],
        "kill_tests": {
            "cpu_fallback_allowed": False,
            "camera_required": False,
            "screen_coordinates_claimed": False,
        },
    }

    models = (
        ("retinaface", MODEL_DIR / "retinaface.onnx"),
        ("binocular_gaze", MODEL_DIR / "gaze.onnx"),
    )
    try:
        for name, path in models:
            result["models"].append(probe_model(name, path))
        result["status"] = "PROBE_VALID"
    except (OSError, ProbeFailure, RuntimeError, ValueError) as exc:
        result["status"] = "PROBE_BLOCKED"
        result["error"] = str(exc)

    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "PROBE_VALID":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
