"""Static contract for the eye-centric normalization experiment."""

from __future__ import annotations

from pathlib import Path


HERE = Path(__file__).parent


def main() -> None:
    failures: list[str] = []
    module = (HERE / "eye_centric.py").read_text(encoding="utf-8")
    runner = (HERE / "run_experiment.py").read_text(encoding="utf-8")
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    for token in (
        "interocular_distance",
        "midpoint",
        "roll_rad",
        "interocular_distance_too_small",
        "does not claim invariance to 3D head yaw/pitch",
    ):
        if token not in module:
            failures.append(f"eye-centric module lacks {token}")
    for token in ("scale", "angle", "translation"):
        if token not in runner:
            failures.append(f"runner lacks {token}")
    if '"head_yaw_pitch_invariance_claimed": False' not in runner:
        failures.append("runner overclaims 3D head-pose invariance")
    if "no abre cámara" not in readme or "UNKNOWN" not in readme:
        failures.append("experiment boundary is not documented")
    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CONTRACT_TESTS_VALID")


if __name__ == "__main__":
    main()
