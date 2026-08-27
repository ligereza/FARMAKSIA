"""Audit incompatible but individually valid editorial sidecars."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SIDECAR_DIR = HERE.parent / "074-farmaxia-media-sidecar-composition"
TOOLS = HERE.parents[1] / "research" / "tools"
sys.path.insert(0, str(TOOLS))

from cloudevents_contract import load_json  # noqa: E402


SIDECAR_MODULE_SPEC = importlib.util.spec_from_file_location(
    "farmaxia_074_media_sidecar_composition",
    SIDECAR_DIR / "run_experiment.py",
)
if SIDECAR_MODULE_SPEC is None or SIDECAR_MODULE_SPEC.loader is None:
    raise ImportError("unable to load media sidecar composition 074")
SIDECAR_MODULE = importlib.util.module_from_spec(SIDECAR_MODULE_SPEC)
SIDECAR_MODULE_SPEC.loader.exec_module(SIDECAR_MODULE)

FIXTURE = HERE / "fixture.json"


def load_fixture() -> dict[str, Any]:
    base = SIDECAR_MODULE.load_fixture()
    overlay = load_json(FIXTURE)
    source = base.setdefault("source_of_truth", {})
    source.setdefault("entity_refs", [])
    source.setdefault("records", [])
    for record in overlay.get("additional_records", []):
        source["entity_refs"].append(record["entity_ref"])
        source["records"].append(record)
    base["sidecars"] = overlay.get("sidecars", [])
    base["conflict_contract"] = overlay.get("conflict_contract", {})
    return base


def rational(value: Any) -> Fraction | None:
    if not isinstance(value, dict):
        return None
    if not isinstance(value.get("value"), int) or not isinstance(value.get("rate"), int):
        return None
    if value["rate"] <= 0:
        return None
    return Fraction(value["value"], value["rate"])


def expected_composition(sidecar: dict[str, Any]) -> dict[str, Any]:
    fps = rational(sidecar.get("timebase"))
    video = sidecar.get("video", {})
    source_start = rational(video.get("source_start"))
    timeline_start = rational(video.get("timeline_start"))
    source_frame = sidecar.get("marker", {}).get("source_frame")
    if fps is None or source_start is None or timeline_start is None or not isinstance(source_frame, int):
        frame = None
        when = None
    else:
        when_fraction = timeline_start + Fraction(source_frame, 1) / fps - source_start
        frame_fraction = when_fraction * fps
        frame = int(frame_fraction) if frame_fraction.denominator == 1 else None
        when = f"{when_fraction.numerator}/{when_fraction.denominator}"
    return {
        "expected_ffprobe_status": "PARTIAL_UNKNOWN",
        "expected_sidecar_status": "VERIFIED",
        "expected_composed_status": "COMPOSED_COMPATIBLE",
        "expected_marker_presentation_frame": frame,
        "expected_marker_presentation_time": when,
        "expected_audio_video_sync_offset_frames": 0,
    }


def candidate_scope(sidecar: dict[str, Any]) -> dict[str, Any]:
    return {
        "asset_ref": sidecar.get("asset_ref"),
        "asset_sha256": sidecar.get("asset_sha256"),
        "source_version": sidecar.get("source_version"),
        "timeline_ref": sidecar.get("timeline_ref"),
        "timeline_id": sidecar.get("timeline_id"),
    }


def semantic_claims(sidecar: dict[str, Any]) -> dict[str, Any]:
    return {
        "timeline_id": sidecar.get("timeline_id"),
        "timebase": sidecar.get("timebase"),
        "video": sidecar.get("video"),
        "audio": sidecar.get("audio"),
        "marker": sidecar.get("marker"),
    }


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else key
            result.update(flatten(child, child_prefix))
        return result
    return {prefix: value}


def differing_claims(first: dict[str, Any], second: dict[str, Any]) -> list[str]:
    left = flatten(semantic_claims(first))
    right = flatten(semantic_claims(second))
    return sorted(key for key in set(left) | set(right) if left.get(key) != right.get(key))


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    sidecars = fixture.get("sidecars", [])
    contract = fixture.get("conflict_contract", {})
    adapter = fixture.get("adapter", {})
    action = fixture.get("action", {})
    blockers: list[str] = []
    if not isinstance(sidecars, list) or len(sidecars) != 2:
        blockers.append("sidecar_candidate_count_invalid")
        sidecars = sidecars if isinstance(sidecars, list) else []
    sidecar_ids = [item.get("sidecar_id") for item in sidecars if isinstance(item, dict)]
    if len(sidecar_ids) != len(set(sidecar_ids)):
        blockers.append("sidecar_id_duplicate")
    if adapter.get("read_only") is not True:
        blockers.append("conflict_adapter_write_policy_missing")
    if action.get("dry_run") is not True:
        blockers.append("conflict_action_dry_run_policy_missing")
    if fixture.get("preferred_sidecar_id") is not None:
        blockers.append("silent_sidecar_selection_forbidden")

    candidate_results: list[dict[str, Any]] = []
    for sidecar in sidecars:
        candidate_fixture = copy.deepcopy(fixture)
        candidate_fixture["sidecar"] = copy.deepcopy(sidecar)
        candidate_fixture["composition"] = expected_composition(sidecar)
        candidate_result = SIDECAR_MODULE.compile_fixture(candidate_fixture)
        candidate_results.append(candidate_result)
        if candidate_result["status"] != "MEDIA_SIDECAR_COMPOSITION_VERIFIED":
            blockers.append(f"candidate_invalid:{sidecar.get('sidecar_id')}")

    all_valid = bool(candidate_results) and not blockers and all(
        item["status"] == "MEDIA_SIDECAR_COMPOSITION_VERIFIED" for item in candidate_results
    )
    scopes = [candidate_scope(sidecar) for sidecar in sidecars]
    same_scope = len(scopes) == 2 and scopes[0] == scopes[1]
    if len(scopes) == 2 and not same_scope:
        blockers.append("conflict_scope_mismatch")

    conflict = None
    if all_valid and same_scope:
        claims = [semantic_claims(sidecar) for sidecar in sidecars]
        if claims[0] != claims[1]:
            conflict = {
                "scope": scopes[0],
                "candidate_ids": sidecar_ids,
                "differing_claims": differing_claims(sidecars[0], sidecars[1]),
            }
        else:
            blockers.append("expected_conflict_not_observed")

    expected_status = contract.get("expected_status")
    status = "CONFLICT" if conflict is not None and not blockers else "BLOCKED"
    if status != expected_status:
        blockers.append("conflict_status_unexpected")
        status = "BLOCKED"

    first_result = candidate_results[0] if candidate_results else {}
    expected_ids = contract.get("expected_preserved_sidecar_ids", [])
    preserved_ids = sidecar_ids if status == "CONFLICT" else []
    if preserved_ids != expected_ids:
        blockers.append("preserved_sidecar_history_unexpected")
    if conflict is not None and conflict["differing_claims"] != contract.get("expected_differing_claims"):
        blockers.append("conflict_claims_unexpected")

    if blockers:
        status = "BLOCKED"
    return {
        "experiment": "075-farmaxia-media-sidecar-conflict-audit",
        "status": status,
        "blockers": sorted(set(blockers)),
        "candidate_count": len(sidecars),
        "candidates": [
            {
                "sidecar_id": item.get("sidecar_id"),
                "status": result.get("sidecar", {}).get("status"),
                "composition_status": result.get("composition", {}).get("status"),
                "marker_presentation_frame": result.get("composition", {}).get("marker_presentation_frame"),
                "marker_presentation_time": result.get("composition", {}).get("marker_presentation_time"),
                "scope": candidate_scope(item),
            }
            for item, result in zip(sidecars, candidate_results)
        ],
        "conflict": conflict,
        "selection": None,
        "preserved_sidecar_ids": preserved_ids,
        "input_envelope": first_result.get("input_envelope"),
        "replay": first_result.get("replay"),
        "adapter": {
            "source": adapter.get("source_surface"),
            "destination": adapter.get("destination_surface"),
            "same_shared_cloudevents_kernel": True,
            "read_only": adapter.get("read_only"),
        },
        "safety": {
            "network_used": False,
            "external_execution": False,
            "human_data": False,
            "media_decoded": False,
            "source_write_attempted": False,
        },
        "scope_limit": "synthetic read-only conflict audit for two editorial sidecars; no live authority, signature, media decode or selection",
    }


def main() -> None:
    print(json.dumps(compile_fixture(load_fixture()), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
