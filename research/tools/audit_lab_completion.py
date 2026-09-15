"""Validate provenance and no-human-data bounds for current research slices."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_EXPERIMENTS = (
    "090-farmaxia-adaptive-representation-layer",
    "091-lucida-pupila-visual-acceptance",
    "092-pupila-temporal-integration",
    "093-iris-representation-ordering",
)
PROHIBITED_TRUE = re.compile(
    r"(?:human_data|raw_capture|devices_started|network_used)\s*['\"]?\s*:\s*true"
    r"|(?:human_data|raw_capture)\s*=\s*True",
    re.IGNORECASE,
)


def main() -> int:
    failures: list[str] = []
    for experiment in ACTIVE_EXPERIMENTS:
        manifest_path = ROOT / "experiments" / experiment / "provenance.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            failures.append(f"invalid provenance for {experiment}: {error}")
            continue
        if not isinstance(manifest, dict) or not manifest.get("experiment"):
            failures.append(f"provenance lacks experiment identity: {experiment}")

    for path in (ROOT / "experiments").rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".py"}:
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if PROHIBITED_TRUE.search(content):
                failures.append(f"prohibited human/device/network flag: {path.relative_to(ROOT)}")

    retired_bundle = ROOT / "experiments" / "030-vizz-webgazer-opt-in"
    if retired_bundle.exists():
        failures.append("retired third-party bundle remains in the active tree")

    if failures:
        print("LAB_COMPLETION_INVALID")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("LAB_COMPLETION_VALID")
    print(f"provenance_records={len(ACTIVE_EXPERIMENTS)}")
    print("personal_data=not_claimed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
