#!/usr/bin/env python3
"""Render a standalone playback preview for recorded light-field snapshots."""

import argparse
import json
import math
from pathlib import Path


def fail(message):
    raise ValueError(message)


def finite_number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        fail(label + " must be a finite number")
    value = float(value)
    if not math.isfinite(value):
        fail(label + " must be a finite number")
    return value


def validate_tape(data):
    if not isinstance(data, dict):
        fail("tape root must be a JSON object")
    sample_hz = finite_number(data.get("sample_hz"), "sample_hz")
    if sample_hz <= 0:
        fail("sample_hz must be greater than zero")
    frames = data.get("frames")
    if not isinstance(frames, list) or not frames:
        fail("frames must be a non-empty array")
    for frame_index, frame in enumerate(frames):
        if not isinstance(frame, dict):
            fail("frames[%d] must be an object" % frame_index)
        for key in ("time_s", "phase", "tempo", "energy", "audio_envelope"):
            finite_number(frame.get(key), "frames[%d].%s" % (frame_index, key))
        fixtures = frame.get("fixtures")
        if not isinstance(fixtures, dict):
            fail("frames[%d].fixtures must be an object" % frame_index)
        for fixture_id, fixture in fixtures.items():
            prefix = "frames[%d].fixtures[%s]" % (frame_index, fixture_id)
            if not isinstance(fixture, dict):
                fail(prefix + " must be an object")
            position = fixture.get("position")
            if not isinstance(position, list) or len(position) != 3:
                fail(prefix + ".position must contain [x, y, z]")
            for axis, value in zip(("x", "y", "z"), position):
                finite_number(value, prefix + ".position." + axis)
            intensity = finite_number(fixture.get("intensity"), prefix + ".intensity")
            if not 0 <= intensity <= 1:
                fail(prefix + ".intensity must be between 0 and 1")
            rgb = fixture.get("rgb")
            if not isinstance(rgb, list) or len(rgb) != 3:
                fail(prefix + ".rgb must contain [r, g, b]")
            for channel, value in zip(("r", "g", "b"), rgb):
                value = finite_number(value, prefix + ".rgb." + channel)
                if not 0 <= value <= 1:
                    fail(prefix + ".rgb." + channel + " must be between 0 and 1")
            if "universe" in fixture:
                finite_number(fixture["universe"], prefix + ".universe")
            channels = fixture.get("channels", {})
            if not isinstance(channels, dict):
                fail(prefix + ".channels must be an object")
            for name, value in channels.items():
                finite_number(value, prefix + ".channels." + str(name))
    return data


def json_for_script(data):
    text = json.dumps(data, ensure_ascii=True, separators=(",", ":"))
    return text.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")


HTML_TEMPLATE = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dimensiones del Orden - playback</title>
<style>
:root{color-scheme:dark;--bg:#11161b;--panel:#192229;--line:#33434d;--text:#d9e2e5;--muted:#91a5ad;--accent:#7fd1c3}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px system-ui,sans-serif}main{max-width:1180px;margin:0 auto;padding:22px}h1{font-size:22px;font-weight:500;margin:0 0 4px}h2{font-size:14px;font-weight:600;margin:0 0 12px;color:var(--muted)}.notice{border:1px solid #49635f;background:#172623;color:#b9e2d9;padding:10px 12px;margin:16px 0;border-radius:6px}.controls,.panel{background:var(--panel);border:1px solid var(--line);border-radius:8px}.controls{display:flex;align-items:center;gap:12px;padding:12px}.controls button{background:#24343c;border:1px solid #50636b;color:var(--text);border-radius:5px;padding:7px 12px;cursor:pointer}.controls button:hover{border-color:var(--accent)}input[type=range]{accent-color:var(--accent);flex:1}.readout{min-width:170px;text-align:right;color:var(--muted);font-variant-numeric:tabular-nums}.grid{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(280px,.8fr);gap:14px;margin-top:14px}.panel{padding:14px}.canvas-wrap{background:#0b1013;border:1px solid #293941;border-radius:6px;overflow:hidden}.canvas-wrap canvas{display:block;width:100%;height:auto}.legend{display:flex;justify-content:space-between;color:var(--muted);font-size:12px;margin-top:8px}.fixture{border-top:1px solid var(--line);padding:10px 0}.fixture:first-child{border-top:0;padding-top:0}.fixture-head{display:flex;justify-content:space-between}.fixture-id{color:var(--accent);font-weight:600}.meta{color:var(--muted);font-size:12px;margin-top:4px}.bar{height:7px;background:#0c1114;border-radius:4px;margin-top:6px;overflow:hidden}.bar i{display:block;height:100%;background:var(--accent)}.channels{display:grid;grid-template-columns:1fr auto;gap:4px 12px;margin-top:7px;font-size:12px}.channels span:nth-child(even){color:var(--muted);font-variant-numeric:tabular-nums}@media(max-width:760px){main{padding:14px}.grid{grid-template-columns:1fr}.readout{min-width:145px}}
</style>
</head>
<body>
<main>
<h1>Dimensiones del Orden</h1>
<h2>Reproductor de snapshots de campo luminoso</h2>
<div class="notice">Simulaci&oacute;n: salida de software; sin medici&oacute;n f&iacute;sica</div>
<div class="controls"><button id="play" type="button">Reproducir</button><input id="scrub" type="range" min="0" max="0" value="0" step="1" aria-label="Frame"><div class="readout"><span id="time">0.00 s</span> &middot; <span id="bpm">0 BPM</span></div></div>
<div class="grid"><section class="panel"><h2>Layout superior: x/y</h2><div class="canvas-wrap"><canvas id="field" width="760" height="520"></canvas></div><div class="legend"><span>Arriba: +y</span><span>Derecha: +x</span><span>z: ver ficha</span></div></section><aside class="panel"><h2>Fixtures y canales DMX</h2><div id="fixtures"></div></aside></div>
</main>
<script>
const TAPE = __TAPE__;
const frames = TAPE.frames;
const canvas = document.getElementById("field");
const ctx = canvas.getContext("2d");
const scrub = document.getElementById("scrub");
const play = document.getElementById("play");
const timeEl = document.getElementById("time");
const bpmEl = document.getElementById("bpm");
let index = 0;
let timer = null;
scrub.max = Math.max(0, frames.length - 1);
const allFixtures = () => { const ids = new Set(); frames.forEach(f => Object.keys(f.fixtures).forEach(id => ids.add(id))); return [...ids].sort(); };
const rgb = (v, scale) => "rgb(" + v.map(x => Math.round(Math.max(0, Math.min(1, x)) * scale)).join(",") + ")";
function draw(frame) {
  const entries = Object.entries(frame.fixtures);
  ctx.fillStyle = "#0b1013"; ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = "#26353c"; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(0, canvas.height / 2); ctx.lineTo(canvas.width, canvas.height / 2); ctx.moveTo(canvas.width / 2, 0); ctx.lineTo(canvas.width / 2, canvas.height); ctx.stroke();
  const points = []; frames.forEach(f => Object.values(f.fixtures).forEach(x => points.push(x.position)));
  const xs = points.map(p => p[0]), ys = points.map(p => p[1]);
  const minX = Math.min(...xs, -1), maxX = Math.max(...xs, 1), minY = Math.min(...ys, -1), maxY = Math.max(...ys, 1);
  const pad = 46, sx = (canvas.width - pad * 2) / Math.max(0.001, maxX - minX), sy = (canvas.height - pad * 2) / Math.max(0.001, maxY - minY);
  const project = p => [pad + (p[0] - minX) * sx, canvas.height - pad - (p[1] - minY) * sy];
  entries.forEach(([id, f]) => { const [x, y] = project(f.position); const glow = 7 + f.intensity * 22; ctx.beginPath(); ctx.fillStyle = rgb(f.rgb, 0.18); ctx.arc(x, y, glow, 0, Math.PI * 2); ctx.fill(); ctx.beginPath(); ctx.fillStyle = rgb(f.rgb, 255 * (0.25 + f.intensity * 0.75)); ctx.arc(x, y, 5 + f.intensity * 8, 0, Math.PI * 2); ctx.fill(); ctx.strokeStyle = "#dce7e8"; ctx.stroke(); ctx.fillStyle = "#d9e2e5"; ctx.font = "12px system-ui"; ctx.fillText(id, x + 10, y - 8); });
  document.getElementById("fixtures").innerHTML = entries.length ? entries.map(([id, f]) => { const channels = Object.entries(f.channels || {}).map(([k,v]) => "<span>" + esc(k) + "</span><span>" + num(v) + "</span>").join(""); return "<div class=\"fixture\"><div class=\"fixture-head\"><span class=\"fixture-id\">" + esc(id) + "</span><span>U" + esc(String(f.universe)) + "</span></div><div class=\"meta\">x " + num(f.position[0]) + " &middot; y " + num(f.position[1]) + " &middot; z " + num(f.position[2]) + "</div><div class=\"bar\"><i style=\"width:" + (f.intensity * 100) + "%\"></i></div><div class=\"meta\">intensidad " + Math.round(f.intensity * 100) + "% &middot; RGB " + f.rgb.map(x => Math.round(x * 255)).join(", ") + "</div><div class=\"channels\">" + (channels || "<span>sin canales adicionales</span>") + "</div></div>"; }).join("") : "<div class=\"meta\">Sin fixtures en este snapshot.</div>";
  timeEl.textContent = num(frame.time_s) + " s"; bpmEl.textContent = num(frame.tempo) + " BPM";
}
function esc(value) { return String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c])); }
function num(value) { return Number(value).toFixed(2); }
function show(next) { index = Math.max(0, Math.min(frames.length - 1, next)); scrub.value = index; draw(frames[index]); }
function stop() { if (timer !== null) { clearInterval(timer); timer = null; } play.textContent = "Reproducir"; }
function start() { stop(); play.textContent = "Pausa"; timer = setInterval(() => { if (index >= frames.length - 1) { stop(); return; } show(index + 1); }, 1000 / TAPE.sample_hz); }
play.addEventListener("click", () => timer === null ? start() : stop()); scrub.addEventListener("input", e => { stop(); show(Number(e.target.value)); }); show(0);
</script>
</body>
</html>
"""


def build_html(data):
    return HTML_TEMPLATE.replace("__TAPE__", json_for_script(data))


def main():
    parser = argparse.ArgumentParser(description="Create a standalone light-field playback HTML")
    parser.add_argument("--frames", required=True, help="Input snapshot tape JSON")
    parser.add_argument("--output", required=True, help="Output standalone HTML")
    parser.add_argument("--validate-only", action="store_true", help="Validate the tape without writing HTML")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.frames).read_text(encoding="utf-8"))
        validate_tape(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    if args.validate_only:
        print("VALID_TAPE")
        return
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_html(data), encoding="utf-8", newline="\n")
    print("WROTE_HTML %s" % output)


if __name__ == "__main__":
    main()
