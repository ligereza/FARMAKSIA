"""Run the repository-boundary guard with explicit roots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from boundary_matrix import BoundaryMatrixError, inspect_matrix  # noqa: E402


def _parse_root(value: str) -> tuple[str, str]:
    role, separator, root = value.partition("=")
    if not separator or not role or not root:
        raise argparse.ArgumentTypeError("root must use ROLE=PATH")
    return role, root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        action="append",
        type=_parse_root,
        required=True,
        metavar="ROLE=PATH",
        help="explicit root to inspect; repeat for each role",
    )
    args = parser.parse_args()
    entries: dict[str, str] = {}
    for role, root in args.root:
        if role in entries:
            parser.error(f"duplicate role: {role}")
        entries[role] = root
    try:
        report = inspect_matrix(entries)
    except BoundaryMatrixError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
