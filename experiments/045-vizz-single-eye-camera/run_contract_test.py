"""Retirement contract for the removed VIZZ 045 optical prototype."""

from __future__ import annotations

from pathlib import Path


HERE = Path(__file__).parent
MODULE_PATH = HERE / "eye_camera_complete.py"


def main() -> None:
    readme = (HERE / "README.md").read_text(encoding="utf-8").lower()
    if MODULE_PATH.exists():
        raise SystemExit("VIZZ_045_RETIREMENT_INVALID: removed optical prototype still exists")
    if "retirado" not in readme or "044" not in readme:
        raise SystemExit("VIZZ_045_RETIREMENT_INVALID: retirement boundary is undocumented")
    print("VIZZ_045_RETIREMENT_CONTRACT_VALID")


if __name__ == "__main__":
    main()
