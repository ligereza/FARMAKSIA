"""Check that FARMAKSIA remains a research archive, not a product runtime."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_EXPERIMENTS = (
    "090-farmaxia-adaptive-representation-layer",
    "091-lucida-pupila-visual-acceptance",
    "092-pupila-temporal-integration",
    "093-iris-representation-ordering",
)


def main() -> int:
    failures: list[str] = []

    for relative in ("README.md", "LICENSE_POLICY.md", "RESEARCH_LOOP.md"):
        if not (ROOT / relative).is_file():
            failures.append(f"missing research boundary document: {relative}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for project in ("X-ANA-X", "PUPILA", "LUCIDA", "FARMAKSIA"):
        if project not in readme:
            failures.append(f"README omits active project boundary: {project}")

    for experiment in ACTIVE_EXPERIMENTS:
        base = ROOT / "experiments" / experiment
        for filename in ("README.md", "provenance.json"):
            if not (base / filename).is_file():
                failures.append(f"missing {filename} for {experiment}")

    retired_bundle = ROOT / "experiments" / "030-vizz-webgazer-opt-in"
    if retired_bundle.exists():
        failures.append("retired third-party WebGazer bundle remains in the active tree")

    if failures:
        print("LAB_STATE_INVALID")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("LAB_STATE_VALID")
    print(f"active_experiment_records={len(ACTIVE_EXPERIMENTS)}")
    print("runtime_ownership=project_boundaries_preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
