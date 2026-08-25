"""Synthetic audit for the no-content naturalistic VIZZ trace."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "experiments/033-vizz-python-headless-runtime"
sys.path.insert(0, str(RUNTIME))
sys.path.insert(0, str(Path(__file__).parent))

from interaction_trace import InteractionTrace  # noqa: E402
from trace_audit import audit_trace  # noqa: E402


def main() -> None:
    sample = SimpleNamespace(
        quality=0.92,
        disagreement_deg=1.5,
        features=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6),
        eye_centric=(0.6, 0.5, 0.4, 0.3, 0.2, 0.1),
        eye_centric_distance_px=70.0,
        eye_centric_roll_rad=0.01,
        pose=(0.5, 0.5, 0.2, 0.3, 0.0, 0.08),
        pretrained_gaze_deg=(12.0, -8.0),
        pretrained_gaze_unknown_reason=None,
        binocular_gaze_deg=(10.0, -7.0),
        raw_model_angle_delta_deg=2.236067977,
    )
    with tempfile.TemporaryDirectory(prefix="farmaxia-vizz-trace-audit-") as directory:
        path = Path(directory) / "trace.jsonl"
        trace = InteractionTrace(path, (1707, 960), sample_hz=20.0)
        trace.write_sample(10.0, sample, (0.2, 0.3), (640, 360))
        trace.write_sample(10.05, None, None, (641, 361))
        trace.close()
        result = audit_trace(path)
    result["all_properties_hold"] = (
        result["sample_count"] == 2
        and result["mouse_present_count"] == 2
        and result["gaze_valid_count"] == 1
        and result["pretrained_gaze_valid_count"] == 1
        and result["model_delta_count"] == 1
        and result["pretrained_gaze_preflight"] == "cuda_zero_tensor"
        and result["screen_coordinates_claimed"] is False
    )
    print(json.dumps(result, indent=2))
    if not result["all_properties_hold"]:
        raise SystemExit(1)
    print("TRACE_AUDIT_VALID")


if __name__ == "__main__":
    main()
