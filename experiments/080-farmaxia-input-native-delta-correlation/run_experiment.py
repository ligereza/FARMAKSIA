"""Correlate real Excel state deltas with opt-in input observations."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from correlator import classify_delta, correlate, snapshot_excel  # noqa: E402


def scratch_excel() -> dict[str, Any]:
    try:
        import pythoncom
        import win32com.client
    except ImportError as exc:
        return {"status": "EXCEL_COM_UNAVAILABLE", "blocker": type(exc).__name__}
    app = None
    workbook = None
    initialized = False
    salt = os.urandom(32)
    try:
        pythoncom.CoInitialize()
        initialized = True
        app = win32com.client.DispatchEx("Excel.Application")
        app.Visible = False
        app.DisplayAlerts = False
        initial = {"workbook_count": int(app.Workbooks.Count), "worksheet_count": 0}
        workbook = app.Workbooks.Add()
        sheet = workbook.Worksheets(1)
        target = sheet.Range("A1:C1")
        created = snapshot_excel(app, salt, target)
        sheet.Range("A1").Value = 2
        sheet.Range("B1").Value = 3
        sheet.Range("C1").Formula = "=A1+B1"
        modified = snapshot_excel(app, salt, target)
        sheet.Range("A1:C1").ClearContents()
        reverted = snapshot_excel(app, salt, target)
        states = [initial, created, modified, reverted]
        kinds = [
            classify_delta(states[0], states[1]),
            classify_delta(states[1], states[2]),
            classify_delta(states[2], states[3], reversion_target=states[1]),
        ]
        deltas = [
            {"t_monotonic": float(index + 1), "application_class": "excel", "delta_kind": kind}
            for index, kind in enumerate(kinds)
            if kind != "no_change"
        ]
        associations = correlate([], deltas)
        return {
            "status": "EXCEL_SCRATCH_CORRELATION_OBSERVED",
            "application": "Microsoft Excel",
            "version": str(app.Version),
            "transition_kinds": kinds,
            "delta_count": len(deltas),
            "associations_without_input": associations,
            "scratch_mutations": ["create_workbook", "write_values_and_formula", "clear_contents"],
            "user_files_written": False,
            "raw_content_persisted": False,
        }
    except Exception as exc:
        return {"status": "EXCEL_SCRATCH_CORRELATION_UNKNOWN", "blocker": type(exc).__name__}
    finally:
        if workbook is not None:
            try:
                workbook.Close(SaveChanges=False)
            except Exception:
                pass
        if app is not None:
            try:
                app.Quit()
            except Exception:
                pass
        if initialized:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass


def live_excel(duration: float, sample_hz: float, window_ms: float) -> dict[str, Any]:
    try:
        import pythoncom
        import win32com.client
        from input_bridge import KeyboardActivity, read_context
    except ImportError as exc:
        return {"status": "LIVE_DEPENDENCIES_UNAVAILABLE", "blocker": type(exc).__name__}
    app = None
    keyboard = None
    initialized = False
    try:
        pythoncom.CoInitialize()
        initialized = True
        app = win32com.client.GetActiveObject("Excel.Application")
        keyboard = KeyboardActivity()
        keyboard.start()
        salt = os.urandom(32)
        started = time.monotonic()
        deadline = started + duration
        next_sample = started
        previous: dict[str, Any] | None = None
        input_events: list[dict[str, Any]] = []
        delta_events: list[dict[str, Any]] = []
        event_counts: dict[str, int] = {}
        while time.monotonic() < deadline:
            now = time.monotonic()
            if now < next_sample:
                time.sleep(min(0.005, next_sample - now))
                continue
            context = read_context(False)
            keyboard_state = keyboard.snapshot(now)
            if int(keyboard_state["keyboard_event_count"]) > 0:
                input_event = {
                    "t_monotonic": now,
                    "application_class": context["application_class"],
                }
                input_events.append(input_event)
                event_counts["keyboard_activity"] = event_counts.get("keyboard_activity", 0) + 1
            current = snapshot_excel(app, salt)
            if previous is not None:
                kind = classify_delta(previous, current)
                if kind != "no_change":
                    delta_events.append({"t_monotonic": now, "application_class": "excel", "delta_kind": kind})
                    event_counts[kind] = event_counts.get(kind, 0) + 1
            previous = current
            next_sample = max(next_sample + 1.0 / sample_hz, time.monotonic())
        associations = correlate(input_events, delta_events, window_ms)
        for item in associations:
            event_counts[item["status"]] = event_counts.get(item["status"], 0) + 1
        return {
            "status": "LIVE_EXCEL_CORRELATION_OBSERVED",
            "application": "Microsoft Excel",
            "duration_seconds": duration,
            "sample_hz": sample_hz,
            "event_counts": dict(sorted(event_counts.items())),
            "association_count": len(associations),
            "associations": associations,
            "key_values_persisted": False,
            "text_persisted": False,
            "raw_content_persisted": False,
            "intent_claimed": False,
            "actions_performed": [],
            "read_only": True,
        }
    except Exception as exc:
        return {"status": "LIVE_EXCEL_CORRELATION_UNKNOWN", "blocker": type(exc).__name__}
    finally:
        if keyboard is not None:
            keyboard.close()
        if initialized:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass


def validate(result: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if result.get("status") != "INPUT_NATIVE_DELTA_CORRELATION_VERIFIED":
        blockers.append("correlation_not_verified")
    excel = result.get("excel", {})
    if excel.get("status") != "EXCEL_SCRATCH_CORRELATION_OBSERVED":
        blockers.append("excel_scratch_not_observed")
    if excel.get("user_files_written") is not False or excel.get("raw_content_persisted") is not False:
        blockers.append("excel_privacy_boundary_broken")
    if excel.get("transition_kinds") != ["create_entity", "modify_property", "revert"]:
        blockers.append("transition_kernel_mismatch")
    for association in excel.get("associations_without_input", []):
        if association.get("status") != "unassociated_native_delta" or association.get("intent_claimed") is not False:
            blockers.append("scratch_delta_claimed_input")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Input/native state delta correlator")
    parser.add_argument("--mode", choices=("scratch", "live-excel"), default="scratch")
    parser.add_argument("--duration", type=float, default=10.0)
    parser.add_argument("--sample-hz", type=float, default=8.0)
    parser.add_argument("--window-ms", type=float, default=750.0)
    args = parser.parse_args()
    if args.mode == "scratch":
        excel = scratch_excel()
        result: dict[str, Any] = {
            "status": "INPUT_NATIVE_DELTA_CORRELATION_VERIFIED" if excel.get("status") == "EXCEL_SCRATCH_CORRELATION_OBSERVED" else "INPUT_NATIVE_DELTA_CORRELATION_PARTIAL",
            "experiment": "080-farmaxia-input-native-delta-correlation",
            "mode": "scratch",
            "excel": excel,
            "input_observation": "not_started_in_scratch_mode",
            "human_input_claimed": False,
            "safety": {
                "network_used": False,
                "screen_capture": False,
                "camera_capture": False,
                "mouse_or_keyboard_injected": False,
                "source_write_attempted": False,
            },
        }
        result["validation_blockers"] = validate(result)
    else:
        if args.duration <= 0.0 or args.sample_hz <= 0.0 or args.window_ms <= 0.0:
            raise ValueError("duration, sample_hz and window_ms must be positive")
        live = live_excel(args.duration, args.sample_hz, args.window_ms)
        result = {
            "status": live.get("status"),
            "experiment": "080-farmaxia-input-native-delta-correlation",
            "mode": "live-excel",
            "live": live,
            "safety": {
                "network_used": False,
                "screen_capture": False,
                "camera_capture": False,
                "mouse_or_keyboard_injected": False,
                "source_write_attempted": False,
            },
        }
        result["validation_blockers"] = [] if live.get("status") == "LIVE_EXCEL_CORRELATION_OBSERVED" else ["live_excel_not_observed"]
    if result["validation_blockers"]:
        result["status"] = "BLOCKED"
    print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
