"""Poll the local VIZZ 086 state file from a running Blender scene.

Paste the documented exec(...) line into Blender's Python Console. The timer
only updates VIZZ_CONTROLLER; it never injects input or executes a command from
the JSON file.
"""

from __future__ import annotations

import json
from pathlib import Path

import bpy


blend_path = Path(bpy.data.filepath).resolve()
if blend_path.name:
    # The 085 blend lives in <repo>/experiments/085/.../output. Deriving the
    # repo root from the opened blend keeps this pasteable from Blender's
    # console, where __file__ is not guaranteed to exist.
    HERE = blend_path.parents[3] / "experiments" / "086-vizz-blender-live-distance-bridge"
else:
    HERE = Path.cwd() / "experiments" / "086-vizz-blender-live-distance-bridge"
CONTROL_FILE = HERE / "output" / "vizz-blender-control.json"
TIMER_FUNCTION_NAME = "vizz_poll_live_distance"


def _state_from_file(path: Path) -> dict | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    if payload.get("schema") != "farmaxia:vizz-blender-live-distance:0.1":
        return None
    return payload


def stop() -> None:
    function = bpy.app.driver_namespace.get(TIMER_FUNCTION_NAME)
    if function is not None and bpy.app.timers.is_registered(function):
        bpy.app.timers.unregister(function)
    bpy.app.driver_namespace.pop(TIMER_FUNCTION_NAME, None)
    print("VIZZ_LIVE_BRIDGE_STOPPED")


def install(control_file: str | Path = CONTROL_FILE) -> None:
    path = Path(control_file).resolve()
    controller = bpy.data.objects.get("VIZZ_CONTROLLER")
    if controller is None:
        raise RuntimeError("VIZZ_CONTROLLER not found; open experiment 085 blend first")
    stop()
    state = {"mtime_ns": -1}

    def poll_live_distance() -> float:
        if not path.exists():
            return 0.25
        try:
            mtime_ns = path.stat().st_mtime_ns
        except OSError:
            return 0.25
        if mtime_ns == state["mtime_ns"]:
            return 0.05
        state["mtime_ns"] = mtime_ns
        payload = _state_from_file(path)
        if payload is None or payload.get("status") != "VALID":
            return 0.05
        distance = payload.get("observer_distance_m")
        if not isinstance(distance, (int, float)) or not 0.20 <= float(distance) <= 3.00:
            return 0.05
        focus_distance = payload.get("focus_distance_m")
        if not isinstance(focus_distance, (int, float)) or not 0.20 <= float(focus_distance) <= 3.00:
            return 0.05
        controller["observer_distance_m"] = float(distance)
        controller["focus_distance_m"] = float(focus_distance)
        controller["focus_offset_m"] = 0.0
        controller.update_tag(refresh={"DATA"})
        bpy.context.view_layer.update()
        return 0.05

    poll_live_distance.__name__ = TIMER_FUNCTION_NAME
    bpy.app.driver_namespace[TIMER_FUNCTION_NAME] = poll_live_distance
    bpy.app.driver_namespace["vizz_stop_live_bridge"] = stop
    bpy.app.timers.register(poll_live_distance, first_interval=0.1)
    print(f"VIZZ_LIVE_BRIDGE_ACTIVE control_file={path}")


install()
