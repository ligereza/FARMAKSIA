"""Pure contract checks for experiment 087.

This test imports only the standard-library router and reads the bootstrap as
text. It must not start a process, camera, window, socket or TouchDesigner.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from host_adapter import from_geometry_state, from_tracker_observation  # noqa: E402
from render_policy import compute_plan  # noqa: E402
from state_router import normalize_state, to_channels  # noqa: E402


def payload(**overrides):
    value = {
        "schema": "farmaxia:vizz-state:0.1",
        "seq": 7,
        "timestamp_monotonic_ms": 1000.0,
        "source": "manual",
        "confidence": 0.9,
        "head": {"x": 0.1, "y": -0.1, "z": 0.0, "rx": 2.0, "ry": -3.0, "rz": 0.5},
        "focus": {"x": 0.2, "y": 0.2, "w": 0.4, "h": 0.3, "interest": 0.8},
        "input": {
            "keyboard_activity": 0.5,
            "pointer_x": 0.4,
            "pointer_y": 0.6,
            "pointer_active": True,
        },
        "window": {
            "selected": True,
            "monitor_id": "display-1",
            "source_rect": {"left": -10, "top": 20, "width": 1280, "height": 720},
        },
        "permissions": {"camera": False, "capture": True, "overlay": True, "input_remap": False},
    }
    value.update(overrides)
    return value


def check_valid_and_minimized():
    state = normalize_state(payload(raw_secret="must-not-forward"), now_monotonic_ms=1100.0)
    assert state["status"] == "VALID"
    assert "raw_secret" not in state
    channels = to_channels(state)
    assert channels["state_valid"] == 1.0
    assert channels["state_unknown"] == 0.0
    assert channels["head_x"] == 0.1
    assert channels["permission_capture"] == 1.0


def check_unknown_boundaries():
    stale = normalize_state(payload(), now_monotonic_ms=2000.0)
    assert stale["status"] == "UNKNOWN" and stale["reason"] == "STATE_STALE"

    low_conf = normalize_state(payload(confidence=0.1), now_monotonic_ms=1100.0)
    assert low_conf["status"] == "UNKNOWN" and low_conf["reason"] == "CONFIDENCE_TOO_LOW"

    wrong_schema = normalize_state(payload(schema="farmaxia:vizz-state:9.9"), now_monotonic_ms=1100.0)
    assert wrong_schema["status"] == "UNKNOWN" and wrong_schema["reason"] == "SCHEMA_MISMATCH"

    nan_state = normalize_state(payload(confidence=math.nan), now_monotonic_ms=1100.0)
    assert nan_state["status"] == "UNKNOWN" and nan_state["reason"] == "CONFIDENCE_INVALID"

    invalid_focus = normalize_state(
        payload(focus={"x": 0.9, "y": 0.2, "w": 0.2, "h": 0.3, "interest": 0.8}),
        now_monotonic_ms=1100.0,
    )
    assert invalid_focus["status"] == "UNKNOWN" and invalid_focus["reason"] == "STATE_GROUP_INVALID"


def check_bootstrap_boundaries():
    bootstrap = (ROOT / "touchdesigner" / "bootstrap_vizz_renderer.py").read_text(encoding="utf-8")
    forbidden = (
        "Video Device In",
        "Screen Grab",
        "Window COMP",
        "subprocess",
        "cv2",
        "SendInput",
        "SetCursorPos",
        "pyautogui",
    )
    for marker in forbidden:
        assert marker not in bootstrap, marker
    assert "osc.par.active = 0" in bootstrap
    assert "node.par.const.numBlocks" in bootstrap
    assert 'filtered.par.type = "oneeuro"' in bootstrap
    assert "filterwidth" not in bootstrap
    assert "state_filtered" in bootstrap
    assert "outTOP" in bootstrap


def check_host_adapter_does_not_invent_gaze():
    candidate = from_tracker_observation(
        seq=8,
        timestamp_monotonic_ms=1000.0,
        pose=(0.6, 0.4, 0.2, 0.3, 0.01, 0.1),
        quality=0.9,
        reference_face_width=0.2,
        window={
            "selected": True,
            "monitor_id": "display-1",
            "source_rect": {"left": 0, "top": 0, "width": 1280, "height": 720},
        },
        permissions={"camera": True, "capture": False, "overlay": True, "input_remap": False},
    )
    state = normalize_state(candidate, now_monotonic_ms=1100.0)
    assert state["status"] == "VALID"
    assert abs(state["head"]["x"] - 0.2) < 1e-9
    assert state["head"]["z"] == 0.0
    assert state["focus"]["interest"] == 0.0
    assert state["focus"]["w"] == 0.0

    explicit_focus = dict(candidate)
    explicit_focus["focus"] = {"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.2, "interest": 0.9}
    state_with_focus = normalize_state(explicit_focus, now_monotonic_ms=1100.0)
    assert state_with_focus["status"] == "VALID"
    assert state_with_focus["focus"]["interest"] == 0.9


def check_bounded_render_policy():
    state = normalize_state(payload(), now_monotonic_ms=1100.0)
    state["permissions"]["overlay"] = True
    active = compute_plan(state)
    assert active["status"] == "ACTIVE"
    assert -0.05 <= active["parallax_x"] <= 0.05
    assert -0.05 <= active["parallax_y"] <= 0.05
    assert 0.98 <= active["depth_scale"] <= 1.02
    assert active["critical_sharpness"] == 1.0

    unknown = compute_plan({"status": "UNKNOWN", "reason": "STATE_STALE"})
    assert unknown["status"] == "NEUTRAL"
    assert unknown["parallax_x"] == 0.0
    assert unknown["critical_sharpness"] == 1.0

    no_permission = compute_plan(state | {"permissions": {"overlay": False}})
    assert no_permission["status"] == "NEUTRAL"


def check_geometry_adapter_preserves_unknown_monitor():
    common = {
        "seq": 9,
        "timestamp_monotonic_ms": 1000.0,
        "head": {"x": 0.0, "y": 0.0, "z": 0.0, "rx": 0.0, "ry": 0.0, "rz": 0.0},
        "window": {
            "selected": True,
            "monitor_id": "display-2",
            "source_rect": {"left": 1280, "top": 0, "width": 1920, "height": 1080},
        },
        "permissions": {"camera": True, "capture": True, "overlay": True, "input_remap": False},
    }
    valid = from_geometry_state(
        **common,
        geometry_state={"status": "VALID", "uv": [0.7, 0.4], "confidence": 0.8},
    )
    valid_state = normalize_state(valid, now_monotonic_ms=1100.0)
    assert valid_state["status"] == "VALID"
    assert valid_state["focus"]["x"] == 0.7
    assert valid_state["focus"]["interest"] == 1.0

    ambiguous = from_geometry_state(
        **common,
        geometry_state={"status": "UNKNOWN", "unknown_reason": "ambiguous_monitor"},
    )
    ambiguous_state = normalize_state(ambiguous, now_monotonic_ms=1100.0)
    assert ambiguous_state["status"] == "UNKNOWN"
    assert ambiguous_state["reason"] == "CONFIDENCE_TOO_LOW"


if __name__ == "__main__":
    check_valid_and_minimized()
    check_unknown_boundaries()
    check_bootstrap_boundaries()
    check_host_adapter_does_not_invent_gaze()
    check_bounded_render_policy()
    check_geometry_adapter_preserves_unknown_monitor()
    print("VIZZ_087_CONTRACT=PASS")
