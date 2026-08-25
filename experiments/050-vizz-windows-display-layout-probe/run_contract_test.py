"""Contract test for the read-only Windows display layout probe."""

from __future__ import annotations

import os

from display_layout import probe_windows_layout


def main() -> None:
    snapshot = probe_windows_layout()
    failures: list[str] = []
    if snapshot.screen_content_mutated or snapshot.camera_started or snapshot.network_used:
        failures.append("probe crossed its read-only boundary")
    if snapshot.physical_geometry_status != "UNKNOWN":
        failures.append("logical desktop data was incorrectly promoted to physical geometry")

    if os.name == "nt":
        if snapshot.status != "VALID":
            failures.append(f"Windows probe did not resolve: {snapshot.unknown_reason}")
        if not snapshot.monitors:
            failures.append("Windows probe returned no monitors")
        if len({monitor.device_name for monitor in snapshot.monitors}) != len(snapshot.monitors):
            failures.append("duplicate monitor device names")
        if sum(monitor.primary for monitor in snapshot.monitors) != 1:
            failures.append("expected exactly one primary monitor")
        for monitor in snapshot.monitors:
            left, top, right, bottom = monitor.monitor_rect
            if right <= left or bottom <= top:
                failures.append(f"invalid monitor rectangle for {monitor.device_name}")
            work_left, work_top, work_right, work_bottom = monitor.work_rect
            if work_right <= work_left or work_bottom <= work_top:
                failures.append(f"invalid work rectangle for {monitor.device_name}")
        if not snapshot.layout_version:
            failures.append("missing deterministic layout version")
    else:
        if snapshot.status != "UNKNOWN" or snapshot.unknown_reason != "platform_not_windows":
            failures.append("non-Windows fallback was not explicit")

    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("VIZZ_050_WINDOWS_DISPLAY_LAYOUT_PROBE_VALID")


if __name__ == "__main__":
    main()
