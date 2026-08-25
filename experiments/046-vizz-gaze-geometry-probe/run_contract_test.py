"""Contract and kill tests for the geometry-first VIZZ probe."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import sys


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("vizz_046_runner", HERE / "run_experiment.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load VIZZ 046 runner")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def main() -> None:
    layout = runner.make_layout()
    target = (0.12, -0.08, 0.72)
    failures: list[str] = []

    normal = runner.summarize_case("normal", runner.observation_for(target), layout)
    if normal["state"]["status"] != "VALID" or normal["state"]["monitor_id"] != "primary":
        failures.append("valid primary gaze did not resolve to primary monitor")
    if normal["policy"]["mode"] != "ADAPTIVE_REGION_DESCRIPTOR":
        failures.append("valid state did not produce an adaptive descriptor")
    if normal["policy"]["preserve_peripheral_signals"] is not True:
        failures.append("adaptive policy does not preserve peripheral signals")
    if normal["state"]["distance_m"] is None or not (0.72 < normal["state"]["distance_m"] < 0.75):
        failures.append("valid state did not expose physical gaze distance")

    moved_head = runner.summarize_case(
        "moved-head",
        runner.observation_for(target, eyes=((0.08, 0.04, 0.02), (0.144, 0.04, 0.02))),
        layout,
    )
    uv_a = normal["state"]["uv"]
    uv_b = moved_head["state"]["uv"]
    if uv_a is None or uv_b is None or max(abs(uv_a[i] - uv_b[i]) for i in range(2)) > 1e-9:
        failures.append("head translation with a fixed world target changed screen UV")

    context = runner.summarize_case(
        "keyboard",
        runner.observation_for(target),
        layout,
        runner.InteractionContext(keyboard_active=True, keyboard_event_count=2, mouse_screen=(100, 100)),
    )
    if context["mouse_is_ground_truth"] is not False or context["state"]["status"] != "VALID":
        failures.append("mouse/keyboard context contaminated gaze state")
    if context["policy"]["keyboard_active"] is not True:
        failures.append("keyboard activity was not preserved as context")

    angled_layout = runner.make_angled_layout()
    angled_monitor = angled_layout.monitors[0]
    angled_target = (
        angled_monitor.origin[0] + angled_monitor.horizontal_axis[0] * 0.16,
        angled_monitor.origin[1] + angled_monitor.vertical_axis[1] * 0.04,
        angled_monitor.origin[2] + angled_monitor.horizontal_axis[2] * 0.16,
    )
    angled = runner.summarize_case(
        "angled",
        runner.observation_for(angled_target, layout_version=angled_layout.version),
        angled_layout,
    )
    if angled["state"]["status"] != "VALID" or angled["state"]["monitor_id"] != "angled":
        failures.append("non-perpendicular monitor plane did not resolve")
    elif max(abs(angled["state"]["uv"][index] - expected) for index, expected in enumerate((0.7, 0.5888888888888889))) > 1e-6:
        failures.append("angled monitor UV is inconsistent with its physical axes")

    unknown_cases = {
        "low_confidence": runner.summarize_case("low", runner.observation_for(target, confidence=0.2), layout),
        "stale_layout": runner.summarize_case("stale", runner.observation_for(target, layout_version="old"), layout),
        "missing_eye": runner.summarize_case(
            "missing",
            runner.GazeObservation(1.0, None, (0.032, 0.0, 0.0), (0.0, 0.0, 1.0), 0.98, 0.35, layout.version),
            layout,
        ),
        "ambiguous": runner.summarize_case("ambiguous", runner.observation_for(target), runner.make_layout(overlapping=True)),
    }
    expected_reasons = {
        "low_confidence": "low_confidence",
        "stale_layout": "display_layout_changed",
        "missing_eye": "missing_eye",
        "ambiguous": "ambiguous_monitor",
    }
    for name, case in unknown_cases.items():
        if case["state"]["status"] != "UNKNOWN":
            failures.append(f"{name} did not fail closed")
        if case["state"]["unknown_reason"] != expected_reasons[name]:
            failures.append(f"{name} has the wrong UNKNOWN reason")
        if case["policy"]["mode"] != "STATIC_FALLBACK":
            failures.append(f"{name} did not select static fallback")

    policy = runner.summarize_case(
        "latency",
        runner.observation_for(target, uncertainty_deg=1.0),
        layout,
        gaze_speed_deg_s=20.0,
        latency_ms=100.0,
    )
    if not math.isclose(policy["state"]["safe_radius_deg"], 6.0, abs_tol=1e-9):
        failures.append("safe radius does not include base, latency motion and uncertainty")

    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("VIZZ_046_GEOMETRY_CONTRACT_VALID")


if __name__ == "__main__":
    main()
