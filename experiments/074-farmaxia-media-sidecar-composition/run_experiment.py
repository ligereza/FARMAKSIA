"""Compose ffprobe-style metadata with a verified editorial sidecar."""

from __future__ import annotations

import json
import importlib.util
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1] / "research" / "tools"
BASE_FIXTURE = HERE.parent / "072-farmaxia-media-timeline-adapter" / "fixture.json"
BRIDGE_FIXTURE = HERE.parent / "073-farmaxia-media-representation-bridge" / "fixture.json"
BRIDGE_DIR = HERE.parent / "073-farmaxia-media-representation-bridge"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(BRIDGE_DIR))

from cloudevents_contract import compile_envelope, load_json  # noqa: E402


BRIDGE_MODULE_SPEC = importlib.util.spec_from_file_location(
    "farmaxia_073_media_representation_bridge",
    BRIDGE_DIR / "run_experiment.py",
)
if BRIDGE_MODULE_SPEC is None or BRIDGE_MODULE_SPEC.loader is None:
    raise ImportError("unable to load media representation bridge 073")
BRIDGE_MODULE = importlib.util.module_from_spec(BRIDGE_MODULE_SPEC)
BRIDGE_MODULE_SPEC.loader.exec_module(BRIDGE_MODULE)
normalize_ffprobe = BRIDGE_MODULE.normalize_ffprobe


FIXTURE = HERE / "fixture.json"


def load_fixture() -> dict[str, Any]:
    base = load_json(BASE_FIXTURE)
    bridge = load_json(BRIDGE_FIXTURE)
    overlay = load_json(FIXTURE)
    base.update(bridge)
    base.update(overlay)
    return base


def rational(value: Any) -> Fraction | None:
    if not isinstance(value, dict):
        return None
    if not isinstance(value.get("value"), int) or not isinstance(value.get("rate"), int):
        return None
    if value["rate"] <= 0:
        return None
    return Fraction(value["value"], value["rate"])


def token(value: Fraction | None) -> str | None:
    return None if value is None else f"{value.numerator}/{value.denominator}"


def record_by_ref(fixture: dict[str, Any], reference: str) -> dict[str, Any]:
    return next(
        (record for record in fixture.get("source_of_truth", {}).get("records", []) if record.get("entity_ref") == reference),
        {},
    )


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    source = fixture.get("source_of_truth", {})
    adapter = fixture.get("adapter", {})
    action = fixture.get("action", {})
    sidecar = fixture.get("sidecar", {})
    composition = fixture.get("composition", {})
    representations = fixture.get("representations", {})
    cloud_result = compile_envelope(fixture)
    blockers = list(cloud_result["blockers"])

    permutations = [
        fixture.get("events", []),
        list(reversed(fixture.get("events", []))),
        sorted(fixture.get("events", []), key=lambda event: (event.get("farmaxia-observed-at", -1), event.get("id", ""))),
    ]
    replay_orders = []
    for permutation in permutations:
        replay = compile_envelope({**fixture, "events": permutation})
        if replay["status"] != "CLOUDEVENTS_ENVELOPE_VERIFIED":
            blockers.append("replay_permutation_not_verified")
        replay_orders.append(replay["envelope"]["canonical_order"])
    replay_invariant = len({json.dumps(order, separators=(",", ":")) for order in replay_orders}) == 1
    if not replay_invariant:
        blockers.append("replay_order_changed_projection")

    actual_events = {event.get("id") for event in fixture.get("events", []) if event.get("id")}
    if not set(adapter.get("required_event_ids", [])).issubset(actual_events):
        blockers.append("required_input_event_missing")
    if adapter.get("source_surface") != "media-representation-composition":
        blockers.append("composition_source_surface_invalid")
    if adapter.get("destination_surface") != "farmaxia-media-contract":
        blockers.append("composition_destination_surface_invalid")
    if adapter.get("read_only") is not True or sidecar.get("read_only") is not True:
        blockers.append("composition_write_policy_missing")
    if action.get("dry_run") is not True:
        blockers.append("action_dry_run_policy_missing")

    ffprobe, ffprobe_blockers = normalize_ffprobe(representations.get("ffprobe", {}))
    if ffprobe_blockers:
        blockers.extend(f"ffprobe_invalid:{item}" for item in ffprobe_blockers)
    if ffprobe.get("status") != composition.get("expected_ffprobe_status"):
        blockers.append("ffprobe_status_unexpected")

    known_refs = set(source.get("entity_refs", []))
    asset_ref = sidecar.get("asset_ref")
    timeline_ref = sidecar.get("timeline_ref")
    marker_ref = sidecar.get("marker", {}).get("marker_ref")
    asset = record_by_ref(fixture, asset_ref or "")
    source_version = source.get("current_version")
    sidecar_errors = []
    if not urlparse(sidecar.get("source_uri", "")).netloc:
        sidecar_errors.append("sidecar_source_uri_invalid")
    if asset_ref not in known_refs or not asset:
        sidecar_errors.append("sidecar_asset_unknown")
    if timeline_ref not in known_refs or not record_by_ref(fixture, timeline_ref):
        sidecar_errors.append("sidecar_timeline_unknown")
    if marker_ref not in known_refs or not record_by_ref(fixture, marker_ref):
        sidecar_errors.append("sidecar_marker_unknown")
    if sidecar.get("source_version") != source_version:
        sidecar_errors.append("sidecar_version_stale")
    if sidecar.get("asset_sha256") != asset.get("sha256"):
        sidecar_errors.append("sidecar_asset_hash_mismatch")
    if sidecar.get("asset_ref") != ffprobe.get("asset_ref") or sidecar.get("asset_sha256") != ffprobe.get("asset_sha256"):
        sidecar_errors.append("sidecar_ffprobe_join_mismatch")
    if sidecar.get("timeline_id") != "cut-01":
        sidecar_errors.append("sidecar_timeline_id_invalid")
    if not isinstance(sidecar.get("source_refs"), list) or set(sidecar.get("source_refs", [])) != {asset_ref, timeline_ref, marker_ref}:
        sidecar_errors.append("sidecar_provenance_incomplete")

    fps = rational(sidecar.get("timebase"))
    video = sidecar.get("video", {})
    audio = sidecar.get("audio", {})
    video_start = rational(video.get("source_start"))
    video_duration = rational(video.get("duration"))
    video_timeline_start = rational(video.get("timeline_start"))
    audio_start = rational(audio.get("timeline_start"))
    audio_source_start = rational(audio.get("source_start"))
    audio_duration = rational(audio.get("duration"))
    if fps is None or fps <= 0:
        sidecar_errors.append("sidecar_timebase_invalid")
    available_range = asset.get("available_range", {})
    available_start = rational(available_range.get("start"))
    available_duration = rational(available_range.get("duration"))
    if None in (video_start, video_duration, video_timeline_start, audio_start, audio_source_start, audio_duration, available_start, available_duration):
        sidecar_errors.append("sidecar_range_incomplete")
    else:
        if (video_start, video_duration) != (audio_source_start, audio_duration):
            sidecar_errors.append("sidecar_audio_video_source_range_mismatch")
        if video_start < available_start or video_start + video_duration > available_start + available_duration:
            sidecar_errors.append("sidecar_source_range_out_of_bounds")
    source_frame = sidecar.get("marker", {}).get("source_frame")
    marker_record = record_by_ref(fixture, marker_ref or "")
    if source_frame != marker_record.get("source_frame") or not isinstance(source_frame, int):
        sidecar_errors.append("sidecar_marker_source_mismatch")
    if fps is None or video_start is None or video_timeline_start is None or not isinstance(source_frame, int):
        presentation_time = None
    else:
        presentation_time = video_timeline_start + Fraction(source_frame, 1) / fps - video_start
    if presentation_time is not None and video_duration is not None and video_timeline_start is not None:
        if presentation_time < video_timeline_start or presentation_time >= video_timeline_start + video_duration:
            sidecar_errors.append("sidecar_marker_outside_clip")
    sync_frames = None
    if fps is not None and audio_start is not None and video_timeline_start is not None:
        sync_frames = (audio_start - video_timeline_start) * fps
        if sync_frames != 0:
            sidecar_errors.append("sidecar_audio_video_sync_drift")
    if sidecar_errors:
        blockers.extend(sidecar_errors)

    frame_value = presentation_time * fps if presentation_time is not None and fps is not None else None
    presentation_frame = int(frame_value) if frame_value is not None and frame_value.denominator == 1 else None
    sidecar_status = "VERIFIED" if not sidecar_errors else "BLOCKED"
    composed_status = "COMPOSED_COMPATIBLE" if sidecar_status == "VERIFIED" and not blockers else "BLOCKED"
    if sidecar_status != composition.get("expected_sidecar_status"):
        blockers.append("sidecar_status_unexpected")
    if composed_status != composition.get("expected_composed_status"):
        blockers.append("composed_status_unexpected")
    if presentation_frame != composition.get("expected_marker_presentation_frame"):
        blockers.append("composed_marker_frame_unexpected")
    if token(presentation_time) != composition.get("expected_marker_presentation_time"):
        blockers.append("composed_marker_time_unexpected")
    if sync_frames is None or token(sync_frames) != str(composition.get("expected_audio_video_sync_offset_frames")) + "/1":
        blockers.append("composed_sync_unexpected")

    status = "MEDIA_SIDECAR_COMPOSITION_VERIFIED" if not blockers else "BLOCKED"
    return {
        "experiment": "074-farmaxia-media-sidecar-composition",
        "status": status,
        "blockers": sorted(set(blockers)),
        "input_envelope": {
            "status": cloud_result["status"],
            "raw_event_count": cloud_result["envelope"]["raw_event_count"],
            "unique_event_count": cloud_result["envelope"]["unique_event_count"],
            "duplicate_event_count": cloud_result["envelope"]["duplicate_event_count"],
            "canonical_order": cloud_result["envelope"]["canonical_order"],
            "original_envelopes_retained": cloud_result["envelope"]["original_envelopes_retained"],
        },
        "replay": {
            "permutation_count": len(permutations),
            "all_canonical_orders_equal": replay_invariant,
            "canonical_order": cloud_result["envelope"]["canonical_order"],
        },
        "ffprobe_before": ffprobe,
        "sidecar": {
            "status": sidecar_status,
            "sidecar_id": sidecar.get("sidecar_id"),
            "asset_ref": asset_ref,
            "asset_sha256": sidecar.get("asset_sha256"),
            "source_version": sidecar.get("source_version"),
            "timeline_id": sidecar.get("timeline_id"),
            "provenance_refs": sidecar.get("source_refs", []),
        },
        "composition": {
            "status": composed_status,
            "join_keys": {
                "asset_ref": sidecar.get("asset_ref") == ffprobe.get("asset_ref"),
                "asset_sha256": sidecar.get("asset_sha256") == ffprobe.get("asset_sha256"),
                "source_version": sidecar.get("source_version") == source_version,
            },
            "marker_presentation_frame": presentation_frame,
            "marker_presentation_time": token(presentation_time),
            "audio_video_sync_offset_frames": int(sync_frames) if sync_frames is not None and sync_frames.denominator == 1 else None,
            "full_contract_equivalent": composed_status == "COMPOSED_COMPATIBLE",
        },
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
        "scope_limit": "synthetic read-only ffprobe-style metadata plus editorial sidecar; no installed tools, media decode, live file or rights claim",
    }


def main() -> None:
    print(json.dumps(compile_fixture(load_fixture()), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
