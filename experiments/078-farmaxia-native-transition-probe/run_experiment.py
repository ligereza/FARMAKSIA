"""Probe typed state transitions in isolated Excel and Blender processes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Any


EXPERIMENT = "078-farmaxia-native-transition-probe"


def discover_blender(requested: str | None = None) -> Path | None:
    if requested:
        candidate = Path(requested)
        return candidate if candidate.is_file() else None
    root = Path("C:/Program Files/Blender Foundation")
    candidates: list[tuple[tuple[int, ...], Path]] = []
    for executable in root.glob("Blender */blender.exe"):
        match = re.search(r"Blender (\d+(?:\.\d+)*)", executable.parent.name, re.IGNORECASE)
        if match:
            version = tuple(int(part) for part in match.group(1).split("."))
            candidates.append((version, executable))
    return max(candidates, default=((), None))[1]


def inspect_excel_transition() -> dict[str, Any]:
    try:
        import pythoncom
        import win32com.client
    except ImportError as exc:
        return {"status": "EXCEL_COM_UNAVAILABLE", "blocker": type(exc).__name__}

    app = None
    initialized = False
    workbook = None
    try:
        pythoncom.CoInitialize()
        initialized = True
        app = win32com.client.DispatchEx("Excel.Application")
        app.Visible = False
        app.DisplayAlerts = False
        workbook = app.Workbooks.Add()
        sheet = workbook.Worksheets(1)
        target = sheet.Range("A1:C1")
        before = {
            "workbook_count": int(app.Workbooks.Count),
            "nonempty_cells_in_target": int(app.WorksheetFunction.CountA(target)),
        }

        # Scratch-only state transition. No physical keyboard or mouse input.
        sheet.Range("A1").Value = 2
        sheet.Range("B1").Value = 3
        sheet.Range("C1").Formula = "=A1+B1"
        after_modify = {
            "nonempty_cells_in_target": int(app.WorksheetFunction.CountA(target)),
            "formula_cells_in_target": 1 if str(sheet.Range("C1").Formula).startswith("=") else 0,
            "computed_numeric_result": float(sheet.Range("C1").Value),
        }

        sheet.Range("A1:C1").ClearContents()
        after_revert = {
            "nonempty_cells_in_target": int(app.WorksheetFunction.CountA(target)),
        }
        return {
            "status": "EXCEL_SCRATCH_TRANSITION_OBSERVED",
            "application": "Microsoft Excel",
            "version": str(app.Version),
            "before": before,
            "after_modify": after_modify,
            "after_revert": after_revert,
            "scratch_mutations": ["write_values_and_formula", "clear_contents"],
            "user_files_written": False,
        }
    except Exception as exc:
        return {"status": "EXCEL_SCRATCH_TRANSITION_UNKNOWN", "blocker": type(exc).__name__}
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


def blender_expression() -> str:
    return (
        "import bpy,json;"
        "initial_selected=list(bpy.context.selected_objects);initial_active=bpy.context.active_object;"
        "before={'object_count':len(bpy.data.objects),'selected_count':len(initial_selected),'active_present':initial_active is not None};"
        "mesh=bpy.data.meshes.new('_farmaxia_078_scratch_mesh');"
        "obj=bpy.data.objects.new('_farmaxia_078_scratch_object',mesh);"
        "bpy.context.scene.collection.objects.link(obj);"
        "after_create={'object_count':len(bpy.data.objects)};"
        "obj.select_set(True);bpy.context.view_layer.objects.active=obj;"
        "after_select={'selected_count':len(bpy.context.selected_objects),'active_is_scratch':bpy.context.active_object is obj};"
        "obj.location.x=2.0;"
        "after_modify={'location_x':float(obj.location.x)};"
        "obj.location.x=0.0;obj.select_set(False);bpy.context.view_layer.objects.active=None;"
        "bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(mesh);"
        "[item.select_set(True) for item in initial_selected if item.name in bpy.data.objects];"
        "bpy.context.view_layer.objects.active=initial_active if initial_active and initial_active.name in bpy.data.objects else None;"
        "after_revert={'object_count':len(bpy.data.objects),'selected_count':len(bpy.context.selected_objects),"
        "'active_restored':bpy.context.active_object is initial_active};"
        "result={'status':'BLENDER_SCRATCH_TRANSITION_OBSERVED','application':'Blender','version':list(bpy.app.version),"
        "'version_string':str(bpy.app.version_string),'before':before,'after_create':after_create,"
        "'after_select':after_select,'after_modify':after_modify,'after_revert':after_revert,"
        "'scratch_mutations':['create_object','select_object','modify_location','remove_object'],"
        "'user_files_written':False};"
        "print('FARMAXIA_078_BLENDER='+json.dumps(result,sort_keys=True))"
    )


def inspect_blender_transition(executable: Path | None) -> dict[str, Any]:
    if executable is None:
        return {"status": "BLENDER_EXECUTABLE_UNAVAILABLE", "blocker": "blender_not_found"}
    try:
        completed = subprocess.run(
            [str(executable), "--background", "--factory-startup", "--python-expr", blender_expression()],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=45,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "BLENDER_SCRATCH_TRANSITION_UNKNOWN", "blocker": type(exc).__name__}
    marker = "FARMAXIA_078_BLENDER="
    line = next((line for line in completed.stdout.splitlines() if line.startswith(marker)), None)
    if completed.returncode or line is None:
        return {"status": "BLENDER_SCRATCH_TRANSITION_UNKNOWN", "blocker": "marker_missing", "returncode": completed.returncode}
    return json.loads(line[len(marker) :])


def common_transitions() -> list[dict[str, Any]]:
    return [
        {"kind": "create_entity", "invariant": "a new editable entity exists"},
        {"kind": "select_entity", "invariant": "the active entity is addressable"},
        {"kind": "modify_property", "invariant": "a typed property changes"},
        {"kind": "revert", "invariant": "the scratch state returns to its initial counts"},
    ]


def validate(result: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if result.get("status") != "NATIVE_TRANSITIONS_VERIFIED":
        blockers.append("transition_probe_not_verified")
    excel = result.get("excel", {})
    blender = result.get("blender", {})
    if excel.get("status") != "EXCEL_SCRATCH_TRANSITION_OBSERVED":
        blockers.append("excel_transition_not_observed")
    if blender.get("status") != "BLENDER_SCRATCH_TRANSITION_OBSERVED":
        blockers.append("blender_transition_not_observed")
    if excel.get("user_files_written") is not False or blender.get("user_files_written") is not False:
        blockers.append("user_file_write_boundary_broken")
    if result.get("physical_input_injected") is not False:
        blockers.append("physical_input_boundary_broken")
    transitions = result.get("common_transitions")
    if not isinstance(transitions, list) or [item.get("kind") for item in transitions] != [
        "create_entity",
        "select_entity",
        "modify_property",
        "revert",
    ]:
        blockers.append("common_transition_kernel_invalid")
    safety = result.get("safety", {})
    for field in ("network_used", "screen_capture", "camera_capture", "mouse_or_keyboard_injected", "source_write_attempted"):
        if safety.get(field) is not False:
            blockers.append(f"unsafe_capability_enabled:{field}")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Real Excel/Blender scratch transition probe")
    parser.add_argument("--blender", help="optional Blender executable path")
    args = parser.parse_args()
    excel = inspect_excel_transition()
    blender = inspect_blender_transition(discover_blender(args.blender))
    result: dict[str, Any] = {
        "status": "NATIVE_TRANSITIONS_VERIFIED"
        if excel.get("status") == "EXCEL_SCRATCH_TRANSITION_OBSERVED" and blender.get("status") == "BLENDER_SCRATCH_TRANSITION_OBSERVED"
        else "NATIVE_TRANSITIONS_PARTIAL",
        "experiment": EXPERIMENT,
        "excel": excel,
        "blender": blender,
        "common_transitions": common_transitions(),
        "scratch_scope": "isolated_unsaved_application_sessions",
        "physical_input_injected": False,
        "safety": {
            "network_used": False,
            "screen_capture": False,
            "camera_capture": False,
            "mouse_or_keyboard_injected": False,
            "source_write_attempted": False,
        },
    }
    result["validation_blockers"] = validate(result)
    if result["validation_blockers"]:
        result["status"] = "BLOCKED"
    print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
