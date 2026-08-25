"""Contract and privacy kill tests for the local FARMAKSIA renderer."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent
HTML = (ROOT / "renderer.html").read_text(encoding="utf-8")


def require(needle: str) -> None:
    if needle not in HTML:
        raise SystemExit(f"missing renderer contract: {needle}")


def main() -> int:
    for mode in ("panel", "guided", "map", "analogy", "builder"):
        require(f'data-mode="{mode}"')
        require(f'data-view="{mode}"')

    for entity in ("objective", "queue", "worker", "failure", "verification", "next"):
        require(entity)

    for field in (
        "semantic_priority",
        "disclosure_layers",
        "spatial_anchors",
        "visual_tokens",
        "motion_policy",
        "tempo_policy",
        "peripheral_context",
        "user_controls",
        "reversible_actions",
    ):
        require(field)

    forbidden = (
        "getUserMedia",
        "mediaDevices",
        "WebSocket",
        "XMLHttpRequest",
        "fetch(",
        "eval(",
        "new Function",
    )
    for token in forbidden:
        if token in HTML:
            raise SystemExit(f"privacy/security kill test failed: {token}")

    if "https://" in HTML or "http://" in HTML:
        raise SystemExit("network dependency found in renderer")

    if "<script src=" in HTML:
        raise SystemExit("external script dependency found in renderer")

    for marker in ("sin cámara", "sin red", "fuente semántica permanece constante", "restaurar"):
        require(marker)

    print("FARMAXIA_056_RENDERER_CONTRACT_VALID")
    print("modes=panel,guided,map,analogy,builder")
    print("privacy=no-camera,no-network,no-execution")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
