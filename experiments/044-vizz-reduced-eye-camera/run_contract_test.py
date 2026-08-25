"""Offline physical contracts for the VIZZ 044 reduced-eye model."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("eye_camera_simulator.py")
spec = importlib.util.spec_from_file_location("eye_camera_simulator", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def main() -> None:
    pose = module.ScreenPose()
    normal = module.EYE_PRESETS[0]
    source = module.screen_point(pose, 0.55, 0.55)

    # The normal preset is constructed so the default screen focuses on the
    # fixed retinal plane, therefore the finite-aperture hits coincide.
    normal_trace = module.trace_screen_point(normal, source, 0.0025)
    assert math.isclose(normal_trace.focus_x, normal.retina, rel_tol=1e-9)
    assert math.isclose(normal_trace.focus_y, normal.retina, rel_tol=1e-9)
    assert normal_trace.blur_rms < 1e-10

    # A positive screen height must map to a negative retinal height.
    assert normal_trace.centroid.y < 0.0
    assert normal_trace.centroid.x < 0.0

    # Pupil rays enter at different heights, but a focused point must meet at
    # one image point.  The first and last hits are therefore equal here.
    assert max(abs(hit.x - normal_trace.centroid.x) for hit in normal_trace.hits) < 1e-10
    assert max(abs(hit.y - normal_trace.centroid.y) for hit in normal_trace.hits) < 1e-10

    myopia = module.EYE_PRESETS[1]
    hyperopia = module.EYE_PRESETS[2]
    assert module.image_distance(myopia.focal_x, pose.z) < myopia.retina
    assert module.image_distance(hyperopia.focal_x, pose.z) > hyperopia.retina

    # A larger pupil exposes more defocus in the myopic model.
    small = module.trace_screen_point(myopia, source, 0.0012)
    large = module.trace_screen_point(myopia, source, 0.0040)
    assert large.blur_rms > small.blur_rms

    astig = module.EYE_PRESETS[3]
    astig_trace = module.trace_screen_point(astig, source, 0.0025)
    assert not math.isclose(astig_trace.focus_x, astig_trace.focus_y)
    assert len(astig_trace.hits) == len(module.PUPIL_SAMPLE_TEMPLATE)
    assert len(module.retinal_grid(normal, pose, 0.0025)) == len(module.GRID_U) * len(module.GRID_V)
    print("VIZZ_044_OPTICAL_CONTRACT_VALID")


if __name__ == "__main__":
    main()
