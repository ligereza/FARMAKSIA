"""Mathematical contracts for VIZZ 045."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("eye_camera_complete.py")
SPEC = importlib.util.spec_from_file_location("vizz045_eye_camera", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def main() -> None:
    pose = MODULE.ScreenPose()
    normal = MODULE.EYE_PRESETS[0]
    myopia = MODULE.EYE_PRESETS[1]
    hyperopia = MODULE.EYE_PRESETS[2]
    astigmatism = MODULE.EYE_PRESETS[3]

    focused = MODULE.trace_point(normal, MODULE.screen_point(pose, 0.3, 0.4), 0.0025)
    assert math.isclose(focused.focus_x, normal.retina, abs_tol=1e-12)
    assert math.isclose(focused.focus_y, normal.retina, abs_tol=1e-12)
    assert focused.blur_rms < 1e-10
    assert focused.centroid.x < 0 and focused.centroid.y < 0
    assert len(focused.hits) == len(MODULE.PUPIL_PATTERN)

    marker = MODULE.trace_point(normal, MODULE.screen_point(pose, MODULE.MARKER_U, MODULE.MARKER_V), 0.0025)
    assert marker.centroid.x > 0 and marker.centroid.y < 0

    translated = MODULE.trace_point(normal, MODULE.screen_point(MODULE.ScreenPose(x=0.1, y=-0.05), 0.0, 0.0), 0.0025)
    assert translated.centroid.x < 0 and translated.centroid.y > 0

    assert myopia and hyperopia
    assert myopia and MODULE.trace_point(myopia, MODULE.screen_point(pose, 0.0, 0.0), 0.0025).focus_x < normal.retina
    assert hyperopia and MODULE.trace_point(hyperopia, MODULE.screen_point(pose, 0.0, 0.0), 0.0025).focus_x > normal.retina
    narrow = MODULE.trace_point(myopia, MODULE.screen_point(pose, 0.0, 0.0), 0.0015)
    wide = MODULE.trace_point(myopia, MODULE.screen_point(pose, 0.0, 0.0), 0.0035)
    assert wide.blur_rms > narrow.blur_rms
    assert astigmatism.focal_x != astigmatism.focal_y
    astig_trace = MODULE.trace_point(astigmatism, MODULE.screen_point(pose, 0.0, 0.0), 0.0025)
    assert not math.isclose(astig_trace.focus_x, astig_trace.focus_y, abs_tol=1e-9)
    assert len(MODULE.retinal_grid(normal, pose, 0.0025)) == len(MODULE.GRID_U) * len(MODULE.GRID_V)
    print("VIZZ_045_CAMERA_OPTICAL_CONTRACT_VALID")


if __name__ == "__main__":
    main()
