"""Static contract test for the retained GPU compositor."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = (ROOT / "Program.cs").read_text(encoding="utf-8")
PROJECT = (ROOT / "058-farmaxia-gpu-composition-runtime.csproj").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")

required = [
    "D3D11.D3D11CreateDevice",
    "DriverType.Hardware",
    "CreateSwapChainForComposition",
    "AlphaMode.Premultiplied",
    "SwapEffect.FlipSequential",
    "DComp.DCompositionCreateDevice",
    "Present(1, PresentFlags.None)",
    "ConcurrentQueue<RenderCommand>",
    "WS_EX_LAYERED",
    "WS_EX_TRANSPARENT",
    "WM_NCHITTEST -> HTTRANSPARENT",
    "WM_MOUSEACTIVATE -> MA_NOACTIVATE",
]
for marker in required:
    if marker not in SOURCE:
        raise SystemExit(f"missing source marker: {marker}")

for package in ("Vortice.Direct3D11", "Vortice.DirectComposition", "Vortice.DXGI", "Vortice.D3DCompiler"):
    if package not in PROJECT:
        raise SystemExit(f"missing package: {package}")

for forbidden in (
    "UpdateLayeredWindow",
    "Windows.Graphics.Capture",
    "getUserMedia",
    "WebSocket",
    "HttpClient",
    "Socket",
    "eval(",
    "new Function",
):
    if forbidden in SOURCE:
        raise SystemExit(f"forbidden capability: {forbidden}")

if SOURCE.count("Native.SetWindowPos(") != 1:
    raise SystemExit("z-order must be established once, outside the render loop")
if SOURCE.count("Present(1,") != 1:
    raise SystemExit("present cadence must be explicit and bounded")

for marker in ("Contrato de estabilidad", "Una escena estatica", "no captura", "--stdin"):
    if marker not in README:
        raise SystemExit(f"README missing marker: {marker}")

print("FARMAXIA_058_GPU_COMPOSITION_CONTRACT_VALID")
print("d3d11=hardware-directcomposition=retained-alpha=premultiplied-network=no-camera=no")
