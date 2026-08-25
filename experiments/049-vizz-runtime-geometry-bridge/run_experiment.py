"""Probe that the legacy runtime stays closed until world geometry exists."""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
import json
from pathlib import Path


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "046-vizz-gaze-geometry-probe"))
sys.path.insert(0, str(HERE))
from runtime_bridge import bridge_sample  # noqa: E402
import run_experiment as geometry_runner  # type: ignore  # noqa: E402


@dataclass(frozen=True)
class SyntheticSample:
    quality: float
    features: tuple[float, float, float, float, float, float]
    binocular_gaze_deg: tuple[float, float]


def main() -> None:
    geometry_runner = load_geometry()
    layout = geometry_runner.make_layout()
    sample = SyntheticSample(0.95, (0.0, 0.0, 0.0, 0.0, 0.5, 0.5), (2.0, -1.0))
    closed = bridge_sample(sample, 1.0, layout)
    target = (0.12, -0.08, 0.72)
    explicit = bridge_sample(
        sample,
        1.0,
        layout,
        left_eye_world=(-0.032, 0.0, 0.0),
        right_eye_world=(0.032, 0.0, 0.0),
        gaze_direction_world=geometry_runner.direction_to(target, (0.0, 0.0, 0.0)),
        uncertainty_deg=0.5,
    )
    result = {
        "schema": "farmaxia:vizz-runtime-geometry-bridge:0.1",
        "experiment": "049-vizz-runtime-geometry-bridge",
        "objective": "prevent legacy image-space features from masquerading as physical screen geometry",
        "legacy_only": closed.as_dict(),
        "explicit_world_geometry": explicit.as_dict(),
        "human_data": False,
        "camera_opened": False,
        "screen_content_mutated": False,
        "network_used": False,
        "scope_limit": "synthetic adapter contract; world geometry provider is not implemented here",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


def load_geometry() -> object:
    geometry_path = ROOT / "experiments" / "046-vizz-gaze-geometry-probe" / "run_experiment.py"
    sys.path.insert(0, str(geometry_path.parent))
    spec = importlib.util.spec_from_file_location("vizz_046_runner_bridge", geometry_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load geometry probe")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    main()
