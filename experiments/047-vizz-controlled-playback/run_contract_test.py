"""Kill tests for the controlled VIZZ playback policy."""

from __future__ import annotations

import sys
from pathlib import Path


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from playback_policy import PlaybackConfig, SceneElement, evaluate_scene  # noqa: E402


SCENE = (
    SceneElement("focus_text", 0.50, 0.50, "text", text=True),
    SceneElement("peripheral_alert", 0.95, 0.10, "alert", base_detail=0.85, peripheral_signal=True),
    SceneElement("peripheral_text", 0.95, 0.90, "text", text=True),
    SceneElement("background", 0.15, 0.85, "background", base_detail=0.90),
)


def main() -> None:
    failures: list[str] = []
    full = evaluate_scene(SCENE, PlaybackConfig("static_full", 0.50, 0.50), "reading")
    full_by_id = {item["element_id"]: item for item in full}
    expected_full = {"focus_text": 1.0, "peripheral_alert": 0.85, "peripheral_text": 1.0, "background": 0.90}
    if any(full_by_id[key]["detail_factor"] != value for key, value in expected_full.items()):
        failures.append("static_full altered scene detail")

    protected = evaluate_scene(SCENE, PlaybackConfig("adaptive_protected", 0.50, 0.50), "reading")
    protected_by_id = {item["element_id"]: item for item in protected}
    if protected_by_id["focus_text"]["zone"] != "foveal":
        failures.append("focus text is not foveal")
    if not protected_by_id["peripheral_alert"]["peripheral_signal_preserved"]:
        failures.append("protected mode damaged a peripheral alert")
    if protected_by_id["peripheral_text"]["text_legible_descriptor"]:
        failures.append("protected mode did not reduce low-priority peripheral text")

    unprotected = evaluate_scene(SCENE, PlaybackConfig("adaptive_unprotected", 0.50, 0.50), "reading")
    unprotected_by_id = {item["element_id"]: item for item in unprotected}
    if unprotected_by_id["peripheral_alert"]["peripheral_signal_preserved"]:
        failures.append("unprotected control unexpectedly preserved peripheral alert")

    clean = evaluate_scene(SCENE, PlaybackConfig("static_clean", 0.50, 0.50), "reading")
    clean_by_id = {item["element_id"]: item for item in clean}
    if clean_by_id["background"]["detail_factor"] >= 0.80:
        failures.append("static_clean did not reduce background-like detail")

    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("VIZZ_047_PLAYBACK_CONTRACT_VALID")


if __name__ == "__main__":
    main()
