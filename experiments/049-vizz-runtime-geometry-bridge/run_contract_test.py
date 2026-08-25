"""Kill tests for the closed legacy-to-geometry bridge."""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "046-vizz-gaze-geometry-probe"))
sys.path.insert(0, str(HERE))
from runtime_bridge import bridge_sample  # noqa: E402
import run_experiment as geometry_runner  # type: ignore  # noqa: E402


@dataclass(frozen=True)
class Sample:
    quality: float
    features: tuple[float, float, float, float, float, float]
    binocular_gaze_deg: tuple[float, float]


def main() -> None:
    failures: list[str] = []
    geometry_runner = load_geometry()
    layout = geometry_runner.make_layout()
    sample = Sample(0.95, (1.0, 1.0, 1.0, 1.0, 0.5, 0.5), (15.0, -10.0))
    closed = bridge_sample(sample, 1.0, layout)
    if closed.status != "UNKNOWN" or closed.reason != "missing_world_geometry":
        failures.append("legacy-only sample was allowed to become screen geometry")
    if closed.legacy_screen_mapping_allowed is not False:
        failures.append("legacy mapping was not closed")

    target = (0.12, -0.08, 0.72)
    explicit = bridge_sample(
        sample,
        1.0,
        layout,
        left_eye_world=(-0.032, 0.0, 0.0),
        right_eye_world=(0.032, 0.0, 0.0),
        gaze_direction_world=geometry_runner.direction_to(target, (0.0, 0.0, 0.0)),
    )
    if explicit.status != "VALID" or explicit.state is None or explicit.state.monitor_id != "primary":
        failures.append("explicit world geometry did not resolve")

    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("VIZZ_049_RUNTIME_BRIDGE_CONTRACT_VALID")


def load_geometry() -> object:
    geometry_path = ROOT / "experiments" / "046-vizz-gaze-geometry-probe" / "run_experiment.py"
    sys.path.insert(0, str(geometry_path.parent))
    spec = importlib.util.spec_from_file_location("vizz_046_runner_bridge_contract", geometry_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load geometry probe")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    main()
