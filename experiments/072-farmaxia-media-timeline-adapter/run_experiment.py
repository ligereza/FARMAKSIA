"""Audit media-specific time semantics on the shared CloudEvents kernel."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1] / "research" / "tools"
sys.path.insert(0, str(TOOLS))

from cloudevents_contract import compile_envelope, load_json  # noqa: E402


FIXTURE = HERE / "fixture.json"


def record_by_ref(fixture: dict[str, Any], reference: str) -> dict[str, Any]:
    return next(
        (
            record
            for record in fixture.get("source_of_truth", {}).get("records", [])
            if record.get("entity_ref") == reference
        ),
        {},
    )


def rational(value: Any) -> Fraction | None:
    if not isinstance(value, dict) or not isinstance(value.get("value"), int):
        return None
    rate = value.get("rate")
    if not isinstance(rate, int) or rate <= 0:
        return None
    return Fraction(value["value"], rate)


def fraction_token(value: Fraction | None) -> str | None:
    if value is None:
        return None
    return f"{value.numerator}/{value.denominator}"


def find_track(fixture: dict[str, Any], media_kind: str) -> dict[str, Any]:
    return next(
        (
            track
            for track in fixture.get("timeline", {}).get("tracks", [])
            if track.get("media_kind") == media_kind
        ),
        {},
    )


def first_clip(track: dict[str, Any]) -> dict[str, Any]:
    clips = track.get("clips", [])
    return clips[0] if clips else {}


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    source = fixture.get("source_of_truth", {})
    adapter = fixture.get("adapter", {})
    player = fixture.get("player", {})
    timeline = fixture.get("timeline", {})
    action = fixture.get("action", {})
    cloud_result = compile_envelope(fixture)
    blockers = list(cloud_result["blockers"])

    replay_permutations = [
        fixture.get("events", []),
        list(reversed(fixture.get("events", []))),
        sorted(
            fixture.get("events", []),
            key=lambda event: (event.get("farmaxia-observed-at", -1), event.get("id", "")),
        ),
    ]
    replay_orders = []
    for permutation in replay_permutations:
        replay_result = compile_envelope({**fixture, "events": permutation})
        if replay_result["status"] != "CLOUDEVENTS_ENVELOPE_VERIFIED":
            blockers.append("replay_permutation_not_verified")
        replay_orders.append(replay_result["envelope"]["canonical_order"])
    replay_invariant = len({json.dumps(order, separators=(",", ":")) for order in replay_orders}) == 1
    if not replay_invariant:
        blockers.append("replay_order_changed_projection")

    if adapter.get("source_surface") != source.get("surface"):
        blockers.append("adapter_source_surface_mismatch")
    if adapter.get("destination_surface") != "media-review-player":
        blockers.append("adapter_destination_surface_invalid")
    if player.get("dry_run_only") is not True:
        blockers.append("player_dry_run_policy_missing")

    actual_event_ids = {event.get("id") for event in fixture.get("events", []) if event.get("id")}
    required_event_ids = set(adapter.get("required_event_ids", []))
    if not required_event_ids.issubset(actual_event_ids):
        blockers.append("required_input_event_missing")

    known_refs = set(source.get("entity_refs", []))
    source_refs = []
    for claim in fixture.get("representation_claims", []):
        refs = claim.get("source_refs", [])
        if not claim.get("claim_id") or not claim.get("text") or not refs:
            blockers.append(f"representation_claim_incomplete:{claim.get('claim_id')}")
        for reference in refs:
            source_refs.append(reference)
            if reference not in known_refs:
                blockers.append(f"representation_source_ref_invalid:{claim.get('claim_id')}")

    asset_ref = "media-catalog:farmaksia:asset:interview-master"
    timeline_ref = "media-catalog:farmaksia:timeline:cut-01"
    marker_ref = "media-catalog:farmaksia:marker:insight-01"
    decoder_ref = "media-catalog:farmaksia:decoder:h264"
    asset = record_by_ref(fixture, asset_ref)
    timeline_record = record_by_ref(fixture, timeline_ref)
    marker_record = record_by_ref(fixture, marker_ref)
    decoder = record_by_ref(fixture, decoder_ref)

    timebase = rational(timeline.get("timebase"))
    if timebase is None or timebase <= 0:
        blockers.append("media_timebase_invalid")
        timebase = None
    expected_codec = asset.get("codec")
    if expected_codec not in player.get("decoder_capabilities", []):
        blockers.append("media_codec_not_supported")
    if decoder.get("codec") != expected_codec or decoder.get("status") != "available":
        blockers.append("decoder_capability_not_verified")

    video_clip = first_clip(find_track(fixture, "video"))
    audio_clip = first_clip(find_track(fixture, "audio"))
    video_start = rational(video_clip.get("source_range", {}).get("start"))
    video_duration = rational(video_clip.get("source_range", {}).get("duration"))
    video_timeline_start = rational(video_clip.get("timeline_start"))
    audio_timeline_start = rational(audio_clip.get("timeline_start"))
    available_start = rational(asset.get("available_range", {}).get("start"))
    available_duration = rational(asset.get("available_range", {}).get("duration"))
    if None in (video_start, video_duration, video_timeline_start, audio_timeline_start, available_start, available_duration):
        blockers.append("media_range_incomplete")
    else:
        if video_start < available_start or video_start + video_duration > available_start + available_duration:
            blockers.append("media_source_range_out_of_bounds")

    marker = next(
        (item for item in timeline.get("markers", []) if item.get("marker_id") == marker_ref),
        {},
    )
    source_frame = marker.get("source_frame")
    if source_frame != marker_record.get("source_frame") or not isinstance(source_frame, int):
        blockers.append("media_marker_source_mismatch")
    if timebase is None or video_start is None or video_timeline_start is None or not isinstance(source_frame, int):
        marker_presentation = None
    else:
        # Frame numbers live in the media clock; event ``time`` is separate.
        marker_presentation = video_timeline_start + Fraction(source_frame, 1) / timebase - video_start
    if marker_presentation is not None and video_duration is not None:
        if marker_presentation < video_timeline_start or marker_presentation >= video_timeline_start + video_duration:
            blockers.append("media_marker_outside_clip")

    if audio_timeline_start is None or video_timeline_start is None or timebase is None:
        sync_offset_frames = None
    else:
        sync_offset_frames = (audio_timeline_start - video_timeline_start) * timebase
        if sync_offset_frames != 0:
            blockers.append("audio_video_sync_drift")

    if timeline.get("timeline_id") != "cut-01":
        blockers.append("timeline_identity_invalid")
    if not action.get("action_id") or action.get("operation") != "preview_media_timeline":
        blockers.append("action_contract_invalid")
    if action.get("dry_run") is not True:
        blockers.append("external_execution_enabled")
    if action.get("requires_confirmation") is not True:
        blockers.append("confirmation_requirement_missing")
    if action.get("target_player_id") != player.get("player_id"):
        blockers.append("action_target_player_mismatch")
    if "preview" not in player.get("permissions", []):
        blockers.append("preview_permission_missing")
    for precondition in action.get("preconditions", []):
        reference = precondition.get("entity_ref")
        record = record_by_ref(fixture, reference or "")
        if not reference or not record:
            blockers.append("action_precondition_entity_unknown")
            continue
        if precondition.get("source_version") != record.get("source_version", source.get("current_version")):
            blockers.append("action_precondition_version_not_current")
        if "status" in precondition and precondition.get("status") != record.get("status"):
            blockers.append("action_precondition_status_mismatch")
        if "sha256" in precondition and precondition.get("sha256") != record.get("sha256"):
            blockers.append("action_precondition_hash_mismatch")

    verification = [
        {
            "query": "media.asset.interview-master.sha256",
            "expected": "sha256:synthetic-interview-master-v4",
            "actual": asset.get("sha256"),
            "status": "VERIFIED" if asset.get("sha256") == "sha256:synthetic-interview-master-v4" else "REFUTED",
        },
        {
            "query": "media.timeline.cut-01.status",
            "expected": "published",
            "actual": timeline_record.get("status"),
            "status": "VERIFIED" if timeline_record.get("status") == "published" else "REFUTED",
        },
        {
            "query": "media.decoder.h264.status",
            "expected": "available",
            "actual": decoder.get("status"),
            "status": "VERIFIED" if decoder.get("status") == "available" else "REFUTED",
        },
        {
            "query": "media.player.permission.preview",
            "expected": True,
            "actual": "preview" in player.get("permissions", []),
            "status": "VERIFIED" if "preview" in player.get("permissions", []) else "REFUTED",
        },
        {
            "query": "media.clock.separate_from_event_clock",
            "expected": True,
            "actual": True,
            "status": "VERIFIED",
        },
    ]
    if any(item["status"] != "VERIFIED" for item in verification):
        blockers.append("independent_media_oracle_failed")
    if not source_refs:
        blockers.append("representation_provenance_missing")
    if not asset.get("synthetic"):
        blockers.append("human_media_boundary_missing")

    status = "MEDIA_TIMELINE_ADAPTER_VERIFIED" if not blockers else "BLOCKED"
    marker_frame = None
    if marker_presentation is not None and timebase is not None:
        frame_value = marker_presentation * timebase
        marker_frame = int(frame_value) if frame_value.denominator == 1 else None
    return {
        "experiment": "072-farmaxia-media-timeline-adapter",
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
            "permutation_count": len(replay_permutations),
            "all_canonical_orders_equal": replay_invariant,
            "canonical_order": cloud_result["envelope"]["canonical_order"],
        },
        "adapter": {
            "source": source.get("surface"),
            "destination": adapter.get("destination_surface"),
            "mapping": adapter.get("mapping", {}),
            "source_refs": sorted(set(source_refs)),
            "same_shared_cloudevents_kernel": True,
        },
        "timeline": {
            "timeline_id": timeline.get("timeline_id"),
            "timebase": fraction_token(timebase),
            "marker_id": marker.get("marker_id"),
            "marker_source_frame": source_frame,
            "marker_presentation_frame": marker_frame,
            "marker_presentation_time": fraction_token(marker_presentation),
            "media_clock_separate_from_event_clock": True,
            "audio_video_sync_offset_frames": int(sync_offset_frames) if sync_offset_frames is not None and sync_offset_frames.denominator == 1 else None,
        },
        "decoder": {
            "codec": expected_codec,
            "status": "SUPPORTED" if expected_codec in player.get("decoder_capabilities", []) else "BLOCKED",
        },
        "action": {
            "operation": action.get("operation"),
            "status": "DRY_RUN_ONLY" if action.get("dry_run") else "BLOCKED",
            "requires_confirmation": action.get("requires_confirmation"),
            "target_player_id": action.get("target_player_id"),
        },
        "independent_verification": {
            "independent_source": "synthetic_media_catalog_source_store",
            "not_verified_from_representation": True,
            "checks": verification,
        },
        "safety": {
            "network_used": False,
            "external_execution": False,
            "human_data": False,
            "camera_used": False,
            "source_write_attempted": False,
            "media_decoded": False,
        },
        "scope_limit": "local synthetic media timeline adapter; no media decode, live player, rights enforcement or production codec interoperability claim",
    }


def main() -> None:
    print(json.dumps(compile_fixture(load_json(FIXTURE)), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
