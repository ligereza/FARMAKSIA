"""Local, opt-in input observations normalized into semantic primitives."""

from __future__ import annotations

import ctypes
import math
from pathlib import Path
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "experiments/033-vizz-python-headless-runtime"
sys.path.insert(0, str(RUNTIME))

from interaction_trace import read_pointer_position  # noqa: E402
from keyboard_activity import KeyboardActivity  # noqa: E402


def _foreground_application_class() -> str:
    """Return an allowlisted executable class, never a path or window title."""
    if not hasattr(ctypes, "windll"):
        return "unknown"
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    user32.GetForegroundWindow.restype = ctypes.c_void_p
    user32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    user32.GetWindowThreadProcessId.restype = ctypes.c_ulong
    kernel32.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.QueryFullProcessImageNameW.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_ulong)]
    kernel32.QueryFullProcessImageNameW.restype = ctypes.c_int
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return "unknown"
    process_id = ctypes.c_ulong()
    if not user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id)):
        return "unknown"
    handle = kernel32.OpenProcess(0x1000, 0, process_id.value)
    if not handle:
        return "unknown"
    try:
        buffer = ctypes.create_unicode_buffer(520)
        length = ctypes.c_ulong(len(buffer))
        if not kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(length)):
            return "unknown"
        basename = Path(buffer.value[: length.value]).stem.casefold()
        if basename in {"excel", "blender", "winword", "code", "firefox", "msedge"}:
            return basename
        return "other"
    finally:
        kernel32.CloseHandle(handle)


def _uia_control_type() -> str | None:
    try:
        from pywinauto.uia_defines import IUIA
        from pywinauto.uia_element_info import UIAElementInfo

        focused = IUIA().get_focused_element()
        return str(UIAElementInfo(focused).control_type or "unknown")
    except Exception:
        return None
    return None


def read_context(pointer_enabled: bool) -> dict[str, Any]:
    pointer = read_pointer_position() if pointer_enabled else None
    return {
        "application_class": _foreground_application_class(),
        "uia_focused_control_type": _uia_control_type(),
        "pointer": list(pointer) if pointer is not None else None,
    }


def normalize_event(
    keyboard: dict[str, Any],
    context: dict[str, Any],
    previous: dict[str, Any] | None,
) -> str:
    if int(keyboard.get("keyboard_event_count", 0)) > 0:
        return "keyboard_activity"
    if previous is None or context.get("application_class") != previous.get("application_class") or context.get("uia_focused_control_type") != previous.get("uia_focused_control_type"):
        return "focus_context_changed"
    previous_pointer = previous.get("pointer")
    current_pointer = context.get("pointer")
    if previous_pointer != current_pointer and current_pointer is not None:
        return "pointer_motion"
    return "idle_observation"


def observe(duration: float, sample_hz: float, pointer_enabled: bool = False) -> dict[str, Any]:
    if duration <= 0.0 or not math.isfinite(duration):
        raise ValueError("duration must be finite and positive")
    if sample_hz <= 0.0 or not math.isfinite(sample_hz):
        raise ValueError("sample_hz must be finite and positive")
    keyboard = KeyboardActivity()
    keyboard.start()
    started = time.monotonic()
    deadline = started + duration
    next_sample = started
    previous: dict[str, Any] | None = None
    event_counts: dict[str, int] = {}
    context_counts: dict[str, int] = {}
    last_context: dict[str, str | None] = {"application_class": None, "uia_focused_control_type": None}
    sample_count = 0
    try:
        while time.monotonic() < deadline:
            now = time.monotonic()
            if now < next_sample:
                time.sleep(min(0.005, next_sample - now))
                continue
            keyboard_state = keyboard.snapshot(now)
            context = read_context(pointer_enabled)
            event = normalize_event(keyboard_state, context, previous)
            event_counts[event] = event_counts.get(event, 0) + 1
            context_key = f"{context['application_class']}:{context['uia_focused_control_type'] or 'unknown'}"
            context_counts[context_key] = context_counts.get(context_key, 0) + 1
            last_context = {
                "application_class": context["application_class"],
                "uia_focused_control_type": context["uia_focused_control_type"],
            }
            previous = context
            sample_count += 1
            next_sample = max(next_sample + 1.0 / sample_hz, time.monotonic())
    finally:
        keyboard.close()
    return {
        "sample_count": sample_count,
        "event_counts": dict(sorted(event_counts.items())),
        "context_counts": dict(sorted(context_counts.items())),
        "last_context": last_context,
        "pointer_enabled": pointer_enabled,
        "key_values_persisted": False,
        "text_persisted": False,
        "window_titles_persisted": False,
        "raw_pixels_persisted": False,
        "semantic_intent_claimed": False,
    }
