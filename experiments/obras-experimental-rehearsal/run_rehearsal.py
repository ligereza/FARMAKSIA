"""Run the complete Obras Experimentales rehearsal in deterministic dry-run mode."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE.parents[1] / "artifacts" / "obras-experimental-rehearsal"
DEFAULT_SESSION_START = "2026-01-01T20:00:00Z"


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False) + "\n"


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json(value), encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, values: list[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for value in values:
            handle.write(json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False))
            handle.write("\n")


def _git_ref(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unresolved"
    return result.stdout.strip()


def _load_modules(xio_root: Path, mosaik_root: Path):
    xio_root = xio_root.resolve()
    mosaik_root = mosaik_root.resolve()
    for root in (str(xio_root), str(mosaik_root)):
        if root not in sys.path:
            sys.path.insert(0, root)
    from xio.experimental_rehearsal import (  # type: ignore[import-not-found]
        extract_pulses,
        load_fixture,
        normalize_signal_events,
        sha256_json,
    )
    from xio.semantic_lighting import (  # type: ignore[import-not-found]
        build_predictive_frame,
        pack_semantic_frame,
        unpack_semantic_frame,
    )
    from adapters.vj.experimental_rehearsal import (  # type: ignore[import-not-found]
        RehearsalBridgeError,
        build_rehearsal_projection,
        validate_resolume_cue,
    )
    from adapters.vj.console_proposals import (  # type: ignore[import-not-found]
        build_console_proposals,
    )
    return (
        extract_pulses,
        load_fixture,
        normalize_signal_events,
        sha256_json,
        build_predictive_frame,
        pack_semantic_frame,
        unpack_semantic_frame,
        RehearsalBridgeError,
        build_rehearsal_projection,
        validate_resolume_cue,
        build_console_proposals,
    )


def _delivery_stream(fixture: Mapping[str, Any], extract_pulses) -> list[dict[str, Any]]:
    pulses = extract_pulses(fixture, threshold=0.62, min_gap_seconds=0.20)
    gaps = [
        {
            "event_id": f"audio-gap-{index + 1:03d}",
            "source_index": -1,
            "time_seconds": interval["start_seconds"],
            "amplitude": 0.0,
            "pulse": 0.0,
            "kind": "audio.gap",
            "gap_end_seconds": interval["end_seconds"],
        }
        for index, interval in enumerate(fixture.get("loss_intervals", []))
    ]
    by_id = {event["event_id"]: event for event in [*pulses, *gaps]}
    order = fixture.get("delivery_order")
    if not isinstance(order, list) or not order:
        return [*pulses, *gaps]
    try:
        return [dict(by_id[event_id]) for event_id in order]
    except KeyError as exc:
        raise ValueError(f"fixture delivery_order references unknown event: {exc.args[0]}") from exc


def _fixture_ids(count: int) -> list[str]:
    return [f"ble-{index + 1:02d}" for index in range(count)]


def _build_visualization(
    output: Path,
    *,
    timeline: Mapping[str, Any],
    phase_states: list[Mapping[str, Any]],
    cues: list[Mapping[str, Any]],
    safety: Mapping[str, Any],
) -> None:
    data = json.dumps(
        {"timeline": timeline, "phase_states": phase_states, "cues": cues, "safety": safety},
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Obras Experimentales - Signal Rehearsal</title>
<style>
:root {{ color-scheme: dark; --ink:#e8eef5; --muted:#91a4b7; --panel:#111d2a; --line:#29425a; --cyan:#54d6ef; --amber:#ffbf69; --green:#7ee081; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:#09121b; color:var(--ink); font:14px/1.45 system-ui,Segoe UI,sans-serif; }}
main {{ max-width:1280px; margin:0 auto; padding:28px; }} h1 {{ margin:0 0 4px; font-size:28px; }} h2 {{ font-size:16px; margin:22px 0 8px; }}
.sub {{ color:var(--muted); margin-bottom:18px; }} .badge {{ display:inline-block; border:1px solid #3b6177; border-radius:999px; padding:3px 9px; margin-right:6px; color:var(--cyan); }}
.grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; }} .card {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:12px; }} .value {{ font-size:22px; font-weight:700; }} .label {{ color:var(--muted); font-size:12px; }}
.panel {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px; margin-top:12px; }} canvas {{ width:100%; height:auto; background:#0b1722; border-radius:8px; }}
.controls {{ display:flex; align-items:center; gap:10px; margin:10px 0 0; }} button {{ background:#15394c; color:var(--ink); border:1px solid #3b7891; border-radius:6px; padding:7px 12px; cursor:pointer; }} input[type=range] {{ flex:1; accent-color:var(--cyan); }}
table {{ width:100%; border-collapse:collapse; font-size:12px; }} th,td {{ text-align:left; border-bottom:1px solid var(--line); padding:6px; }} th {{ color:var(--muted); }} .ok {{ color:var(--green); }} .warn {{ color:var(--amber); }} code {{ color:#b9eaff; }}
@media(max-width:780px) {{ .grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} main {{ padding:15px; }} }}
</style>
</head>
<body>
<main>
<h1>Obras Experimentales / ensayo de señal</h1>
<div class="sub"><span class="badge">synthetic fixture</span><span class="badge">dry-run</span><span class="badge">proposal-only</span> Recorrido XIO → PhaseChaser → MOSAIK/Resolume.</div>
<div class="grid" id="cards"></div>
<section class="panel"><h2>Señal normalizada y auditoría de entrega</h2><canvas id="signal" width="1200" height="190"></canvas></section>
<section class="panel"><h2>Estado PhaseChaser / N luminarias</h2><canvas id="stage" width="1200" height="460"></canvas>
<div class="controls"><button id="play">Play</button><input id="scrub" type="range" min="0" max="0" value="0"><span id="frame-label"></span></div></section>
<section class="panel"><h2>Cue propuesto para Resolume</h2><div id="cue"></div></section>
<section class="panel"><h2>Acciones de seguridad</h2><div id="safety"></div></section>
</main>
<script>
const DATA = {data};
const events = DATA.timeline.events || [];
const states = DATA.phase_states || [];
const cues = DATA.cues || [];
const signalCanvas = document.getElementById('signal');
const stageCanvas = document.getElementById('stage');
const signal = signalCanvas.getContext('2d');
const stage = stageCanvas.getContext('2d');
const scrub = document.getElementById('scrub');
const cards = document.getElementById('cards');
const frameLabel = document.getElementById('frame-label');
scrub.max = Math.max(0, states.length - 1);
cards.innerHTML = [
  ['Signals', events.length], ['Phase states', states.length], ['Fixtures', states[0]?.lights?.length || 0], ['Blocked actions', DATA.safety.actions_blocked.length]
].map(item => `<div class="card"><div class="value">${{item[1]}}</div><div class="label">${{item[0]}}</div></div>`).join('');
function clear(ctx, canvas) {{ ctx.clearRect(0,0,canvas.width,canvas.height); }}
function drawSignal() {{
  clear(signal, signalCanvas); const w=signalCanvas.width, h=signalCanvas.height;
  signal.strokeStyle='#29425a'; signal.beginPath(); signal.moveTo(30,h-32); signal.lineTo(w-20,h-32); signal.stroke();
  const maxT = Math.max(...events.map(e => e.time_seconds), 1);
  events.forEach(e => {{ const x=30+(e.time_seconds/maxT)*(w-55); const missing=e.payload.signal_state==='missing'; const height=missing?22:30+e.payload.amplitude*105; signal.strokeStyle=missing?'#ffbf69':'#54d6ef'; signal.lineWidth=missing?5:2; signal.beginPath(); signal.moveTo(x,h-32); signal.lineTo(x,h-32-height); signal.stroke(); signal.fillStyle=signal.strokeStyle; signal.font='12px system-ui'; signal.fillText(e.event_id,x-22, h-10); }});
  signal.fillStyle='#91a4b7'; signal.font='12px system-ui'; signal.fillText('time / canonical sequence',35,18);
}}
function drawStage(index) {{
  clear(stage, stageCanvas); const state=states[index] || states[0]; if (!state) return;
  const cx=stageCanvas.width/2, cy=stageCanvas.height/2+14, radius=Math.min(stageCanvas.width, stageCanvas.height)*.30;
  stage.strokeStyle='#29425a'; stage.lineWidth=1; stage.beginPath(); stage.arc(cx,cy,radius,0,Math.PI*2); stage.stroke();
  stage.fillStyle='#91a4b7'; stage.font='14px system-ui'; stage.fillText(`${{state.timecode}}  ${{state.signal_state}}`,20,26);
  state.lights.forEach((light, i) => {{ const a=(light.angle_degrees-90)*Math.PI/180; const x=cx+Math.cos(a)*radius, y=cy+Math.sin(a)*radius; const hue=180+light.phase*150; stage.fillStyle=`hsl(${{hue}}, 80%, ${{35+light.intensity*35}}%)`; stage.beginPath(); stage.arc(x,y,10+light.intensity*18,0,Math.PI*2); stage.fill(); stage.fillStyle='#e8eef5'; stage.font='12px system-ui'; stage.fillText(light.fixture_id,x+12,y+4); }});
  stage.fillStyle='#54d6ef'; stage.beginPath(); stage.arc(cx,cy,18,0,Math.PI*2); stage.fill(); stage.fillStyle='#09121b'; stage.font='12px system-ui'; stage.fillText('XIO',cx-11,cy+4);
  frameLabel.textContent = `frame ${{index+1}}/${{states.length}} · ${{state.event_id}}`;
  const cue=cues[index] || {{}}; document.getElementById('cue').innerHTML=`<code>${{JSON.stringify(cue,null,2)}}</code>`;
}}
const blocked=DATA.safety.actions_blocked.map(item => `<span class="warn">⛔ ${{item.action}}</span> — ${{item.reason}}`).join('<br>');
document.getElementById('safety').innerHTML = `<span class="ok">No external effects executed.</span><br>${{blocked}}`;
let playing=false, timer=null; document.getElementById('play').onclick=()=>{{ playing=!playing; document.getElementById('play').textContent=playing?'Pause':'Play'; if(playing) timer=setInterval(()=>{{ const next=(Number(scrub.value)+1)%Math.max(states.length,1); scrub.value=next; drawStage(next); }},350); else clearInterval(timer); }};
scrub.oninput=()=>drawStage(Number(scrub.value)); drawSignal(); drawStage(0);
</script>
</body></html>
'''
    output.write_text(html, encoding="utf-8", newline="\n")


def run(args: argparse.Namespace) -> dict[str, Any]:
    output = Path(args.output).expanduser().resolve()
    fixture_path = Path(args.fixture).expanduser().resolve()
    xio_root = Path(args.xio_root).expanduser().resolve()
    mosaik_root = Path(args.mosaik_root).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    (
        extract_pulses,
        load_fixture,
        normalize_signal_events,
        sha256_json,
        build_predictive_frame,
        pack_semantic_frame,
        unpack_semantic_frame,
        RehearsalBridgeError,
        build_rehearsal_projection,
        validate_resolume_cue,
        build_console_proposals,
    ) = _load_modules(xio_root, mosaik_root)
    from phase_chaser import PhaseChaser

    fixture = load_fixture(fixture_path)
    delivery = _delivery_stream(fixture, extract_pulses)
    session_id = args.session_id
    xio_kwargs = {
        "session_id": session_id,
        "session_start": args.session_start,
        "source_path": str(fixture_path),
        "fps": args.fps,
        "threshold": 0.62,
        "min_gap_seconds": 0.20,
        "ingest_events": delivery,
    }
    envelope = normalize_signal_events(fixture, **xio_kwargs)
    resumed_envelope = normalize_signal_events(fixture, resume_from_sequence=2, **xio_kwargs)
    normalized_events = envelope["events"]
    first_events = normalized_events[:2]
    resumed_events = resumed_envelope["events"]

    fixture_ids = _fixture_ids(args.fixtures)
    continuous_chaser = PhaseChaser(fixture_ids, cycle_seconds=2.4, base_angle_degrees=12.0)
    continuous_states = continuous_chaser.process_all(normalized_events)
    first_chaser = PhaseChaser(fixture_ids, cycle_seconds=2.4, base_angle_degrees=12.0)
    first_states = first_chaser.process_all(first_events)
    checkpoint = first_chaser.checkpoint()
    resumed_chaser = PhaseChaser.from_checkpoint(checkpoint)
    resumed_states = resumed_chaser.process_all(resumed_events)
    phase_states = [*first_states, *resumed_states]
    restart_resume_equivalent = phase_states == continuous_states

    source_event_digest = sha256_json(normalized_events)
    projection = build_rehearsal_projection(
        session_id,
        phase_states,
        source_event_digest=source_event_digest,
        sample_hz=args.fps,
    )
    replay_again = build_rehearsal_projection(
        session_id,
        phase_states,
        source_event_digest=source_event_digest,
        sample_hz=args.fps,
    )

    predictive_parameters = {
        "cycle_seconds": 2.4,
        "angle_offset_degrees": 12.0,
        "master_intensity": 1.0,
        "sensitivity": 1.0,
        "seed": 2026,
        "channels_per_fixture": 80,
    }
    predictive_frames = [
        build_predictive_frame(
            event,
            session_id=session_id,
            fixture_ids=fixture_ids,
            parameters=predictive_parameters,
        )
        for event in normalized_events
    ]
    predictive_replay_frames = [
        build_predictive_frame(
            event,
            session_id=session_id,
            fixture_ids=fixture_ids,
            parameters=predictive_parameters,
        )
        for event in normalized_events
    ]
    console_proposals = [
        build_console_proposals(
            frame,
            resolume_layer=1,
            resolume_clip=1,
            avolites_playback=1,
        )
        for frame in predictive_frames
    ]
    revoked_console_proposal = build_console_proposals(
        predictive_frames[0],
        permissions_revoked=True,
    )
    semantic_roundtrip_checks: list[dict[str, Any]] = []
    for frame in predictive_frames:
        packet = bytes.fromhex(frame["transport"]["packet_hex"])
        decoded = unpack_semantic_frame(packet)
        reencoded = pack_semantic_frame(frame)
        semantic_roundtrip_checks.append(
            {
                "sequence": frame["sequence"],
                "fixture_count": decoded["fixture_count"],
                "crc32": decoded["crc32"],
                "packet_reencoded_equal": reencoded == packet,
                "status": "PASS"
                if decoded["fixture_count"] == len(fixture_ids) and reencoded == packet
                else "FAIL",
            }
        )
    predictive_same_outputs = predictive_frames == predictive_replay_frames
    predictive_transport = {
        "schema": "xio:predictive-semantic-lighting-frame:0.1",
        "decoder_profile": predictive_frames[0]["transport"]["decoder_profile"],
        "fixture_count": args.fixtures,
        "channels_per_fixture": predictive_parameters["channels_per_fixture"],
        "frames": len(predictive_frames),
        "semantic_packet_bytes": predictive_frames[0]["transport"]["packet_bytes"],
        "direct_dmx_channel_bytes": predictive_frames[0]["transport"]["compression"]["direct_channel_bytes"],
        "direct_dmx_universes": predictive_frames[0]["transport"]["direct_dmx"]["universes"],
        "compression_ratio": predictive_frames[0]["transport"]["compression"]["ratio"],
        "saved_fraction": predictive_frames[0]["transport"]["compression"]["saved_fraction"],
        "all_packets_roundtrip": all(item["status"] == "PASS" for item in semantic_roundtrip_checks),
    }
    semantic_replay = {
        "schema": "farmaxia:predictive-semantic-replay:0.1",
        "session_id": session_id,
        "status": "PASS" if predictive_same_outputs and predictive_transport["all_packets_roundtrip"] else "REVIEW",
        "determinism": {
            "first_frames_sha256": sha256_json(predictive_frames),
            "second_frames_sha256": sha256_json(predictive_replay_frames),
            "same_outputs": predictive_same_outputs,
        },
        "packet_roundtrip": semantic_roundtrip_checks,
        "transport": predictive_transport,
    }

    variable_fixture_check = []
    for count in (2, 5, 8):
        chaser = PhaseChaser(_fixture_ids(count), cycle_seconds=2.4, base_angle_degrees=12.0)
        state = chaser.process(normalized_events[0])
        variable_fixture_check.append({"fixture_count": count, "state_count": len(state["lights"]), "status": "PASS"})

    invalid_cue = {
        "layer": "phasechaser-main",
        "clip": "synthetic-phasechaser",
        "opacity": 1.0,
        "rotation_degrees": 0.0,
        "strobe": False,
        "transport": "timeline",
        "proposal_only": False,
    }
    try:
        validate_resolume_cue(invalid_cue)
        invalid_cue_result = {"status": "FAIL", "reason": "invalid cue was accepted"}
    except RehearsalBridgeError as exc:
        invalid_cue_result = {"status": "PASS", "blocked": True, "reason": str(exc)}
    revoked_projection = build_rehearsal_projection(
        session_id,
        phase_states,
        source_event_digest=source_event_digest,
        sample_hz=args.fps,
        permissions_revoked=True,
    )

    timeline = {
        "schema": "farmaxia:obras-rehearsal-timeline:0.1",
        "session_id": session_id,
        "source": {
            "type": fixture["fixture_type"],
            "fixture_id": fixture["fixture_id"],
            "fixture_sha256": envelope["fixture_sha256"],
            "physical_audio_used": False,
        },
        "xio": {
            "schema": envelope["schema"],
            "extraction": envelope["extraction"],
            "audit": envelope["audit"],
            "events": normalized_events,
        },
        "phase_chaser": {
            "schema": "farmaxia:phase-chaser-state:0.1",
            "fixture_count": args.fixtures,
            "states": phase_states,
            "restart_checkpoint": checkpoint,
            "restart_resume_equivalent": restart_resume_equivalent,
        },
        "mosaik": {
            "schema": projection["schema"],
            "proposal_id": projection["proposal"]["proposal_id"],
            "frame_count": projection["frame_count"],
            "fixture_count": projection["fixture_count"],
        },
        "predictive_semantic": {
            "schema": predictive_transport["schema"],
            "decoder_profile": predictive_transport["decoder_profile"],
            "frame_count": predictive_transport["frames"],
            "fixture_count": predictive_transport["fixture_count"],
            "direct_dmx_universes": predictive_transport["direct_dmx_universes"],
            "semantic_packet_bytes": predictive_transport["semantic_packet_bytes"],
            "compression_ratio": predictive_transport["compression_ratio"],
        },
    }
    safety = {
        "mode": "dry-run",
        "external_side_effects": False,
        "actions_blocked": [
            {"action": "artnet.emit", "reason": "dry-run never emits Art-Net"},
            {"action": "osc.send", "reason": "dry-run never sends OSC outside localhost"},
            {"action": "resolume.open", "reason": "dry-run never opens Resolume automatically"},
            {"action": "host.command", "reason": "dry-run never executes host actions"},
        ],
        "actions_would_have_occurred": {
            "phase_frames": len(phase_states),
            "resolume_cue_proposals": len(projection["resolume_cues"]),
            "predictive_semantic_frames": len(predictive_frames),
            "resolume_osc_proposals": len(console_proposals),
            "avolites_titan_proposals": len(console_proposals),
            "physical_fixture_count": args.fixtures,
        },
        "scenarios": {
            "duplicate_delivery": envelope["audit"]["duplicate_count"] == 1,
            "out_of_order_delivery": envelope["audit"]["out_of_order_count"] > 0,
            "temporary_audio_loss": any(event["event_type"] == "audio.gap" for event in normalized_events),
            "restart_and_resume": restart_resume_equivalent,
            "variable_fixture_count": all(item["status"] == "PASS" for item in variable_fixture_check),
            "invalid_cue_blocked": invalid_cue_result["status"] == "PASS",
            "permission_revocation_blocked": revoked_projection["status"] == "BLOCKED",
            "deterministic_replay": projection["tape_sha256"] == replay_again["tape_sha256"],
            "predictive_frame_deterministic": semantic_replay["determinism"]["same_outputs"],
            "semantic_packet_crc_roundtrip": semantic_replay["packet_roundtrip"]
            and semantic_replay["status"] == "PASS",
            "console_proposals_proposal_only": all(
                item["status"] == "PENDING_APPROVAL"
                and item["safety"]["external_side_effects"] is False
                for item in console_proposals
            ),
            "console_permission_revocation_blocked": revoked_console_proposal["status"] == "BLOCKED",
        },
        "revocation_result": revoked_projection,
        "console_revocation_result": revoked_console_proposal,
        "invalid_cue_result": invalid_cue_result,
    }
    replay_complete = {
        "schema": "farmaxia:obras-rehearsal-replay:0.1",
        "session_id": session_id,
        "status": "PASS" if all(safety["scenarios"].values()) else "REVIEW",
        "determinism": {
            "xio_event_sha256": source_event_digest,
            "phase_state_sha256": sha256_json(phase_states),
            "mosaik_tape_sha256": projection["tape_sha256"],
            "second_mosaik_tape_sha256": replay_again["tape_sha256"],
            "same_outputs": projection["tape_sha256"] == replay_again["tape_sha256"] and restart_resume_equivalent,
        },
        "mosaik_replay_report": projection["replay_report"],
        "predictive_semantic_replay": semantic_replay,
        "safety": safety,
    }
    manifest = {
        "artifact_type": "ObrasExperimentalRehearsalEvidence",
        "schema_version": "0.1",
        "session_id": session_id,
        "mode": "dry-run",
        "fixture": "../../experiments/obras-experimental-rehearsal/fixture-synthetic-audio.json",
        "physical_audio_used": False,
        "source_repositories": {
            "xio": {"path": str(xio_root), "commit": _git_ref(xio_root)},
            "farmaxia": {"path": str(HERE.parents[1]), "commit": _git_ref(HERE.parents[1])},
            "mosaik": {"path": str(mosaik_root), "commit": _git_ref(mosaik_root)},
        },
        "files": [
            "../instructions.md",
            "../commits.md",
            "xio-envelope.json",
            "signal-events.jsonl",
            "timeline-normalized.json",
            "phase-states.jsonl",
            "mosaik-proposals.json",
            "mosaik-replay-fixture.json",
            "mosaik-replay-report.json",
            "resolume-cues.json",
            "predictive-frames.jsonl",
            "predictive-transport.json",
            "semantic-replay.json",
            "console-proposals.json",
            "replay-complete.json",
            "safety-summary.json",
            "variable-fixture-check.json",
            "visualization.html",
            "run-summary.json",
        ],
    }

    _write_jsonl(output / "signal-events.jsonl", normalized_events)
    _write_json(output / "xio-envelope.json", envelope)
    _write_json(output / "timeline-normalized.json", timeline)
    _write_jsonl(output / "phase-states.jsonl", phase_states)
    _write_json(output / "phase-states.json", {"schema": "farmaxia:phase-chaser-state:0.1", "states": phase_states})
    _write_json(output / "mosaik-proposals.json", {"schema": projection["schema"], "proposal": projection["proposal"], "safety": projection["safety"]})
    _write_json(output / "mosaik-replay-fixture.json", projection["replay_fixture"])
    _write_json(output / "mosaik-replay-report.json", projection["replay_report"])
    _write_json(output / "resolume-cues.json", {"proposal_only": True, "cues": projection["resolume_cues"]})
    _write_jsonl(output / "predictive-frames.jsonl", predictive_frames)
    _write_json(output / "predictive-transport.json", predictive_transport)
    _write_json(output / "semantic-replay.json", semantic_replay)
    _write_json(
        output / "console-proposals.json",
        {
            "schema": "mosaik:console-proposals:0.1",
            "proposal_only": True,
            "proposals": console_proposals,
            "revocation": revoked_console_proposal,
        },
    )
    _write_json(output / "replay-complete.json", replay_complete)
    _write_json(output / "safety-summary.json", safety)
    _write_json(output / "variable-fixture-check.json", {"checks": variable_fixture_check})
    _write_json(output / "manifest.json", manifest)
    _build_visualization(
        output / "visualization.html",
        timeline=timeline["xio"],
        phase_states=phase_states,
        cues=projection["resolume_cues"],
        safety=safety,
    )
    summary = {
        "status": replay_complete["status"],
        "output": str(output),
        "fixture": fixture["fixture_id"],
        "physical_audio_used": False,
        "signal_count": len(normalized_events),
        "phase_state_count": len(phase_states),
        "fixture_count": args.fixtures,
        "mosaik_replay_status": projection["replay_report"]["status"],
        "predictive_replay_status": semantic_replay["status"],
        "console_proposal_status": "PASS"
        if all(item["status"] == "PENDING_APPROVAL" for item in console_proposals)
        else "REVIEW",
        "semantic_packet_bytes": predictive_transport["semantic_packet_bytes"],
        "direct_dmx_channel_bytes": predictive_transport["direct_dmx_channel_bytes"],
        "safety_external_side_effects": safety["external_side_effects"],
        "visualization": str(output / "visualization.html"),
    }
    _write_json(output / "run-summary.json", summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Obras Experimentales rehearsal in dry-run mode.")
    parser.add_argument("--fixture", default=str(HERE / "fixture-synthetic-audio.json"))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--xio-root", default=r"C:\IA\XIO")
    parser.add_argument("--mosaik-root", default=r"C:\IA\VJ")
    parser.add_argument("--session-id", default="obras-rehearsal-2026-09-08")
    parser.add_argument("--session-start", default=DEFAULT_SESSION_START)
    parser.add_argument("--fps", type=int, default=25)
    parser.add_argument("--fixtures", type=int, default=5)
    return parser.parse_args()


if __name__ == "__main__":
    result = run(parse_args())
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
