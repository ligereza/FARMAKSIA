"""Adversarial tests: missing rulers, excessive pose and false precision."""

from __future__ import annotations

import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from scale_geometry import ScaleContractError, ScaleObservation, fuse_scale  # noqa: E402


def rejected(callable_obj, message: str) -> None:
    try:
        callable_obj()
    except ScaleContractError:
        return
    raise AssertionError(message)


def main() -> None:
    reference = ScaleObservation(120.0, 300.0)

    rejected(
        lambda: fuse_scale(ScaleObservation(0.0, 300.0), reference),
        "zero eye distance was accepted",
    )
    rejected(
        lambda: fuse_scale(ScaleObservation(120.0, 0.0), reference),
        "zero face width was accepted",
    )
    rejected(
        lambda: fuse_scale(
            reference, ScaleObservation(120.0, 300.0, yaw_deg=40.0)
        ),
        "out-of-domain head pose was extrapolated",
    )
    rejected(
        lambda: fuse_scale(
            reference, ScaleObservation(120.0, 300.0, eye_quality=0.0)
        ),
        "one ruler was allowed to disappear silently",
    )

    eye_only_change = fuse_scale(reference, ScaleObservation(168.0, 300.0))
    face_only_change = fuse_scale(reference, ScaleObservation(120.0, 390.0))
    assert eye_only_change.status == "UNKNOWN"
    assert face_only_change.status == "UNKNOWN"

    contradictory = fuse_scale(reference, ScaleObservation(150.0, 255.0))
    assert contradictory.status == "UNKNOWN"
    assert contradictory.fused_scale is None
    assert contradictory.relative_distance_ratio is None

    print("FARMAXIA_084_VIZZ_DISTANCE_SCALE_KILL_TESTS_VALID")


if __name__ == "__main__":
    main()
