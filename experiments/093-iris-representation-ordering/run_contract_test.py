from __future__ import annotations
import json
from copy import deepcopy
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from iris_farmaksia_adapter import adapt  # noqa: E402
BASE = json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))

def expect_blocked(change: dict, blocker: str) -> None:
    plan = deepcopy(BASE); plan.update(change)
    result = adapt(plan)
    assert blocker in result["blockers"], (blocker, result["blockers"])

def main() -> None:
    result = adapt(BASE)
    assert result["admitted"]
    assert [item["sourceId"] for item in result["ordering"]["items"]] == ["record-demo-001", "record-demo-002"]
    assert result["identity"]["contextIds"] == ["record-demo-004"]
    expect_blocked({"authorialOrder": ["record-iris-002", "work-iris-001"]}, "authorial_order_mismatch")
    expect_blocked({"selectedIds": ["work-iris-001", "missing"]}, "selected_item_missing:missing")
    expect_blocked({"verification": {"independent": False, "passed": True}}, "independent_verification_missing")
    expect_blocked({"objective": {"aesthetic": True}}, "aesthetic_optimality_not_admitted")
    print("IRIS_FARMAKSIA_CONTRACT_TESTS_PASSED")

if __name__ == "__main__":
    main()
