"""Run the read-only Windows display layout probe."""

from __future__ import annotations

import json

from display_layout import probe_windows_layout


def main() -> None:
    snapshot = probe_windows_layout()
    payload = {
        "schema": "farmaxia:vizz-windows-display-layout:0.1",
        "experiment": "050-vizz-windows-display-layout-probe",
        "objective": "observe the logical Windows monitor layout without pretending it is physical 3-D geometry",
        **snapshot.as_dict(),
        "contract": "VIZZ_050_WINDOWS_DISPLAY_LAYOUT_PROBE_VALID",
        "interpretation": {
            "logical_rects": "usable for virtual-desktop addressing and monitor identity",
            "physical_planes": "not inferred from pixels, DPI or EDID identifiers",
            "next_required_input": "physical monitor dimensions and camera/eye-to-plane calibration",
        },
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
