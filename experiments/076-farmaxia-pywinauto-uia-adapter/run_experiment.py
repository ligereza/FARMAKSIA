"""Use pywinauto UIA to inspect real Windows windows without acting on them."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
from typing import Any


def safe_is_visible(window: Any) -> bool:
    try:
        return bool(window.is_visible())
    except Exception:
        return False


def safe_control_type(window: Any) -> str:
    try:
        return str(window.element_info.control_type or "unknown")
    except Exception:
        return "unknown"


def collect_observation(title_regex: str | None = None, inspect_controls: bool = False) -> dict[str, Any]:
    try:
        from pywinauto import Desktop
    except ImportError as exc:
        return {
            "status": "TOOL_UNAVAILABLE",
            "blockers": [f"pywinauto_import_failed:{type(exc).__name__}"],
            "tool_available": False,
        }

    try:
        windows = Desktop(backend="uia").windows()
    except Exception as exc:
        return {
            "status": "UIA_ENVIRONMENT_UNKNOWN",
            "blockers": [f"uia_enumeration_failed:{type(exc).__name__}"],
            "tool_available": True,
        }

    pattern = re.compile(title_regex, re.IGNORECASE) if title_regex else None
    visible_count = 0
    named_count = 0
    matched_count = 0
    matched_control_types: Counter[str] = Counter()
    descendant_control_types: Counter[str] = Counter()
    descendant_count = 0
    inaccessible_count = 0
    for window in windows:
        visible = safe_is_visible(window)
        visible_count += int(visible)
        try:
            title = window.window_text()
            named_count += int(bool(title))
            matched = pattern.search(title or "") if pattern else True
        except Exception:
            inaccessible_count += 1
            matched = False
        if matched:
            matched_count += 1
            matched_control_types[safe_control_type(window)] += 1
            if inspect_controls:
                try:
                    descendants = window.descendants()
                    descendant_count += len(descendants)
                    for control in descendants:
                        descendant_control_types[safe_control_type(control)] += 1
                except Exception:
                    inaccessible_count += 1

    blockers: list[str] = []
    if not windows:
        blockers.append("no_uia_windows_visible_to_probe")
    status = "PYWINAUTO_UIA_PROBE_VERIFIED" if not blockers else "UIA_ENVIRONMENT_UNKNOWN"
    return {
        "status": status,
        "blockers": blockers,
        "tool_available": True,
        "tool_version": "0.6.9",
        "backend": "uia",
        "observation": {
            "top_level_window_count": len(windows),
            "visible_window_count": visible_count,
            "named_window_count": named_count,
            "matched_window_count": matched_count,
            "matched_control_type_counts": dict(sorted(matched_control_types.items())),
            "descendant_control_count": descendant_count,
            "descendant_control_type_counts": dict(sorted(descendant_control_types.items())),
            "inaccessible_window_count": inaccessible_count,
        },
        "inspect_controls": inspect_controls,
        "title_texts_emitted": False,
        "actions_performed": [],
        "read_only": True,
        "safety": {
            "screen_capture": False,
            "camera_capture": False,
            "network_used": False,
            "mouse_or_keyboard_injected": False,
            "source_write_attempted": False,
        },
    }


def validate_observation(observation: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if observation.get("status") not in {"PYWINAUTO_UIA_PROBE_VERIFIED", "UIA_ENVIRONMENT_UNKNOWN"}:
        blockers.append("probe_status_invalid")
    if observation.get("tool_available") is not True:
        blockers.append("tool_unavailable")
    if observation.get("backend") != "uia":
        blockers.append("uia_backend_missing")
    metrics = observation.get("observation", {})
    if not isinstance(metrics.get("top_level_window_count"), int) or metrics.get("top_level_window_count", 0) < 0:
        blockers.append("window_count_invalid")
    if observation.get("title_texts_emitted") is not False:
        blockers.append("raw_title_emission_forbidden")
    if observation.get("actions_performed") != []:
        blockers.append("read_only_action_boundary_broken")
    if observation.get("read_only") is not True:
        blockers.append("read_only_policy_missing")
    safety = observation.get("safety", {})
    for field in ("screen_capture", "camera_capture", "network_used", "mouse_or_keyboard_injected", "source_write_attempted"):
        if safety.get(field) is not False:
            blockers.append(f"unsafe_capability_enabled:{field}")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only pywinauto UIA probe")
    parser.add_argument("--title-regex", help="optional local filter; matching title text is never emitted")
    parser.add_argument("--inspect-controls", action="store_true", help="read control tree metadata without emitting text or acting")
    args = parser.parse_args()
    result = collect_observation(args.title_regex, args.inspect_controls)
    result["experiment"] = "076-farmaxia-pywinauto-uia-adapter"
    result["validation_blockers"] = validate_observation(result)
    if result["validation_blockers"]:
        result["status"] = "BLOCKED"
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
