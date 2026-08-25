"""Native click-through focus layer; it has no controls or VIZZ chrome."""

from __future__ import annotations

import ctypes
import os
from ctypes import wintypes

import numpy as np


class OverlayUnavailable(RuntimeError):
    pass


if os.name == "nt":
    # LPARAM is 64-bit on this Python/Windows process.  Using c_long here
    # truncates message data and makes DefWindowProcW reject lParam values.
    WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

    class POINT(ctypes.Structure):
        _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

    class SIZE(ctypes.Structure):
        _fields_ = [("cx", wintypes.LONG), ("cy", wintypes.LONG)]

    class BLENDFUNCTION(ctypes.Structure):
        _fields_ = [("BlendOp", ctypes.c_ubyte), ("BlendFlags", ctypes.c_ubyte), ("SourceConstantAlpha", ctypes.c_ubyte), ("AlphaFormat", ctypes.c_ubyte)]

    class WNDCLASSW(ctypes.Structure):
        _fields_ = [
            ("style", wintypes.UINT),
            ("lpfnWndProc", WNDPROC),
            ("cbClsExtra", ctypes.c_int),
            ("cbWndExtra", ctypes.c_int),
            ("hInstance", wintypes.HINSTANCE),
            ("hIcon", ctypes.c_void_p),
            ("hCursor", ctypes.c_void_p),
            ("hbrBackground", ctypes.c_void_p),
            ("lpszMenuName", wintypes.LPCWSTR),
            ("lpszClassName", wintypes.LPCWSTR),
        ]

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize", wintypes.DWORD),
            ("biWidth", wintypes.LONG),
            ("biHeight", wintypes.LONG),
            ("biPlanes", wintypes.WORD),
            ("biBitCount", wintypes.WORD),
            ("biCompression", wintypes.DWORD),
            ("biSizeImage", wintypes.DWORD),
            ("biXPelsPerMeter", wintypes.LONG),
            ("biYPelsPerMeter", wintypes.LONG),
            ("biClrUsed", wintypes.DWORD),
            ("biClrImportant", wintypes.DWORD),
        ]

    class BITMAPINFO(ctypes.Structure):
        _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]


class FocusOverlay:
    """A black translucent vignette that leaves a gaze-centered region clear."""

    def __init__(self, width: int, height: int, alpha: int = 30, radius_px: int = 260, origin: tuple[int, int] = (0, 0), diagnostic_marker: bool = False) -> None:
        if os.name != "nt":
            raise OverlayUnavailable("the native click-through layer currently targets Windows")
        if width <= 0 or height <= 0:
            raise ValueError("overlay dimensions must be positive")
        self.width = int(width)
        self.height = int(height)
        self.origin_x = int(origin[0])
        self.origin_y = int(origin[1])
        self.diagnostic_marker = bool(diagnostic_marker)
        self.alpha = max(0, min(255, int(alpha)))
        self.radius_px = max(32, int(radius_px))
        self.user32 = ctypes.windll.user32
        self.gdi32 = ctypes.windll.gdi32
        self.user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        self.user32.DefWindowProcW.restype = ctypes.c_ssize_t
        self.user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.UINT]
        self.user32.SetWindowPos.restype = wintypes.BOOL
        self.user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        self.user32.ShowWindow.restype = wintypes.BOOL
        self.hinstance = ctypes.windll.kernel32.GetModuleHandleW(None)
        self.class_name = f"FARMAXIA_VIZZ_LAYER_{id(self):x}"
        self._wndproc = WNDPROC(self._window_proc)
        window_class = WNDCLASSW()
        window_class.lpfnWndProc = self._wndproc
        window_class.hInstance = self.hinstance
        window_class.lpszClassName = self.class_name
        if not self.user32.RegisterClassW(ctypes.byref(window_class)):
            raise OverlayUnavailable("could not register the transparent layer")
        style = 0x80000000  # WS_POPUP
        extended = 0x00080000 | 0x00000020 | 0x00000080 | 0x08000000  # layered, transparent, tool, no activate
        self.hwnd = self.user32.CreateWindowExW(extended, self.class_name, "FARMAXIA_CONTENT_LAYER", style, self.origin_x, self.origin_y, self.width, self.height, None, None, self.hinstance, None)
        if not self.hwnd:
            self.user32.UnregisterClassW(self.class_name, self.hinstance)
            raise OverlayUnavailable("could not create the content layer")
        self.memdc = self.gdi32.CreateCompatibleDC(None)
        if not self.memdc:
            self.destroy()
            raise OverlayUnavailable("could not create the overlay drawing context")
        bitmap_info = BITMAPINFO()
        bitmap_info.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bitmap_info.bmiHeader.biWidth = self.width
        bitmap_info.bmiHeader.biHeight = -self.height
        bitmap_info.bmiHeader.biPlanes = 1
        bitmap_info.bmiHeader.biBitCount = 32
        bitmap_info.bmiHeader.biCompression = 0
        bits = ctypes.c_void_p()
        self.bitmap = self.gdi32.CreateDIBSection(self.memdc, ctypes.byref(bitmap_info), 0, ctypes.byref(bits), None, 0)
        if not self.bitmap or not bits.value:
            self.destroy()
            raise OverlayUnavailable("could not allocate the overlay bitmap")
        self.gdi32.SelectObject(self.memdc, self.bitmap)
        self.bits = bits
        self._blend = BLENDFUNCTION(0, 0, 255, 1)
        self._visible = False

    def _window_proc(self, hwnd: int, message: int, wparam: int, lparam: int) -> int:
        return self.user32.DefWindowProcW(hwnd, message, wparam, lparam)

    def set_focus(self, x_norm: float, y_norm: float) -> None:
        x = float(np.clip(x_norm, 0.0, 1.0)) * (self.width - 1)
        y = float(np.clip(y_norm, 0.0, 1.0)) * (self.height - 1)
        yy, xx = np.ogrid[: self.height, : self.width]
        distance2 = (xx - x) ** 2 + (yy - y) ** 2
        clear = np.exp(-distance2 / (2.0 * self.radius_px**2))
        alpha = np.asarray(np.rint(self.alpha * (1.0 - clear)), dtype=np.uint8)
        image = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        image[:, :, 3] = alpha
        if self.diagnostic_marker:
            marker_distance = np.sqrt(distance2)
            marker = np.abs(marker_distance - 18.0) <= 3.0
            image[marker, 0:3] = 255
            image[marker, 3] = 230
        ctypes.memmove(self.bits, image.ctypes.data, image.nbytes)
        destination = POINT(self.origin_x, self.origin_y)
        size = SIZE(self.width, self.height)
        source = POINT(0, 0)
        if not self.user32.UpdateLayeredWindow(self.hwnd, None, ctypes.byref(destination), ctypes.byref(size), self.memdc, ctypes.byref(source), 0, ctypes.byref(self._blend), 2):
            raise OverlayUnavailable("UpdateLayeredWindow failed")
        # Reassert topmost on every frame. A normal application opened after
        # the overlay must not cover the layer; the layer still remains
        # click-through and does not activate itself.
        flags = 0x0010 | 0x0040 | 0x0080 | 0x0400  # NOACTIVATE | SHOWWINDOW | NOOWNERZORDER | NOSENDCHANGING
        if not self.user32.SetWindowPos(self.hwnd, wintypes.HWND(-1), self.origin_x, self.origin_y, self.width, self.height, flags):
            raise OverlayUnavailable("SetWindowPos failed while asserting topmost overlay")
        if not self._visible:
            self.user32.ShowWindow(self.hwnd, 4)  # SW_SHOWNOACTIVATE; layered windows need an explicit show call.
            self._visible = True

    def pump_messages(self) -> None:
        """Keep the native window alive without taking focus from the app below."""
        message = wintypes.MSG()
        while self.user32.PeekMessageW(ctypes.byref(message), self.hwnd, 0, 0, 1):  # PM_REMOVE
            self.user32.TranslateMessage(ctypes.byref(message))
            self.user32.DispatchMessageW(ctypes.byref(message))

    def hide(self) -> None:
        if self._visible:
            self.user32.ShowWindow(self.hwnd, 0)
            self._visible = False

    def destroy(self) -> None:
        if os.name != "nt":
            return
        if getattr(self, "hwnd", None):
            self.user32.DestroyWindow(self.hwnd)
            self.hwnd = None
        if getattr(self, "bitmap", None):
            self.gdi32.DeleteObject(self.bitmap)
            self.bitmap = None
        if getattr(self, "memdc", None):
            self.gdi32.DeleteDC(self.memdc)
            self.memdc = None
        if getattr(self, "hinstance", None):
            self.user32.UnregisterClassW(self.class_name, self.hinstance)

    def __enter__(self) -> "FocusOverlay":
        return self

    def __exit__(self, *_: object) -> None:
        self.destroy()
