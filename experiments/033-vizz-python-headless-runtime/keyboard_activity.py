"""Opt-in Windows keyboard activity detector that never stores key values."""

from __future__ import annotations

import ctypes
import threading
import time
from ctypes import wintypes
from typing import Any


WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
WM_QUIT = 0x0012


class KeyboardActivity:
    """Count key-down events globally without retaining their identity."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._pending_events = 0
        self._last_event_monotonic: float | None = None
        self._running = threading.Event()
        self._ready = threading.Event()
        self._thread: threading.Thread | None = None
        self._thread_id: int | None = None
        self._hook = None
        self._callback = None
        self._error: BaseException | None = None

    def start(self) -> None:
        if self._thread is not None:
            return
        if not hasattr(ctypes, "windll"):
            raise RuntimeError("keyboard activity tracing requires Windows")
        self._running.set()
        self._thread = threading.Thread(target=self._run, name="vizz-keyboard-activity", daemon=True)
        self._thread.start()
        if not self._ready.wait(timeout=2.0):
            self.close()
            raise RuntimeError("keyboard hook did not become ready")
        if self._error is not None:
            error = self._error
            self.close()
            raise RuntimeError(f"keyboard hook failed: {error}") from error

    def _run(self) -> None:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

        user32.SetWindowsHookExW.argtypes = [ctypes.c_int, callback_type, ctypes.c_void_p, wintypes.DWORD]
        user32.SetWindowsHookExW.restype = ctypes.c_void_p
        user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
        user32.CallNextHookEx.restype = ctypes.c_ssize_t
        user32.UnhookWindowsHookEx.argtypes = [ctypes.c_void_p]
        user32.UnhookWindowsHookEx.restype = wintypes.BOOL
        user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), ctypes.c_void_p, wintypes.UINT, wintypes.UINT]
        user32.GetMessageW.restype = ctypes.c_int
        user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
        user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
        user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        user32.PostThreadMessageW.restype = wintypes.BOOL
        kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
        kernel32.GetModuleHandleW.restype = ctypes.c_void_p
        kernel32.GetCurrentThreadId.restype = wintypes.DWORD

        def hook_proc(code: int, message: int, _data: int) -> int:
            if code >= 0 and message in (WM_KEYDOWN, WM_SYSKEYDOWN):
                with self._lock:
                    self._pending_events += 1
                    self._last_event_monotonic = time.monotonic()
            return int(user32.CallNextHookEx(self._hook, code, message, _data))

        self._callback = callback_type(hook_proc)
        self._thread_id = int(kernel32.GetCurrentThreadId())
        try:
            self._hook = user32.SetWindowsHookExW(
                WH_KEYBOARD_LL,
                self._callback,
                kernel32.GetModuleHandleW(None),
                0,
            )
            if not self._hook:
                raise ctypes.WinError(ctypes.get_last_error())
            self._ready.set()
            message = wintypes.MSG()
            while self._running.is_set():
                result = user32.GetMessageW(ctypes.byref(message), None, 0, 0)
                if result <= 0:
                    break
                user32.TranslateMessage(ctypes.byref(message))
                user32.DispatchMessageW(ctypes.byref(message))
        except BaseException as exc:  # pragma: no cover - Windows hook failures are environment-specific
            self._error = exc
            self._ready.set()
        finally:
            if self._hook:
                user32.UnhookWindowsHookEx(self._hook)
            self._hook = None

    def snapshot(self, now: float | None = None) -> dict[str, Any]:
        timestamp = time.monotonic() if now is None else float(now)
        with self._lock:
            count = self._pending_events
            self._pending_events = 0
            last_event = self._last_event_monotonic
        age_ms = None
        if last_event is not None and timestamp >= last_event:
            age_ms = (timestamp - last_event) * 1000.0
        return {
            "keyboard_event_count": count,
            "keyboard_active": count > 0,
            "keyboard_last_event_age_ms": age_ms,
        }

    def close(self) -> None:
        self._running.clear()
        if self._thread_id is not None and hasattr(ctypes, "windll"):
            user32 = ctypes.windll.user32
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(timeout=2.0)
        self._thread = None
        self._thread_id = None
        self._hook = None
        self._callback = None
