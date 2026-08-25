"""Static contract for legacy plus eye-centric capture persistence."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    failures: list[str] = []
    tracker = (ROOT / "experiments/033-vizz-python-headless-runtime/gpu_tracker.py").read_text(encoding="utf-8")
    capture = (ROOT / "experiments/033-vizz-python-headless-runtime/calibration_capture.py").read_text(encoding="utf-8")
    calibration = (ROOT / "experiments/033-vizz-python-headless-runtime/calibration_ui.py").read_text(encoding="utf-8")
    validation = (ROOT / "experiments/033-vizz-python-headless-runtime/validation_ui.py").read_text(encoding="utf-8")
    runner = (Path(__file__).parent / "run_experiment.py").read_text(encoding="utf-8")
    for token in ("eye_centric", "eye_centric_distance_px", "eye_centric_roll_rad", "eye_centric_unknown_reason"):
        if token not in tracker or token not in capture or token not in calibration or token not in validation:
            failures.append(f"missing persistence token: {token}")
    for token in ("EYE_CENTRIC_CAPTURE_VALID", "legacy_feature_count", "eye_centric_valid_count"):
        if token not in runner:
            failures.append(f"synthetic contract lacks {token}")
    if "mapper.predict(sample.features)" not in (ROOT / "experiments/033-vizz-python-headless-runtime/run_vizz.py").read_text(encoding="utf-8"):
        failures.append("legacy mapper is no longer the controlled comparison")
    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CONTRACT_TESTS_VALID")
    print("legacy_features_preserved=True")
    print("eye_centric_persisted=True")
    print("screen_mapper_changed=False")


if __name__ == "__main__":
    main()
