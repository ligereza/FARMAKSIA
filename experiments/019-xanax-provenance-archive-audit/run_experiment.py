"""Compare chain-of-custody analogy with direct provenance validation."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).parent
ROOT = HERE.parents[1]
VALIDATOR_PATH = ROOT / "research" / "tools" / "validate_provenance.py"
SOURCE_CARD = HERE / "source_card.json"


def load_validator() -> Any:
    spec = importlib.util.spec_from_file_location("farmaxia_provenance_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load provenance validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manifest_for(root: Path, case: str) -> Path:
    record = root / "record.txt"
    if case != "missing-file":
        record.write_text("declared control record\n", encoding="utf-8")
    digest = hashlib.sha256(record.read_bytes()).hexdigest().upper() if record.is_file() else "0" * 64
    if case == "hash-mismatch":
        digest = "0" * 64
    required_entities = ["missing-entity"] if case == "unknown-reference" else ["entity-record"]
    manifest = {
        "schema": "farmaxia:provenance-manifest:0.1",
        "agents": [{"id": "agent", "type": "software_agent"}],
        "entities": [
            {
                "id": "entity-record",
                "type": "entity",
                "path": "record.txt",
                "sha256": digest,
                "authority": "human_declared_fixture",
            }
        ],
        "activities": [],
        "queries": [
            {
                "id": "query",
                "authority": "experiment_defined",
                "required_entities": required_entities,
            }
        ],
        "unknowns": [],
    }
    path = root / "provenance.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def direct_route(validator: Any, case: str) -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix="farmaxia-xanax-019-") as directory:
        path = manifest_for(Path(directory), case)
        try:
            validator.validate(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return {"status": "invalid", "reason": str(exc)}
        return {"status": "valid", "reason": "all declared provenance checks passed"}


def analogy_prediction(source: dict[str, Any], case: str) -> dict[str, str]:
    expected = {
        "valid": "valid",
        "hash-mismatch": "invalid",
        "unknown-reference": "invalid",
        "missing-file": "invalid",
    }[case]
    return {
        "source": source["id"],
        "predicted_status": expected,
        "prediction": source["prediction"],
    }


def main() -> None:
    validator = load_validator()
    source = json.loads(SOURCE_CARD.read_text(encoding="utf-8"))
    cases = ["valid", "hash-mismatch", "unknown-reference", "missing-file"]
    direct = {case: direct_route(validator, case) for case in cases}
    analogy = {case: analogy_prediction(source, case) for case in cases}
    direct_statuses = {case: result["status"] for case, result in direct.items()}
    analogy_statuses = {case: result["predicted_status"] for case, result in analogy.items()}
    print(
        json.dumps(
            {
                "experiment": "019-xanax-provenance-archive-audit",
                "target": "research/tools/validate_provenance.py",
                "cases": cases,
                "direct_route": direct,
                "analogy_route": analogy,
                "comparison": {
                    "same_statuses": direct_statuses == analogy_statuses,
                    "unique_analogy_decision": direct_statuses != analogy_statuses,
                    "novelty_status": "not_demonstrated",
                    "residue": "analogy vocabulary does not add a validator state",
                },
                "human_data": False,
                "network_used": False,
                "arbitrary_corpus": False,
                "scope_limit": "ephemeral controlled manifests; no human provenance or analogy efficacy claim",
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
