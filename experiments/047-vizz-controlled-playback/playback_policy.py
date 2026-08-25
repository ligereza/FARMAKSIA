"""Synthetic gaze-contingent display policy for controlled playback."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SceneElement:
    element_id: str
    u: float
    v: float
    category: str
    base_detail: float = 1.0
    peripheral_signal: bool = False
    text: bool = False


@dataclass(frozen=True)
class PlaybackConfig:
    mode: str
    focus_u: float
    focus_v: float
    screen_horizontal_deg: float = 45.0
    screen_vertical_deg: float = 26.0
    inner_radius_deg: float = 3.0
    transition_radius_deg: float = 8.0


def eccentricity_deg(element: SceneElement, config: PlaybackConfig) -> float:
    if not all(math.isfinite(value) for value in (element.u, element.v, config.focus_u, config.focus_v)):
        raise ValueError("playback coordinates must be finite")
    horizontal = (element.u - config.focus_u) * config.screen_horizontal_deg
    vertical = (element.v - config.focus_v) * config.screen_vertical_deg
    return math.hypot(horizontal, vertical)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def element_policy(element: SceneElement, config: PlaybackConfig, task: str = "unknown") -> dict[str, Any]:
    eccentricity = eccentricity_deg(element, config)
    if config.mode == "static_full":
        zone = "static"
        detail = element.base_detail
    elif config.mode == "static_clean":
        zone = "static_clean"
        detail = element.base_detail if element.category in {"text", "alert", "control"} else 0.45
    elif config.mode in {"adaptive_protected", "adaptive_unprotected"}:
        if eccentricity <= config.inner_radius_deg:
            zone = "foveal"
            detail = 1.0
        elif eccentricity <= config.transition_radius_deg:
            zone = "parafoveal"
            detail = max(0.65, element.base_detail)
        else:
            zone = "peripheral"
            if config.mode == "adaptive_protected" and element.peripheral_signal:
                detail = max(0.80, element.base_detail)
            elif element.category in {"text", "control"}:
                detail = 0.28
            else:
                detail = 0.22
    else:
        raise ValueError(f"unknown playback mode: {config.mode}")
    detail = _clamp(detail)
    return {
        "element_id": element.element_id,
        "category": element.category,
        "zone": zone,
        "eccentricity_deg": round(eccentricity, 6),
        "detail_factor": round(detail, 6),
        "peripheral_signal_preserved": bool(element.peripheral_signal and detail >= 0.8),
        "text_legible_descriptor": bool(not element.text or detail >= 0.65),
        "task": task,
    }


def evaluate_scene(elements: tuple[SceneElement, ...], config: PlaybackConfig, task: str = "unknown") -> list[dict[str, Any]]:
    if not elements:
        raise ValueError("playback scene cannot be empty")
    return [element_policy(element, config, task) for element in elements]
