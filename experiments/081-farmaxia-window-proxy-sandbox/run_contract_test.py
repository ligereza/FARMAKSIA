"""Offline spatial and source-boundary contract for experiment 081."""

from __future__ import annotations

import random
from pathlib import Path

from proxy_math import DEFAULT_PERMUTATION, QuadrantPermutation


HERE = Path(__file__).resolve().parent
SOURCE = (HERE / "native" / "main.cpp").read_text(encoding="utf-8")


def main() -> None:
    size = 320
    randomizer = random.Random(81)
    points = [(0, 0), (159, 159), (160, 0), (319, 319)]
    points.extend((randomizer.randrange(size), randomizer.randrange(size)) for _ in range(1_000))
    for source in points:
        proxy = DEFAULT_PERMUTATION.source_to_proxy(*source, size)
        assert DEFAULT_PERMUTATION.proxy_to_source(*proxy, size) == source

    for invalid in ((0, 0, 1, 2), (0, 1, 2), (0, 1, 2, 4)):
        try:
            QuadrantPermutation(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"non-bijection accepted: {invalid}")

    for required in (
        "Windows::Graphics::Capture",
        "CreateCaptureItemForWindow(source_window)",
        "destination_to_source",
        "RouteProxyClick",
        "WM_LBUTTONDOWN",
        "WINDOW_PROXY_SANDBOX_VERIFIED",
    ):
        assert required in SOURCE, f"native proof lacks {required}"
    for forbidden in ("FindWindow", "EnumWindows", "GetForegroundWindow", "SendInput", "keybd_event", "mouse_event", "Windows.Graphics.CapturePicker"):
        assert forbidden not in SOURCE, f"unsafe or external capability: {forbidden}"
    print("FARMAXIA_081_WINDOW_PROXY_CONTRACT_VALID")


if __name__ == "__main__":
    main()
