"""Synthetic adoption probe for the real VIZZ GPU binocular ray adapter."""

from __future__ import annotations

import json
import sys
from pathlib import Path


HERE = Path(__file__).parent
TRACKER_DIR = HERE.parent / "033-vizz-python-headless-runtime"
sys.path.insert(0, str(TRACKER_DIR))

from ray_proxy import build_binocular_ray_proxy  # noqa: E402


def main() -> None:
    valid, valid_reason = build_binocular_ray_proxy(
        left_center_px=(300.0, 240.0),
        right_center_px=(340.0, 240.0),
        left_yaw_deg=-3.0,
        left_pitch_deg=1.0,
        right_yaw_deg=3.0,
        right_pitch_deg=1.0,
        width=640,
        height=480,
        disagreement_deg=6.0,
    )
    rejected, rejected_reason = build_binocular_ray_proxy(
        left_center_px=(300.0, 240.0),
        right_center_px=(340.0, 240.0),
        left_yaw_deg=-40.0,
        left_pitch_deg=0.0,
        right_yaw_deg=40.0,
        right_pitch_deg=0.0,
        width=640,
        height=480,
        disagreement_deg=80.0,
    )
    result = {
        "schema": "farmaxia:vizz-gpu-binocular-ray-adapter:0.1",
        "experiment": "053-vizz-gpu-binocular-ray-adapter",
        "provider": "experiments/033-vizz-python-headless-runtime/gpu_tracker.py",
        "valid_status": valid.status if valid is not None else "UNKNOWN",
        "valid_reason": valid_reason,
        "interocular_baseline_proxy": valid.interocular_baseline_proxy if valid is not None else None,
        "rejected_status": rejected.status if rejected is not None else "UNKNOWN",
        "rejected_reason": rejected_reason,
        "relative_only": True,
        "camera_opened": False,
        "screen_content_mutated": False,
        "network_used": False,
        "raw_video": False,
        "human_data": False,
        "contract": "VIZZ_053_GPU_BINOCULAR_RAY_ADAPTER_CONTRACT_VALID",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
