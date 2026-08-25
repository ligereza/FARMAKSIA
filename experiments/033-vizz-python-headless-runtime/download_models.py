"""Download the pinned open-source ONNX assets outside git."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).parent
MODEL_DIR = ROOT.parents[1] / ".vizz-models"
BASE_URL = "https://github.com/PINTO0309/screen-eye-tracking/releases/download/onnx"
ASSETS = {
    "retinaface.onnx": {
        "source": f"{BASE_URL}/retinaface_mbn025_with_postprocess_480x640_max1000_th0.70.onnx",
        "sha256": "",
    },
    "gaze.onnx": {
        "source": f"{BASE_URL}/gaze_Nx3x160x160.onnx",
        "sha256": "",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {"schema": "farmaxia:vizz-model-manifest:0.1", "models": {}}
    for name, metadata in ASSETS.items():
        target = MODEL_DIR / name
        if not target.is_file():
            print(f"downloading {name}")
            urllib.request.urlretrieve(metadata["source"], target)
        digest = sha256(target)
        manifest["models"][name] = {
            "source": metadata["source"],
            "sha256": digest,
            "bytes": target.stat().st_size,
            "license_note": "Source project is MIT; model provenance remains external and pinned here.",
        }
        print(f"{name}: {target.stat().st_size} bytes sha256={digest}")
    (MODEL_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("MODELS_READY")


if __name__ == "__main__":
    main()
