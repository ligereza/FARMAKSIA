"""Static contract for the explicit, passive selected-window preview."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = (HERE / "native" / "main.cpp").read_text(encoding="utf-8")
README = (HERE / "README.md").read_text(encoding="utf-8")


def main() -> None:
    required = (
        "GraphicsCapturePicker",
        "PickSingleItemAsync",
        "IInitializeWithWindow",
        "GraphicsCaptureSession::IsSupported",
        "OnFrame",
        "preview",
        "WINDOW_PREVIEW_SELECTED",
    )
    for marker in required:
        assert marker in SOURCE or marker in README, f"missing preview contract: {marker}"
    forbidden = (
        "EnumWindows",
        "FindWindow",
        "GetWindowText",
        "GetForegroundWindow",
        "SendInput",
        "mouse_event",
        "keybd_event",
        "SetCursorPos",
        "CreateCaptureItemForWindow",
        "WriteFile",
        "CreateFile",
        "WebSocket",
        "WinHttp",
    )
    for marker in forbidden:
        assert marker not in SOURCE, f"preview has forbidden capability: {marker}"
    for marker in ("PickSingleItemAsync", "FrameArrived", "selector seguro", "no intercepta input"):
        assert marker.lower() in (SOURCE + README).lower(), f"documentation missing: {marker}"
    print("FARMAXIA_082_SELECTED_WINDOW_PREVIEW_CONTRACT_VALID")


if __name__ == "__main__":
    main()
