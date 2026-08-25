"""Run the no-camera FARMAKSIA overlay proof over existing applications."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = EXPERIMENT_ROOT.parents[1] / "experiments" / "033-vizz-python-headless-runtime"
sys.path.insert(0, str(RUNTIME_ROOT))

from content_overlay import FocusOverlay  # noqa: E402
from overlay_runtime import build_pointer_plan, virtual_desktop  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FARMAKSIA 057 no-camera overlay runtime")
    parser.add_argument("--duration", type=float, default=30.0, help="seconds; 0 runs until Ctrl+C")
    parser.add_argument("--overlay-alpha", type=int, default=90)
    parser.add_argument("--focus-radius", type=int, default=320)
    parser.add_argument("--hz", type=float, default=30.0)
    parser.add_argument(
        "--diagnostic-marker",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="show a visible moving ring for the first overlay smoke test",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.hz <= 0:
        raise SystemExit("--hz must be positive")
    origin_x, origin_y, width, height = virtual_desktop()
    deadline = None if args.duration == 0 else time.monotonic() + max(0.1, args.duration)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("057 overlay active: camera=False network=False click_through=True")
    try:
        with FocusOverlay(
            width,
            height,
            alpha=args.overlay_alpha,
            radius_px=args.focus_radius,
            origin=(origin_x, origin_y),
            diagnostic_marker=args.diagnostic_marker,
        ) as overlay:
            interval = 1.0 / args.hz
            while deadline is None or time.monotonic() < deadline:
                plan = build_pointer_plan(
                    origin_x,
                    origin_y,
                    width,
                    height,
                    alpha=args.overlay_alpha,
                    radius=args.focus_radius,
                    ttl=interval * 2.0,
                )
                overlay.set_focus(plan.focus_x, plan.focus_y)
                overlay.pump_messages()
                time.sleep(interval)
    except KeyboardInterrupt:
        logging.info("057 overlay stopped by user")
    finally:
        logging.info("057 overlay stopped: reversible=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
