from __future__ import annotations
import json
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from iris_farmaksia_adapter import adapt  # noqa: E402

def main() -> None:
    plan = json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))
    result = adapt(plan)
    if not result["admitted"]:
        raise SystemExit(json.dumps(result, indent=2))
    print("IRIS_FARMAKSIA_ADAPTER_VERIFIED")
    print(json.dumps({"status": result["status"], "order": [x["id"] for x in result["ordering"]["items"]], "provenance": result["provenance"]}, indent=2))

if __name__ == "__main__":
    main()
