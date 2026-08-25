"""Minimal representation-plan to transparent desktop overlay bridge."""

from __future__ import annotations

import ctypes
import os
import time
from ctypes import wintypes
from dataclasses import dataclass


class OverlayRuntimeUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class RepresentationPlan:
    source: str
    target_space: str
    focus_x: float
    focus_y: float
    periphery_alpha: int = 30
    focus_radius_px: int = 260
    expires_at: float | None = None
    reversible: bool = True

    def validate(self) -> None:
        if not self.source:
            raise ValueError("representation plan requires a source")
        if self.target_space != "virtual_desktop":
            raise ValueError("057 only supports virtual_desktop target space")
        if not 0.0 <= self.focus_x <= 1.0 or not 0.0 <= self.focus_y <= 1.0:
            raise ValueError("focus must be normalized to [0, 1]")
        if not 0 <= self.periphery_alpha <= 255:
            raise ValueError("periphery_alpha must be in [0, 255]")
        if self.focus_radius_px < 32:
            raise ValueError("focus_radius_px must be at least 32")
        if not self.reversible:
            raise ValueError("057 requires reversible plans")

    def is_expired(self, now: float | None = None) -> bool:
        return self.expires_at is not None and (time.monotonic() if now is None else now) >= self.expires_at


def virtual_desktop() -> tuple[int, int, int, int]:
    if os.name != "nt":
        raise OverlayRuntimeUnavailable("057 currently targets Windows")
    user32 = ctypes.windll.user32
    return (
        int(user32.GetSystemMetrics(76)),
        int(user32.GetSystemMetrics(77)),
        int(user32.GetSystemMetrics(78)),
        int(user32.GetSystemMetrics(79)),
    )


def cursor_focus(origin_x: int, origin_y: int, width: int, height: int) -> tuple[float, float]:
    if os.name != "nt":
        raise OverlayRuntimeUnavailable("057 currently targets Windows")
    point = wintypes.POINT()
    if not ctypes.windll.user32.GetCursorPos(ctypes.byref(point)):
        raise OverlayRuntimeUnavailable("GetCursorPos failed")
    x = (point.x - origin_x) / max(1, width - 1)
    y = (point.y - origin_y) / max(1, height - 1)
    return max(0.0, min(1.0, x)), max(0.0, min(1.0, y))


def build_pointer_plan(
    origin_x: int,
    origin_y: int,
    width: int,
    height: int,
    *,
    alpha: int,
    radius: int,
    ttl: float,
) -> RepresentationPlan:
    focus_x, focus_y = cursor_focus(origin_x, origin_y, width, height)
    plan = RepresentationPlan(
        source="pointer_probe",
        target_space="virtual_desktop",
        focus_x=focus_x,
        focus_y=focus_y,
        periphery_alpha=alpha,
        focus_radius_px=radius,
        expires_at=time.monotonic() + ttl,
    )
    plan.validate()
    return plan
