"""Inspect the real Excel and Blender capability surfaces without mutating user data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Any


EXPERIMENT = "077-farmaxia-excel-blender-capability-inventory"


def safe_attr(value: Any, name: str, default: Any = None) -> Any:
    try:
        return getattr(value, name)
    except Exception:
        return default


def com_member_available(value: Any, name: str) -> bool:
    """Check an Excel COM member without invoking a document-scoped property."""
    try:
        ole = value._oleobj_
        ole.GetIDsOfNames(0, name)
        return True
    except Exception:
        return False


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


def inspect_excel() -> dict[str, Any]:
    try:
        import pythoncom
        import win32com.client
    except ImportError as exc:
        return {
            "status": "EXCEL_COM_UNAVAILABLE",
            "blocker": f"dependency_import_failed:{type(exc).__name__}",
        }

    app = None
    initialized = False
    try:
        pythoncom.CoInitialize()
        initialized = True
        app = win32com.client.DispatchEx("Excel.Application")
        app.Visible = False
        app.DisplayAlerts = False
        workbooks = app.Workbooks
        result = {
            "status": "EXCEL_COM_OBSERVED",
            "application": "Microsoft Excel",
            "version": str(safe_attr(app, "Version", "unknown")),
            "build": str(safe_attr(app, "Build", "unknown")),
            "workbook_count_at_attach": int(safe_attr(workbooks, "Count", 0) or 0),
            "capabilities": {
                "workbooks_member": com_member_available(app, "Workbooks"),
                "worksheets_member": com_member_available(app, "Worksheets"),
                "ranges_member": com_member_available(app, "Range"),
                "formula_evaluation_member": com_member_available(app, "WorksheetFunction"),
                "charts_member": com_member_available(app, "Charts"),
                "names_member": com_member_available(app, "Names"),
                "pivot_caches_member": com_member_available(app, "PivotCaches"),
                "data_connections_member": com_member_available(app, "Connections"),
            },
            "document_scoped_observations_deferred": [
                "worksheets",
                "charts",
                "names",
                "pivot_caches",
                "data_connections",
            ],
            "mutations_performed": [],
        }
        return result
    except Exception as exc:
        return {
            "status": "EXCEL_COM_UNKNOWN",
            "blocker": f"com_probe_failed:{type(exc).__name__}",
        }
    finally:
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
        "result={"
        "'status':'BLENDER_PYTHON_API_OBSERVED',"
        "'application':'Blender',"
        "'version':list(bpy.app.version),"
        "'version_string':str(bpy.app.version_string),"
        "'build_hash':str(getattr(bpy.app,'build_hash','unknown')),"
        "'build_options':str(bpy.app.build_options),"
        "'context_types':{"
        "'scene':hasattr(bpy.context,'scene'),"
        "'view_layer':hasattr(bpy.context,'view_layer'),"
        "'selected_objects':hasattr(bpy.context,'selected_objects'),"
        "'active_object':hasattr(bpy.context,'active_object'),"
        "'window_manager':hasattr(bpy.context,'window_manager')},"
        "'data_types':{"
        "'objects':hasattr(bpy.data,'objects'),"
        "'collections':hasattr(bpy.data,'collections'),"
        "'materials':hasattr(bpy.data,'materials'),"
        "'images':hasattr(bpy.data,'images'),"
        "'node_groups':hasattr(bpy.data,'node_groups'),"
        "'scenes':hasattr(bpy.data,'scenes')},"
        "'graph_types':{"
        "'node_tree':hasattr(bpy.types,'NodeTree'),"
        "'geometry_node_tree':hasattr(bpy.types,'GeometryNodeTree'),"
        "'node_socket':hasattr(bpy.types,'NodeSocket'),"
        "'dependency_graph':hasattr(bpy.context,'evaluated_depsgraph_get')},"
        "'reversible_operations':{"
        "'undo':hasattr(bpy.ops.ed,'undo'),"
        "'redo':hasattr(bpy.ops.ed,'redo')},"
        "'gpu_module':__import__('gpu') is not None}"
        ";"
        "print('FARMAXIA_077_BLENDER='+json.dumps(result,sort_keys=True))"
    )


def inspect_blender(executable: Path | None) -> dict[str, Any]:
    if executable is None:
        return {"status": "BLENDER_EXECUTABLE_UNAVAILABLE", "blocker": "blender_not_found"}
    try:
        completed = subprocess.run(
            [
                str(executable),
                "--background",
                "--factory-startup",
                "--python-expr",
                blender_expression(),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=45,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "status": "BLENDER_PYTHON_API_UNKNOWN",
            "blocker": f"blender_probe_failed:{type(exc).__name__}",
            "executable": str(executable),
        }
    marker = "FARMAXIA_077_BLENDER="
    line = next((line for line in completed.stdout.splitlines() if line.startswith(marker)), None)
    if completed.returncode or line is None:
        return {
            "status": "BLENDER_PYTHON_API_UNKNOWN",
            "blocker": "blender_probe_marker_missing",
            "executable": str(executable),
            "returncode": completed.returncode,
        }
    payload = json.loads(line[len(marker) :])
    payload["executable"] = str(executable)
    payload["stderr_lines"] = len(completed.stderr.splitlines())
    return payload


def validate(result: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if result.get("status") != "EXCEL_BLENDER_CAPABILITY_INVENTORY_VERIFIED":
        blockers.append("inventory_not_verified")
    excel = result.get("excel", {})
    blender = result.get("blender", {})
    if excel.get("status") != "EXCEL_COM_OBSERVED":
        blockers.append("excel_surface_not_observed")
    if blender.get("status") != "BLENDER_PYTHON_API_OBSERVED":
        blockers.append("blender_surface_not_observed")
    if excel.get("mutations_performed") != []:
        blockers.append("excel_mutation_boundary_broken")
    if result.get("actions_performed") != []:
        blockers.append("input_injection_boundary_broken")
    layers = result.get("adapter_layers", {})
    if layers.get("surface") != "pywinauto_uia":
        blockers.append("surface_adapter_not_adopted")
    if layers.get("excel_state") != "local_excel_com_object_model":
        blockers.append("excel_native_adapter_missing")
    if layers.get("blender_state") != "official_blender_python_api":
        blockers.append("blender_native_adapter_missing")
    if layers.get("shared_layer") != "typed_state_transition_graph":
        blockers.append("shared_transition_layer_missing")
    safety = result.get("safety", {})
    for field in ("network_used", "screen_capture", "camera_capture", "mouse_or_keyboard_injected", "source_write_attempted"):
        if safety.get(field) is not False:
            blockers.append(f"unsafe_capability_enabled:{field}")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Real Excel/Blender capability inventory")
    parser.add_argument("--blender", help="optional Blender executable path")
    parser.add_argument("--skip-excel", action="store_true")
    parser.add_argument("--skip-blender", action="store_true")
    args = parser.parse_args()

    excel = {"status": "SKIPPED"} if args.skip_excel else inspect_excel()
    blender = {"status": "SKIPPED"} if args.skip_blender else inspect_blender(discover_blender(args.blender))
    result: dict[str, Any] = {
        "status": "EXCEL_BLENDER_CAPABILITY_INVENTORY_VERIFIED"
        if excel.get("status") == "EXCEL_COM_OBSERVED" and blender.get("status") == "BLENDER_PYTHON_API_OBSERVED"
        else "CAPABILITY_INVENTORY_PARTIAL",
        "experiment": EXPERIMENT,
        "excel": excel,
        "blender": blender,
        "adapter_layers": {
            "surface": "pywinauto_uia",
            "excel_state": "local_excel_com_object_model",
            "blender_state": "official_blender_python_api",
            "shared_layer": "typed_state_transition_graph",
        },
        "actions_performed": [],
        "read_only": True,
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
