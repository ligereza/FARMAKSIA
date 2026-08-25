"""Offline contract tests for the VIZZ 042 optical sketch."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("ray_screen_simulator.py")
spec = importlib.util.spec_from_file_location("ray_screen_simulator", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def main() -> None:
    pose_a = module.ScreenPose()
    pose_b = module.ScreenPose(x=0.12, y=-0.08, z=0.9)

    # One shared screen must move the source point seen by every optical model.
    for model_index, model in enumerate(module.EYE_MODELS):
        eye = module.eye_position(model_index)
        trace_a = module.trace_eye(model, eye, pose_a, (0.68, 0.30))
        trace_b = module.trace_eye(model, eye, pose_b, (0.68, 0.30))
        assert trace_a.source != trace_b.source
        assert trace_a.object_distance < trace_b.object_distance

        # A positive screen y is represented by a negative retinal y: optical
        # projection is inverted before the conceptual brain reconstruction.
        # The y-meridian carries the vertical sample; its retinal image is
        # inverted even when the x-meridian is used for the other focus line.
        assert trace_a.retina_y.y < eye.y

    astig = module.EYE_MODELS[2]
    astig_trace = module.trace_eye(astig, module.eye_position(2), pose_a, (0.68, 0.30))
    assert abs(astig_trace.focus_x.z - astig_trace.focus_y.z) > 1e-6
    assert module.focus_state(astig, astig_trace) == "dos focos"

    dx, dy, dz = module.classify_screen_motion(pose_a, pose_b)
    assert math.isclose(dx, 0.12)
    assert math.isclose(dy, -0.08)
    assert math.isclose(dz, 0.18)
    assert len(module.EYE_MODELS) == 3
    assert len(module.SCREEN_SAMPLES) == 3
    print("VIZZ_042_CONTRACT_VALID")


if __name__ == "__main__":
    main()
