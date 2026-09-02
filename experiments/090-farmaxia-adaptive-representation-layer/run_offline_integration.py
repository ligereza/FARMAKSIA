"""Run the reproducible offline checks for the first integration seam."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
FARMAXIA_ROOT = HERE.parents[1]


def _run_check(label: str, script: Path, arguments: list[str]) -> dict[str, object]:
    command = [sys.executable, str(script), *arguments]
    completed = subprocess.run(
        command,
        cwd=FARMAXIA_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output_lines = [line for line in completed.stdout.splitlines() if line.strip()]
    error_lines = [line for line in completed.stderr.splitlines() if line.strip()]
    return {
        "label": label,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "exitCode": completed.returncode,
        "summary": output_lines[-1] if output_lines else None,
        "error": error_lines[-1] if error_lines else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xio-root", default=r"C:\IA\XIO")
    parser.add_argument("--lucida-root", default=r"C:\IA\VJ")
    parser.add_argument("--lucida-multi-root")
    args = parser.parse_args()

    checks = [
        _run_check(
            "farmaxia-090-contract",
            HERE / "run_contract_test.py",
            [],
        ),
        _run_check(
            "xio-route-persistence-and-permission",
            HERE / "run_xio_route_handoff_check.py",
            [],
        ),
        _run_check(
            "pupila-lucida-atomic-consumer",
            HERE / "run_lucida_pupila_consumer_check.py",
            ["--lucida-root", args.lucida_root],
        ),
    ]
    if args.lucida_multi_root:
        checks.append(
            _run_check(
                "lucida-multi-transport",
                HERE / "run_lucida_multi_check.py",
                [
                    "--xio-root",
                    args.xio_root,
                    "--lucida-multi-root",
                    args.lucida_multi_root,
                ],
            )
        )

    failed = [check for check in checks if check["status"] != "PASS"]
    result = {
        "status": "PASS" if not failed else "FAIL",
        "checkCount": len(checks),
        "passedCount": len(checks) - len(failed),
        "failedCount": len(failed),
        "multiCheck": "included" if args.lucida_multi_root else "not-requested",
        "checks": checks,
        "networkOpened": False,
        "guiOpened": False,
        "hostActionsExecuted": False,
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
