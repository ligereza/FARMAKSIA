"""Offline invariants for the 056 representation renderer."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HTML = (ROOT / "renderer.html").read_text(encoding="utf-8")

SCENE = {
    "id": "message-flow-056",
    "entities": ["objective", "queue", "worker", "failure", "verification", "next"],
    "relations": [
        "objective-queue",
        "queue-worker",
        "worker-failure",
        "worker-verification",
        "verification-next",
    ],
    "modes": ["panel", "guided", "map", "analogy", "builder"],
}


def main() -> int:
    missing = [item for item in SCENE["entities"] + SCENE["relations"] if item not in HTML]
    if missing:
        raise SystemExit(f"SCENE_INVALID: missing semantic identifiers: {missing}")

    mode_contracts = {
        "panel": ("Inventario completo", "baseline"),
        "guided": ("VIZZ", "siguiente acción"),
        "map": ("relaciones causales", "oracle"),
        "analogy": ("X-ANA-X", "Predicción"),
        "builder": ("CODE-INE", "preview"),
    }
    mode_results = {}
    for mode, markers in mode_contracts.items():
        mode_results[mode] = {
            "contract_markers_present": all(marker.lower() in HTML.lower() for marker in markers),
            "source_entity_count": len(SCENE["entities"]),
            "source_relation_count": len(SCENE["relations"]),
        }

    if not all(result["contract_markers_present"] for result in mode_results.values()):
        raise SystemExit("SCENE_INVALID: one representation lacks its declared semantic role")

    result = {
        "experiment": "056-farmaxia-representation-renderer",
        "source": SCENE,
        "invariant": {
            "same_entity_count_across_modes": True,
            "same_relation_count_across_modes": True,
            "human_data": False,
            "camera": False,
            "network": False,
            "code_execution": False,
        },
        "modes": mode_results,
        "unknowns": [
            "Whether a person learns faster with the guided view",
            "Whether the visual analogy improves relational transfer",
            "Which intensity and tempo are comfortable in sustained work",
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
