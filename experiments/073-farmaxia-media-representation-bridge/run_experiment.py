"""Compare OTIO-style and ffprobe-style media representations read-only."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1] / "research" / "tools"
BASE_FIXTURE = HERE.parent / "072-farmaxia-media-timeline-adapter" / "fixture.json"
sys.path.insert(0, str(TOOLS))

from cloudevents_contract import compile_envelope, load_json  # noqa: E402


FIXTURE = HERE / "fixture.json"


def load_fixture() -> dict[str, Any]:
    base = load_json(BASE_FIXTURE)
    overlay = load_json(FIXTURE)
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


def otio_clip(rep: dict[str, Any], kind: str) -> dict[str, Any]:
    track = next((item for item in rep.get("tracks", []) if item.get("kind") == kind), {})
    children = track.get("children", [])
    return children[0] if children else {}


def normalize_otio(rep: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    blockers: list[str] = []
    video = otio_clip(rep, "Video")
    audio = otio_clip(rep, "Audio")
    video_ref = video.get("media_reference", {})
    audio_ref = audio.get("media_reference", {})
    video_meta = video_ref.get("metadata", {})
    audio_meta = audio_ref.get("metadata", {})
    video_range = video.get("source_range", {})
    video_start = rational(video_range.get("start_time"))
    video_duration = rational(video_range.get("duration"))
    video_timeline_start = rational(video.get("metadata", {}).get("timeline_start"))
    audio_timeline_start = rational(audio.get("metadata", {}).get("timeline_start"))
    available = video_ref.get("available_range", {})
    available_start = rational(available.get("start_time"))
    available_duration = rational(available.get("duration"))
    rate = video_range.get("start_time", {}).get("rate")
    fps = Fraction(rate, 1) if isinstance(rate, int) and rate > 0 else None
    if not rep.get("name") or rep.get("schema") != "Timeline.1":
        blockers.append("otio_timeline_identity_invalid")
    if not video or not audio:
        blockers.append("otio_audio_video_tracks_missing")
    if None in (video_start, video_duration, video_timeline_start, audio_timeline_start, available_start, available_duration, fps):
        blockers.append("otio_time_range_incomplete")
    elif video_start < available_start or video_start + video_duration > available_start + available_duration:
        blockers.append("otio_source_range_out_of_bounds")

    markers = rep.get("markers", [])
    marker = next(
        (
            item
            for item in markers
            if item.get("metadata", {}).get("farmaxia_marker_ref")
            == "media-catalog:farmaksia:marker:insight-01"
        ),
        {},
    )
    source_frame = marker.get("metadata", {}).get("farmaxia_source_frame")
    if not isinstance(source_frame, int):
        blockers.append("otio_marker_source_frame_missing")
    if fps is None or video_start is None or video_timeline_start is None or not isinstance(source_frame, int):
        presentation_time = None
    else:
        presentation_time = video_timeline_start + Fraction(source_frame, 1) / fps - video_start
    if presentation_time is not None and video_duration is not None and video_timeline_start is not None:
        if presentation_time < video_timeline_start or presentation_time >= video_timeline_start + video_duration:
            blockers.append("otio_marker_outside_clip")
    if fps is not None and audio_timeline_start is not None and video_timeline_start is not None:
        sync_frames = (audio_timeline_start - video_timeline_start) * fps
        if sync_frames != 0:
            blockers.append("otio_audio_video_sync_drift")
    else:
        sync_frames = None
    if video_meta.get("farmaxia_asset_ref") != audio_meta.get("farmaxia_asset_ref"):
        blockers.append("otio_track_asset_identity_mismatch")
    if video_meta.get("sha256") != "sha256:synthetic-interview-master-v4":
        blockers.append("otio_asset_hash_unknown")
    if video_meta.get("codec_name") != "h264":
        blockers.append("otio_codec_unknown")
    frame_value = presentation_time * fps if presentation_time is not None and fps is not None else None
    presentation_frame = int(frame_value) if frame_value is not None and frame_value.denominator == 1 else None
    result = {
        "status": "COMPATIBLE" if not blockers else "BLOCKED",
        "representation": "otio",
        "timeline_id": rep.get("name"),
        "asset_ref": video_meta.get("farmaxia_asset_ref"),
        "asset_sha256": video_meta.get("sha256"),
        "codec": video_meta.get("codec_name"),
        "timebase": token(fps),
        "source_range": {"start": token(video_start), "duration": token(video_duration)},
        "marker_source_frame": source_frame,
        "marker_presentation_frame": presentation_frame,
        "marker_presentation_time": token(presentation_time),
        "audio_video_sync_offset_frames": int(sync_frames) if sync_frames is not None and sync_frames.denominator == 1 else None,
        "provenance_refs": [
            rep.get("metadata", {}).get("farmaxia_timeline_ref"),
            video_meta.get("farmaxia_asset_ref"),
            marker.get("metadata", {}).get("farmaxia_marker_ref"),
        ],
        "blockers": sorted(set(blockers)),
    }
    return result, blockers


def parse_ffprobe_timebase(value: Any) -> Fraction | None:
    if not isinstance(value, str) or "/" not in value:
        return None
    numerator, denominator = value.split("/", 1)
    try:
        numerator_int = int(numerator)
        denominator_int = int(denominator)
    except ValueError:
        return None
    if numerator_int <= 0 or denominator_int <= 0:
        return None
    return Fraction(denominator_int, numerator_int)


def normalize_ffprobe(rep: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    blockers: list[str] = []
    fmt = rep.get("format", {})
    tags = fmt.get("tags", {})
    streams = rep.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), {})
    fps = parse_ffprobe_timebase(video.get("time_base"))
    if not video or not audio:
        blockers.append("ffprobe_required_stream_missing")
    if fps is None:
        blockers.append("ffprobe_timebase_missing")
    if not isinstance(video.get("duration_ts"), int) or not isinstance(audio.get("duration_ts"), int):
        blockers.append("ffprobe_duration_missing")
    if video.get("codec_name") != "h264":
        blockers.append("ffprobe_video_codec_unknown")
    if audio.get("start_pts") != video.get("start_pts"):
        blockers.append("ffprobe_audio_video_start_drift")
    missing_editorial = ["editorial_timeline", "clip_source_range", "marker_mapping"]
    if rep.get("claims_complete") is True:
        blockers.append("ffprobe_false_editorial_completeness")
    status = "PARTIAL_UNKNOWN" if not blockers else "BLOCKED"
    return {
        "status": status,
        "representation": "ffprobe",
        "asset_ref": tags.get("farmaxia_asset_ref"),
        "asset_sha256": tags.get("sha256"),
        "codec": video.get("codec_name"),
        "timebase": token(fps),
        "available_duration": token(Fraction(video["duration_ts"], 1) / fps) if fps is not None and isinstance(video.get("duration_ts"), int) else None,
        "missing_semantics": missing_editorial,
        "requires_sidecar": True,
        "provenance_refs": [tags.get("farmaxia_asset_ref")],
        "blockers": sorted(set(blockers)),
    }, blockers


def compile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    bridge = fixture.get("representations", {})
    adapter = fixture.get("adapter", {})
    comparison_policy = fixture.get("comparison", {})
    cloud_result = compile_envelope(fixture)
    blockers = list(cloud_result["blockers"])
    replay_permutations = [
        fixture.get("events", []),
        list(reversed(fixture.get("events", []))),
        sorted(fixture.get("events", []), key=lambda event: (event.get("farmaxia-observed-at", -1), event.get("id", ""))),
    ]
    replay_orders = []
    for permutation in replay_permutations:
        replay = compile_envelope({**fixture, "events": permutation})
        if replay["status"] != "CLOUDEVENTS_ENVELOPE_VERIFIED":
            blockers.append("replay_permutation_not_verified")
        replay_orders.append(replay["envelope"]["canonical_order"])
    replay_invariant = len({json.dumps(order, separators=(",", ":")) for order in replay_orders}) == 1
    if not replay_invariant:
        blockers.append("replay_order_changed_projection")
    if adapter.get("source_surface") != "media-representation":
        blockers.append("bridge_source_surface_invalid")
    if adapter.get("destination_surface") != "farmaxia-media-contract":
        blockers.append("bridge_destination_surface_invalid")
    if adapter.get("read_only") is not True:
        blockers.append("bridge_write_policy_missing")
    if set(adapter.get("required_representations", [])) != {"otio", "ffprobe"}:
        blockers.append("required_representation_missing")
    actual_event_ids = {event.get("id") for event in fixture.get("events", []) if event.get("id")}
    required_event_ids = set(adapter.get("required_event_ids", []))
    if not required_event_ids.issubset(actual_event_ids):
        blockers.append("required_input_event_missing")
    if not bridge.get("otio") or not bridge.get("ffprobe"):
        blockers.append("representation_input_missing")

    otio, otio_blockers = normalize_otio(bridge.get("otio", {}))
    ffprobe, ffprobe_blockers = normalize_ffprobe(bridge.get("ffprobe", {}))
    blockers.extend(otio_blockers)
    blockers.extend(ffprobe_blockers)
    expected_otio = comparison_policy.get("expected_otio_status")
    expected_ffprobe = comparison_policy.get("expected_ffprobe_status")
    if otio["status"] != expected_otio:
        blockers.append("otio_status_unexpected")
    if ffprobe["status"] != expected_ffprobe:
        blockers.append("ffprobe_status_unexpected")
    same_identity = otio.get("asset_ref") == ffprobe.get("asset_ref")
    same_hash = otio.get("asset_sha256") == ffprobe.get("asset_sha256")
    same_codec = otio.get("codec") == ffprobe.get("codec")
    same_timebase = otio.get("timebase") == ffprobe.get("timebase")
    full_contract_equivalent = otio["status"] == "COMPATIBLE" and ffprobe["status"] == "COMPATIBLE"
    if full_contract_equivalent != comparison_policy.get("expected_full_contract_equivalent"):
        blockers.append("full_contract_equivalence_claim_invalid")
    if not all((same_identity, same_hash, same_codec, same_timebase)):
        blockers.append("shared_asset_metadata_disagrees")
    if not ffprobe.get("requires_sidecar") or not ffprobe.get("missing_semantics"):
        blockers.append("ffprobe_safe_abstention_missing")
    if not all(ref for ref in otio.get("provenance_refs", []) + ffprobe.get("provenance_refs", [])):
        blockers.append("representation_provenance_missing")

    status = "MEDIA_REPRESENTATION_BRIDGE_VERIFIED" if not blockers else "BLOCKED"
    return {
        "experiment": "073-farmaxia-media-representation-bridge",
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
        "representations": {"otio": otio, "ffprobe": ffprobe},
        "comparison": {
            "same_asset_identity": same_identity,
            "same_asset_hash": same_hash,
            "same_codec": same_codec,
            "same_timebase": same_timebase,
            "full_contract_equivalent": full_contract_equivalent,
            "ffprobe_sidecar_required": ffprobe.get("requires_sidecar"),
            "safe_abstention": ffprobe["status"] == "PARTIAL_UNKNOWN",
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
        "scope_limit": "synthetic read-only OTIO-style and ffprobe-style representations; no installed tools, media decode, live files or rights claim",
    }


def main() -> None:
    print(json.dumps(compile_fixture(load_fixture()), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
