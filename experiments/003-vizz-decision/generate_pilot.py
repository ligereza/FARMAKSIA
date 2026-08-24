"""Generate the offline, local-only VIZZ human pilot instrument."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).parent
SOURCE = ROOT / "decision-state.json"
OUTPUT = ROOT / "pilot.html"


HTML_TEMPLATE = r'''<!doctype html>
<html lang="es">
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline';">
<title>FARMAKSIA — piloto VIZZ</title>
<style>
body { font-family: system-ui, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; background: #f7f4ed; color: #1f2933; }
button, input, select, textarea { font: inherit; }
button { padding: .55rem .8rem; margin: .2rem; cursor: pointer; min-height: 44px; }
input, select, textarea { min-height: 44px; }
:focus-visible { outline: 3px solid #1d4ed8; outline-offset: 2px; }
fieldset { background: white; border: 1px solid #a8a29e; margin: 1rem 0; padding: 1rem; }
#items { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: .8rem; }
.card { border: 1px solid #a8a29e; background: white; padding: .8rem; }
.card.selected { outline: 3px solid #3568a8; }
.bar { height: 12px; background: #3568a8; }
.uncertainty { height: 8px; background: #d07b32; }
.muted { color: #57534e; }
.hidden { display: none; }
table { border-collapse: collapse; width: 100%; background: white; }
th, td { border: 1px solid #a8a29e; padding: .45rem; text-align: left; vertical-align: top; }
.row { margin: .8rem 0; padding: .7rem; background: white; border: 1px solid #d6d3d1; }
</style>
<main>
  <h1>Piloto humano VIZZ</h1>
  <p class="muted">Instrumento local. No envía datos. No define valor artístico.</p>
  <section id="intro">
    <p>Completarás tres condiciones con la misma información. En cada una elige una acción, indica confianza y explica tu decisión.</p>
    <label>Código anónimo <input id="participant" autocomplete="off"></label>
    <label>Semilla de orden <input id="seed" autocomplete="off" placeholder="vacío = aleatoria"></label>
    <button id="begin">Comenzar</button>
  </section>
  <section id="trial" class="hidden">
    <p id="progress" role="status" aria-live="polite"></p>
    <div id="condition"></div>
    <fieldset>
      <legend>Respuesta humana</legend>
      <label>Elección
        <select id="choice" required aria-describedby="form-error">
          <option value="">Seleccionar…</option>
          <option value="continue-A">continue-A</option>
          <option value="switch-B">switch-B</option>
          <option value="reuse-C">reuse-C</option>
          <option value="stop">stop</option>
        </select>
      </label>
      <div class="row"><label>Confianza: <output id="confidence-value">50</output>/100</label><input id="confidence" type="range" min="0" max="100" value="50"></div>
      <label><input id="uncertainty" type="checkbox"> Detecté la incertidumbre relevante</label>
      <p><label>Explicación<br><textarea id="explanation" rows="4" cols="70" required aria-describedby="form-error"></textarea></label></p>
      <p id="form-error" class="muted" role="alert" aria-live="assertive"></p>
      <button id="submit">Registrar decisión</button>
    </fieldset>
  </section>
  <section id="done" class="hidden">
    <h2>Piloto terminado</h2>
    <p>Los datos permanecen en memoria hasta descargarlos. Revisa que no contengan información identificable.</p>
    <button id="download">Descargar JSON</button>
    <pre id="summary"></pre>
  </section>
</main>
<script>
const branches = __BRANCHES__;
const dataSignature = '__SIGNATURE__';
const conditionNames = ['table', 'static-graph', 'vizz-candidate'];
let participantCode = '';
let seed = '';
let order = [];
let trialIndex = 0;
let trialStarted = 0;
let records = [];

function seededValue(text) {
  let value = 2166136261;
  for (const char of text) value = Math.imul(value ^ char.charCodeAt(0), 16777619);
  return value >>> 0;
}

function shuffled(values, seedValue) {
  const result = [...values];
  let value = seedValue || 1;
  for (let index = result.length - 1; index > 0; index -= 1) {
    value = (Math.imul(value, 1664525) + 1013904223) >>> 0;
    const swap = value % (index + 1);
    [result[index], result[swap]] = [result[swap], result[index]];
  }
  return result;
}

function branchRows() {
  return branches.map(branch => `<tr><th>${branch.id}</th><td>${branch.kind}</td><td>${branch.expected_gain.toFixed(2)}</td><td>${branch.cost.toFixed(2)}</td><td>${branch.uncertainty.toFixed(2)}</td><td>${branch.reuse_credit.toFixed(2)}</td><td>${branch.evidence.join('; ')}</td></tr>`).join('');
}

function renderTable() {
  return `<h2>Condición A — tabla</h2><p class="muted">Firma: ${dataSignature}</p><table><thead><tr><th>id</th><th>kind</th><th>gain</th><th>cost</th><th>uncertainty</th><th>reuse</th><th>evidence</th></tr></thead><tbody>${branchRows()}</tbody></table>`;
}

function renderStatic() {
  const rows = branches.map(branch => `<div class="row"><strong>${branch.id}</strong> (${branch.kind})<div class="bar" style="width:${branch.expected_gain * 100}%"></div><div class="uncertainty" style="width:${branch.uncertainty * 100}%"></div><div>gain ${branch.expected_gain.toFixed(2)} · cost ${branch.cost.toFixed(2)} · uncertainty ${branch.uncertainty.toFixed(2)} · reuse ${branch.reuse_credit.toFixed(2)}</div><small>${branch.evidence.join('; ')}</small></div>`).join('');
  return `<h2>Condición B — vista estática</h2><p class="muted">Firma: ${dataSignature}</p>${rows}`;
}

function renderVizz(orderKey = 'original') {
  const values = [...branches];
  if (orderKey !== 'original') values.sort((a, b) => b[orderKey] - a[orderKey]);
  const cards = values.map(branch => `<article class="card" data-id="${branch.id}" tabindex="0" role="button" aria-pressed="false" aria-label="Seleccionar ${branch.id}"><h3>${branch.id}</h3><p>${branch.kind}</p><div class="bar" style="width:${branch.expected_gain * 100}%"></div><div class="uncertainty" style="width:${branch.uncertainty * 100}%"></div><p>gain ${branch.expected_gain.toFixed(2)} · cost ${branch.cost.toFixed(2)} · uncertainty ${branch.uncertainty.toFixed(2)} · reuse ${branch.reuse_credit.toFixed(2)}</p><small>${branch.evidence.join('; ')}</small></article>`).join('');
  return `<h2>Condición C — VIZZ candidata</h2><p class="muted">Firma: ${dataSignature}</p><p>Esta interfaz permite ordenar y seleccionar. No recomienda una acción.</p><div><button data-sort="original">orden original</button><button data-sort="expected_gain">ordenar por gain</button><button data-sort="uncertainty">ordenar por uncertainty</button><button data-sort="reuse_credit">ordenar por reuse credit</button></div><p id="vizz-selection">Selección visual: ninguna</p><div id="items">${cards}</div>`;
}

function renderCondition(name) {
  const root = document.querySelector('#condition');
  root.innerHTML = name === 'table' ? renderTable() : name === 'static-graph' ? renderStatic() : renderVizz();
  if (name === 'vizz-candidate') {
    root.querySelectorAll('[data-sort]').forEach(button => button.addEventListener('click', () => {
      root.innerHTML = renderVizz(button.dataset.sort);
      attachVizzHandlers();
    }));
    attachVizzHandlers();
  }
}

function attachVizzHandlers() {
  const root = document.querySelector('#condition');
  function selectCard(card) {
    root.querySelectorAll('.card').forEach(node => node.classList.remove('selected'));
    root.querySelectorAll('.card').forEach(node => node.setAttribute('aria-pressed', 'false'));
    card.classList.add('selected');
    card.setAttribute('aria-pressed', 'true');
    root.querySelector('#vizz-selection').textContent = `Selección visual: ${card.dataset.id}`;
  }
  root.querySelectorAll('.card').forEach(card => {
    card.addEventListener('click', () => selectCard(card));
    card.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        selectCard(card);
      }
    });
  });
}

function startTrial() {
  const condition = order[trialIndex];
  document.querySelector('#progress').textContent = `Condición ${trialIndex + 1} de ${order.length}: ${condition}`;
  renderCondition(condition);
  document.querySelector('#choice').value = '';
  document.querySelector('#confidence').value = 50;
  document.querySelector('#confidence-value').textContent = '50';
  document.querySelector('#uncertainty').checked = false;
  document.querySelector('#explanation').value = '';
  document.querySelector('#form-error').textContent = '';
  trialStarted = performance.now();
}

function submitTrial() {
  const choice = document.querySelector('#choice').value;
  const explanation = document.querySelector('#explanation').value.trim();
  if (!choice || !explanation) {
    document.querySelector('#form-error').textContent = 'Falta elegir una acción y escribir una explicación.';
    return;
  }
  records.push({
    condition: order[trialIndex],
    order_index: trialIndex,
    choice,
    duration_ms: Math.round(performance.now() - trialStarted),
    confidence: Number(document.querySelector('#confidence').value),
    detected_uncertainty: document.querySelector('#uncertainty').checked,
    explanation,
    data_signature: dataSignature
  });
  trialIndex += 1;
  if (trialIndex < order.length) startTrial();
  else finish();
}

function finish() {
  document.querySelector('#trial').classList.add('hidden');
  document.querySelector('#done').classList.remove('hidden');
  document.querySelector('#summary').textContent = JSON.stringify({schema: 'farmaxia:vizz-pilot:0.1', participant: participantCode, seed, order, records}, null, 2);
}

function downloadResults() {
  const payload = {schema: 'farmaxia:vizz-pilot:0.1', participant: participantCode, seed, order, data_signature: dataSignature, records};
  const blob = new Blob([JSON.stringify(payload, null, 2)], {type: 'application/json'});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `farmaxia-vizz-${participantCode || 'anonymous'}.json`;
  link.click();
  URL.revokeObjectURL(link.href);
}

document.querySelector('#confidence').addEventListener('input', event => document.querySelector('#confidence-value').textContent = event.target.value);
document.querySelector('#begin').addEventListener('click', () => {
  participantCode = document.querySelector('#participant').value.trim() || 'anonymous';
  seed = document.querySelector('#seed').value.trim() || String(Date.now());
  order = shuffled(conditionNames, seededValue(seed));
  trialIndex = 0;
  records = [];
  document.querySelector('#intro').classList.add('hidden');
  document.querySelector('#trial').classList.remove('hidden');
  startTrial();
});
document.querySelector('#submit').addEventListener('click', submitTrial);
document.querySelector('#download').addEventListener('click', downloadResults);
</script>
</html>
'''


def main() -> None:
    state = json.loads(SOURCE.read_text(encoding="utf-8"))
    branches = sorted(state["branches"], key=lambda branch: branch["id"])
    payload = json.dumps(branches, ensure_ascii=False).replace("</", "<\\/")
    canonical = json.dumps(branches, sort_keys=True, separators=(",", ":")).encode("utf-8")
    data_signature = hashlib.sha256(canonical).hexdigest().upper()
    pilot = HTML_TEMPLATE.replace("__BRANCHES__", payload).replace("__SIGNATURE__", data_signature)
    OUTPUT.write_text(pilot, encoding="utf-8")
    print(json.dumps({"pilot": str(OUTPUT), "data_signature": data_signature}, indent=2))


if __name__ == "__main__":
    main()
