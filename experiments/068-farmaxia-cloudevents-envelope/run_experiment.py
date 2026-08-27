"""Validate the 068 CloudEvents fixture through the shared FARMAKSIA kernel."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1] / "research" / "tools"
sys.path.insert(0, str(TOOLS))

from cloudevents_contract import compile_envelope, load_json  # noqa: E402


FIXTURE = HERE / "fixture.json"


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    result = compile_envelope(fixture)
    blockers = list(result["blockers"])
    expected_order = fixture.get("expected_canonical_order")
    if expected_order is not None and result["envelope"]["canonical_order"] != expected_order:
        blockers.append("canonical_order_mismatch")
    result["experiment"] = "068-farmaxia-cloudevents-envelope"
    result["blockers"] = sorted(set(blockers))
    result["status"] = "CLOUDEVENTS_ENVELOPE_VERIFIED" if not blockers else "BLOCKED"
    result["scope_limit"] = (
        "local synthetic envelope validation; no broker, network, signature, "
        "schema registry or production interoperability claim"
    )
    return result


def main() -> None:
    print(json.dumps(compile_fixture(load_json(FIXTURE)), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
