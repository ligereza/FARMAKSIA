"""Visible one-shot calibration boundary.

The eventual Tkinter/PySide window belongs here and nowhere in runtime.py.
This module only defines the profile seal contract until the CUDA feature
provider and the screen-point renderer are installed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


CALIBRATION_POINT_COUNT = 12


def seal_local_profile(
    profile_path: Path,
    screen_size: tuple[int, int],
    samples: Iterable[dict[str, object]],
    model_sha256: str,
) -> Path:
    """Write only explicit calibration vectors; reject incomplete profiles."""

    materialized = list(samples)
    if len(materialized) < CALIBRATION_POINT_COUNT:
        raise ValueError("at least 12 calibration samples are required")
    if not model_sha256:
        raise ValueError("model hash is required to seal a profile")
    for sample in materialized:
        if not sample.get("features") or not sample.get("target"):
            raise ValueError("profile sample is missing features or target")
    profile = {
        "schema": "farmaxia:vizz-calibration-profile:0.1",
        "screen_size": list(screen_size),
        "sample_count": len(materialized),
        "model_sha256": model_sha256,
        "samples": materialized,
        "raw_video": False,
    }
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = profile_path.with_suffix(profile_path.suffix + ".tmp")
    temporary.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(profile_path)
    return profile_path
