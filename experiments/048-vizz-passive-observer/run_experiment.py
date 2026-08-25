"""Synthetic passive observer audit; no camera, desktop or human trace."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from passive_trace import PassiveTraceWriter, audit_trace  # noqa: E402


def load_geometry() -> object:
    geometry_path = ROOT / "experiments" / "046-vizz-gaze-geometry-probe" / "run_experiment.py"
    spec = importlib.util.spec_from_file_location("vizz_046_runner", geometry_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load geometry probe")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(geometry_path.parent))
    spec.loader.exec_module(module)
    return module


def main() -> None:
    geometry = load_geometry()
    layout = geometry.make_layout()
    valid = geometry.resolve_gaze(geometry.observation_for((0.12, -0.08, 0.72)), layout)
    unknown = geometry.resolve_gaze(geometry.observation_for((0.12, -0.08, 0.72), confidence=0.3), layout)
    with tempfile.TemporaryDirectory(prefix="farmaxia-vizz-048-") as directory:
        path = Path(directory) / "passive.jsonl"
        writer = PassiveTraceWriter(path, layout.version)
        writer.write_sample(1.0, valid, {"keyboard_event_count": 2, "keyboard_active": True, "mouse_screen": (100, 200)})
        writer.write_sample(1.05, unknown, {"keyboard_event_count": 0, "keyboard_active": False, "mouse_screen": (110, 205)})
        writer.close()
        audit = audit_trace(path)
    result = {
        "schema": "farmaxia:vizz-passive-observer:0.1",
        "experiment": "048-vizz-passive-observer",
        "objective": "prepare privacy-preserving gaze/context observation without content mutation",
        "audit": audit,
        "human_data": False,
        "camera_opened": False,
        "screen_content_mutated": False,
        "network_used": False,
        "raw_video": False,
        "text_persisted": False,
        "scope_limit": "synthetic writer/audit; no claim about real-time performance or user experience",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
