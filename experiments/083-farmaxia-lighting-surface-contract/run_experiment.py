"""Verify a reversible, read-only grandMA3-to-Titan surface contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lighting_surface_contract import ContractError, LightingSurfaceContract, TASKS


HERE = Path(__file__).resolve().parent


def load_fixture() -> dict[str, Any]:
    return json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    try:
        contract = LightingSurfaceContract.from_value(fixture)
    except (ContractError, TypeError, ValueError) as exc:
        return {
            "experiment": "083-farmaxia-lighting-surface-contract",
            "status": "BLOCKED",
            "blockers": [type(exc).__name__ + ": " + str(exc)],
        }

    roundtrips: list[dict[str, Any]] = []
    for task in sorted(TASKS):
        region = contract.region_for_task(task)
        local = (0.37, 0.63)
        destination = contract.preview_point(task, local)
        source = contract.inverse_point(task, destination)
        error = max(abs(source[index] - region.source_rect.forward(local)[index]) for index in (0, 1))
        roundtrips.append({"task": task, "max_error": error})
        if error > 1e-12:
            blockers.append(f"inverse_error:{task}")

    expectations = fixture.get("expectations", {})
    if expectations.get("observed_surfaces") is not False:
        blockers.append("observed_surface_claim_without_runtime")
    if expectations.get("external_execution") is not False:
        blockers.append("external_execution_not_blocked")
    if expectations.get("network_used") is not False:
        blockers.append("network_boundary_not_closed")
    if expectations.get("input_injected") is not False:
        blockers.append("input_injection_not_blocked")
    if expectations.get("source_write_attempted") is not False:
        blockers.append("source_write_not_blocked")

    status = "LIGHTING_SURFACE_CONTRACT_VERIFIED" if not blockers else "BLOCKED"
    return {
        "experiment": "083-farmaxia-lighting-surface-contract",
        "status": status,
        "blockers": sorted(set(blockers)),
        "contract": contract.as_summary(),
        "mapping": [
            {
                "task": region.canonical_task,
                "source_role": region.source_role,
                "target_term": region.target_term,
                "status": region.status,
                "confidence": region.confidence,
            }
            for region in contract.regions
        ],
        "roundtrips": roundtrips,
        "safety": {
            "network_used": False,
            "external_execution": False,
            "input_injected": False,
            "source_write_attempted": False,
            "observed_surfaces": False,
        },
        "scope_limit": "declarative fixture only; no grandMA3 or Titan window has been observed yet",
    }


def main() -> None:
    print(json.dumps(compile_fixture(load_fixture()), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
