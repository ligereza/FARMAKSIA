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

    # The thin-lens equation must reproduce a normal reference eye at the
    # default distance when its focal length is chosen from the retina plane.
    normal_focal = 1.0 / (1.0 / (pose_a.z - module.LENS_Z) + 1.0 / 0.017)
    normal_image = module.thin_lens_image_distance(normal_focal, pose_a.z - module.LENS_Z)
    assert math.isclose(normal_image, 0.017, rel_tol=1e-9)

    # One shared screen must change the spatial path seen by every model.
    for model_index, model in enumerate(module.EYE_MODELS):
        eye = module.eye_position(model_index)
        trace_a = module.spatial_trace(pose_a, eye, (0.0, 0.0))
        trace_b = module.spatial_trace(pose_b, eye, (0.0, 0.0))
        assert trace_a.source != trace_b.source
        assert trace_a.distance != trace_b.distance

        # A positive object height is inverted on the retinal plane.  All
        # aperture rays must meet at the same calculated paraxial focus.
        vertical = module.eye_meridian_trace(model, eye, pose_a, "vertical")
        assert vertical.object_height == 0.0
        off_axis = module.trace_paraxial(0.02, vertical.object_distance, model.focal_y, model.retina)
        assert off_axis.focus_height < 0.0
        assert all(
            math.isclose(ray.focus_height, off_axis.focus_height, rel_tol=1e-9, abs_tol=1e-9)
            for ray in off_axis.rays
        )

    astig = module.EYE_MODELS[2]
    astig_vertical = module.eye_meridian_trace(astig, module.eye_position(2), pose_a, "vertical")
    astig_horizontal = module.eye_meridian_trace(astig, module.eye_position(2), pose_a, "horizontal")
    assert not math.isclose(astig_vertical.image_distance, astig_horizontal.image_distance)
    assert module.focus_state(astig_vertical.image_distance, astig.retina) == "detrás de retina"
    assert module.focus_state(astig_horizontal.image_distance, astig.retina) == "antes de retina"

    dx, dy, dz = module.classify_screen_motion(pose_a, pose_b)
    assert math.isclose(dx, 0.12)
    assert math.isclose(dy, -0.08)
    assert math.isclose(dz, 0.18)
    assert len(module.EYE_MODELS) == 3
    assert len(module.SCREEN_SAMPLES) == 3
    assert len(module.APERTURE_SAMPLES) == 3
    print("VIZZ_042_CONTRACT_VALID")


if __name__ == "__main__":
    main()
