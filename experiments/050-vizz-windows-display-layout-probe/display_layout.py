"""Read-only Windows display layout probe for the VIZZ geometry contract.

Windows exposes monitor rectangles in virtual-desktop coordinates. Those
coordinates are useful for addressing a desktop, but they are not a physical
3-D monitor pose. This module therefore reports the logical layout and keeps
physical plane geometry explicitly unknown until it is measured or calibrated.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
from dataclasses import asdict, dataclass
from typing import Any

try:
    import winreg
except ImportError:  # pragma: no cover - non-Windows fallback
    winreg = None


MONITORINFOF_PRIMARY = 1
ENUM_CURRENT_SETTINGS = -1
MDT_EFFECTIVE_DPI = 0


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


class MONITORINFOEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint32),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", ctypes.c_uint32),
        ("szDevice", ctypes.c_wchar * 32),
    ]


class DISPLAY_DEVICEW(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_uint32),
        ("DeviceName", ctypes.c_wchar * 32),
        ("DeviceString", ctypes.c_wchar * 128),
        ("StateFlags", ctypes.c_uint32),
        ("DeviceID", ctypes.c_wchar * 128),
        ("DeviceKey", ctypes.c_wchar * 128),
    ]


class POINTL(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class DEVMODE_DISPLAY_UNION(ctypes.Union):
    _fields_ = [
        ("dmPosition", POINTL),
        ("dmDisplayOrientation", ctypes.c_uint32),
        ("dmDisplayFixedOutput", ctypes.c_uint32),
        ("print_fields", ctypes.c_int16 * 8),
    ]


class DEVMODEW(ctypes.Structure):
    _anonymous_ = ("display",)
    _fields_ = [
        ("dmDeviceName", ctypes.c_wchar * 32),
        ("dmSpecVersion", ctypes.c_uint16),
        ("dmDriverVersion", ctypes.c_uint16),
        ("dmSize", ctypes.c_uint16),
        ("dmDriverExtra", ctypes.c_uint16),
        ("dmFields", ctypes.c_uint32),
        ("display", DEVMODE_DISPLAY_UNION),
        ("dmColor", ctypes.c_int16),
        ("dmDuplex", ctypes.c_int16),
        ("dmYResolution", ctypes.c_int16),
        ("dmTTOption", ctypes.c_int16),
        ("dmCollate", ctypes.c_int16),
        ("dmFormName", ctypes.c_wchar * 32),
        ("dmLogPixels", ctypes.c_uint16),
        ("dmBitsPerPel", ctypes.c_uint32),
        ("dmPelsWidth", ctypes.c_uint32),
        ("dmPelsHeight", ctypes.c_uint32),
        ("dmDisplayFlags", ctypes.c_uint32),
        ("dmDisplayFrequency", ctypes.c_uint32),
        ("dmICMMethod", ctypes.c_uint32),
        ("dmICMIntent", ctypes.c_uint32),
        ("dmMediaType", ctypes.c_uint32),
        ("dmDitherType", ctypes.c_uint32),
        ("dmReserved1", ctypes.c_uint32),
        ("dmReserved2", ctypes.c_uint32),
        ("dmPanningWidth", ctypes.c_uint32),
        ("dmPanningHeight", ctypes.c_uint32),
    ]


def _rect(value: RECT) -> tuple[int, int, int, int]:
    return int(value.left), int(value.top), int(value.right), int(value.bottom)


def _rect_size(value: tuple[int, int, int, int]) -> tuple[int, int]:
    return value[2] - value[0], value[3] - value[1]


def _device_details(user32: Any, device_name: str) -> tuple[str | None, str | None]:
    device = DISPLAY_DEVICEW()
    device.cb = ctypes.sizeof(DISPLAY_DEVICEW)
    ok = user32.EnumDisplayDevicesW(device_name, 0, ctypes.byref(device), 0)
    if not ok:
        return None, None
    return device.DeviceString.rstrip("\x00") or None, device.DeviceID.rstrip("\x00") or None


def _read_dpi(shcore: Any, monitor_handle: Any) -> tuple[int | None, int | None, str]:
    if shcore is None:
        return None, None, "unknown_shcore_unavailable"
    dpi_x = ctypes.c_uint()
    dpi_y = ctypes.c_uint()
    try:
        result = shcore.GetDpiForMonitor(
            monitor_handle,
            MDT_EFFECTIVE_DPI,
            ctypes.byref(dpi_x),
            ctypes.byref(dpi_y),
        )
    except (AttributeError, OSError):
        return None, None, "unknown_get_dpi_failed"
    if result != 0:
        return None, None, f"unknown_hresult_0x{int(result) & 0xFFFFFFFF:08X}"
    return int(dpi_x.value), int(dpi_y.value), "GetDpiForMonitor:MDT_EFFECTIVE_DPI"


def _read_orientation(user32: Any, device_name: str) -> tuple[int | None, str]:
    settings = DEVMODEW()
    settings.dmSize = ctypes.sizeof(DEVMODEW)
    try:
        ok = user32.EnumDisplaySettingsExW(
            device_name,
            ENUM_CURRENT_SETTINGS,
            ctypes.byref(settings),
            0,
        )
    except (AttributeError, OSError):
        return None, "unknown_enum_display_settings_failed"
    if not ok:
        return None, "unknown_enum_display_settings_failed"
    value = int(settings.dmDisplayOrientation)
    if value not in (0, 1, 2, 3):
        return None, "unknown_invalid_orientation"
    return value, "EnumDisplaySettingsExW"


def _read_edid_dimensions(device_id: str | None) -> tuple[int | None, int | None, str, int]:
    """Read manufacturer-reported EDID dimensions with a base-block checksum."""

    if os.name != "nt" or winreg is None or not device_id:
        return None, None, "UNKNOWN_NO_DEVICE_ID", 0
    parts = device_id.split("\\")
    if len(parts) < 2 or not parts[1]:
        return None, None, "UNKNOWN_INVALID_DEVICE_ID", 0
    vendor = parts[1]
    root_path = rf"SYSTEM\CurrentControlSet\Enum\DISPLAY\{vendor}"
    candidates: list[tuple[int, int]] = []
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, root_path) as vendor_key:
            instance_count = winreg.QueryInfoKey(vendor_key)[0]
            instance_names = [winreg.EnumKey(vendor_key, index) for index in range(instance_count)]
        for instance_name in instance_names:
            params_path = f"{root_path}\\{instance_name}\\Device Parameters"
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, params_path) as params_key:
                    raw_edid, _value_type = winreg.QueryValueEx(params_key, "EDID")
            except (FileNotFoundError, OSError):
                continue
            edid = bytes(raw_edid)
            if len(edid) < 128 or sum(edid[:128]) % 256 != 0:
                continue
            width_cm, height_cm = int(edid[21]), int(edid[22])
            if width_cm > 0 and height_cm > 0:
                candidates.append((width_cm, height_cm))
    except (FileNotFoundError, OSError):
        return None, None, "UNKNOWN_EDID_UNAVAILABLE", 0
    if not candidates:
        return None, None, "UNKNOWN_NO_VALID_EDID", 0
    unique = sorted(set(candidates))
    if len(unique) > 1:
        return None, None, "AMBIGUOUS_EDID_DIMENSIONS", len(candidates)
    status = "CONSENSUS_UNIQUE" if len(candidates) == 1 else "CONSENSUS_MULTIPLE"
    return unique[0][0], unique[0][1], status, len(candidates)


@dataclass(frozen=True)
class MonitorRecord:
    device_name: str
    device_string: str | None
    device_id: str | None
    monitor_rect: tuple[int, int, int, int]
    work_rect: tuple[int, int, int, int]
    primary: bool
    dpi_x: int | None
    dpi_y: int | None
    dpi_source: str
    orientation: int | None
    orientation_source: str
    edid_width_cm: int | None
    edid_height_cm: int | None
    edid_status: str
    edid_candidate_count: int

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["monitor_rect"] = list(self.monitor_rect)
        payload["work_rect"] = list(self.work_rect)
        width, height = _rect_size(self.monitor_rect)
        payload["logical_size_px"] = [width, height]
        payload["physical_size_m"] = (
            [self.edid_width_cm / 100.0, self.edid_height_cm / 100.0]
            if self.edid_width_cm is not None and self.edid_height_cm is not None
            else None
        )
        payload["physical_plane"] = None
        return payload


@dataclass(frozen=True)
class DisplayLayoutSnapshot:
    status: str
    platform: str
    layout_version: str | None
    virtual_screen_rect: tuple[int, int, int, int] | None
    monitors: tuple[MonitorRecord, ...]
    physical_geometry_status: str
    unknown_reason: str | None
    screen_content_mutated: bool = False
    camera_started: bool = False
    network_used: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "platform": self.platform,
            "layout_version": self.layout_version,
            "virtual_screen_rect": None if self.virtual_screen_rect is None else list(self.virtual_screen_rect),
            "monitors": [monitor.as_dict() for monitor in self.monitors],
            "physical_geometry_status": self.physical_geometry_status,
            "unknown_reason": self.unknown_reason,
            "screen_content_mutated": self.screen_content_mutated,
            "camera_started": self.camera_started,
            "network_used": self.network_used,
        }


def _unknown(reason: str) -> DisplayLayoutSnapshot:
    return DisplayLayoutSnapshot(
        status="UNKNOWN",
        platform=os.name,
        layout_version=None,
        virtual_screen_rect=None,
        monitors=(),
        physical_geometry_status="UNKNOWN",
        unknown_reason=reason,
    )


def _version(monitors: tuple[MonitorRecord, ...], virtual_rect: tuple[int, int, int, int]) -> str:
    canonical = {
        "virtual_screen_rect": list(virtual_rect),
        "monitors": [],
    }
    for monitor in monitors:
        descriptor = monitor.as_dict()
        # The logical layout version must not change merely because EDID
        # metadata becomes available; physical metadata has its own status.
        descriptor["physical_size_m"] = None
        descriptor["physical_plane"] = None
        descriptor.pop("edid_width_cm", None)
        descriptor.pop("edid_height_cm", None)
        descriptor.pop("edid_status", None)
        descriptor.pop("edid_candidate_count", None)
        canonical["monitors"].append(descriptor)
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def probe_windows_layout() -> DisplayLayoutSnapshot:
    """Read active Windows monitors; never open a camera or mutate displays."""

    if os.name != "nt":
        return _unknown("platform_not_windows")
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
    except OSError:
        return _unknown("user32_unavailable")

    try:
        user32.EnumDisplayMonitors.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(RECT),
            ctypes.WINFUNCTYPE(
                ctypes.c_int,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.POINTER(RECT),
                ctypes.c_long,
            ),
            ctypes.c_long,
        ]
        user32.EnumDisplayMonitors.restype = ctypes.c_int
        user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(MONITORINFOEXW)]
        user32.GetMonitorInfoW.restype = ctypes.c_int
        user32.EnumDisplayDevicesW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.POINTER(DISPLAY_DEVICEW), ctypes.c_uint32]
        user32.EnumDisplayDevicesW.restype = ctypes.c_int
        user32.EnumDisplaySettingsExW.argtypes = [ctypes.c_wchar_p, ctypes.c_int, ctypes.POINTER(DEVMODEW), ctypes.c_uint32]
        user32.EnumDisplaySettingsExW.restype = ctypes.c_int
    except AttributeError:
        return _unknown("user32_api_unavailable")

    try:
        shcore = ctypes.WinDLL("Shcore", use_last_error=True)
        shcore.GetDpiForMonitor.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)]
        shcore.GetDpiForMonitor.restype = ctypes.c_long
    except OSError:
        shcore = None

    callback_type = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.POINTER(RECT),
        ctypes.c_long,
    )
    records: list[MonitorRecord] = []

    def callback(monitor_handle: Any, _hdc: Any, _monitor_rect: Any, _data: int) -> int:
        info = MONITORINFOEXW()
        info.cbSize = ctypes.sizeof(MONITORINFOEXW)
        if not user32.GetMonitorInfoW(monitor_handle, ctypes.byref(info)):
            return 1
        device_name = info.szDevice.rstrip("\x00")
        device_string, device_id = _device_details(user32, device_name)
        dpi_x, dpi_y, dpi_source = _read_dpi(shcore, monitor_handle)
        orientation, orientation_source = _read_orientation(user32, device_name)
        edid_width_cm, edid_height_cm, edid_status, edid_candidate_count = _read_edid_dimensions(device_id)
        records.append(
            MonitorRecord(
                device_name=device_name,
                device_string=device_string,
                device_id=device_id,
                monitor_rect=_rect(info.rcMonitor),
                work_rect=_rect(info.rcWork),
                primary=bool(info.dwFlags & MONITORINFOF_PRIMARY),
                dpi_x=dpi_x,
                dpi_y=dpi_y,
                dpi_source=dpi_source,
                orientation=orientation,
                orientation_source=orientation_source,
                edid_width_cm=edid_width_cm,
                edid_height_cm=edid_height_cm,
                edid_status=edid_status,
                edid_candidate_count=edid_candidate_count,
            )
        )
        return 1

    callback_instance = callback_type(callback)
    if not user32.EnumDisplayMonitors(None, None, callback_instance, 0):
        return _unknown("enum_display_monitors_failed")
    if not records:
        return _unknown("no_active_monitors")

    left = min(record.monitor_rect[0] for record in records)
    top = min(record.monitor_rect[1] for record in records)
    right = max(record.monitor_rect[2] for record in records)
    bottom = max(record.monitor_rect[3] for record in records)
    virtual_rect = (left, top, right, bottom)
    ordered = tuple(sorted(records, key=lambda record: (record.monitor_rect[0], record.monitor_rect[1], record.device_name)))
    return DisplayLayoutSnapshot(
        status="VALID",
        platform="nt",
        layout_version=_version(ordered, virtual_rect),
        virtual_screen_rect=virtual_rect,
        monitors=ordered,
        physical_geometry_status=(
            "PARTIAL_EDID_ONLY"
            if any(record.edid_status.startswith("CONSENSUS") for record in ordered)
            else "UNKNOWN"
        ),
        unknown_reason=None,
    )
