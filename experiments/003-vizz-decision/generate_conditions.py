"""Generate three information-equivalent VIZZ study conditions.

The generator is an experimental stimulus builder, not a VIZZ operator.
All conditions receive the same normalized data and expose its signature.
"""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).parent
SOURCE = ROOT / "decision-state.json"
OUTPUT = ROOT / "conditions"


def load_state() -> dict:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def canonical_branches(state: dict) -> list[dict]:
    return sorted(state["branches"], key=lambda branch: branch["id"])


def signature(branches: list[dict]) -> str:
    payload = json.dumps(branches, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def cell(value: object) -> str:
    return html.escape(json.dumps(value, ensure_ascii=False) if isinstance(value, list) else str(value))


def table_html(state: dict, data_signature: str) -> str:
    rows = []
    for branch in state["branches"]:
        rows.append(
            "<tr>"
            f"<th>{cell(branch['id'])}</th>"
            f"<td>{cell(branch['kind'])}</td>"
            f"<td>{branch['expected_gain']:.2f}</td>"
            f"<td>{branch['cost']:.2f}</td>"
            f"<td>{branch['uncertainty']:.2f}</td>"
            f"<td>{branch['reuse_credit']:.2f}</td>"
            f"<td>{cell(branch['evidence'])}</td>"
            "</tr>"
        )
    return f"""<!doctype html>
<meta charset="utf-8">
<title>FARMAKSIA VIZZ condition: table</title>
<h1>Condition A — tabla</h1>
<p data-information-signature="{data_signature}">Consulta: {html.escape(state['query'])}</p>
<table border="1">
<thead><tr><th>id</th><th>kind</th><th>expected gain</th><th>cost</th><th>uncertainty</th><th>reuse credit</th><th>evidence</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
<p>La persona debe elegir y explicar la decisión. La vista no recomienda una acción.</p>
"""


def static_svg(state: dict, data_signature: str) -> str:
    width, row_height = 900, 120
    rows = []
    for index, branch in enumerate(state["branches"]):
        y = 70 + index * row_height
        gain_width = branch["expected_gain"] * 700
        uncertainty_width = branch["uncertainty"] * 150
        evidence = html.escape("; ".join(branch["evidence"]))
        rows.append(
            f'<g data-branch="{html.escape(branch["id"])}">'
            f'<text x="20" y="{y}" font-size="18">{html.escape(branch["id"])} ({html.escape(branch["kind"])})</text>'
            f'<rect x="220" y="{y-22}" width="{gain_width:.2f}" height="22" fill="#3568a8"><title>expected gain {branch["expected_gain"]:.2f}</title></rect>'
            f'<rect x="220" y="{y+8}" width="{uncertainty_width:.2f}" height="14" fill="#d07b32"><title>uncertainty {branch["uncertainty"]:.2f}</title></rect>'
            f'<text x="220" y="{y+48}" font-size="14">gain {branch["expected_gain"]:.2f} · cost {branch["cost"]:.2f} · uncertainty {branch["uncertainty"]:.2f} · reuse {branch["reuse_credit"]:.2f}</text>'
            f'<text x="220" y="{y+70}" font-size="12">{evidence}</text>'
            "</g>"
        )
    height = 100 + len(state["branches"]) * row_height
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<title>FARMAKSIA VIZZ condition: static representation</title>
<desc data-information-signature="{data_signature}">{html.escape(state['query'])}</desc>
<rect width="100%" height="100%" fill="#f7f4ed"/>
<text x="20" y="30" font-size="20">Condition B — vista estática</text>
{''.join(rows)}
</svg>
"""


def interactive_html(state: dict, data_signature: str) -> str:
    payload = json.dumps(state["branches"], ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<meta charset="utf-8">
<title>FARMAKSIA VIZZ condition: linked view</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #f7f4ed; color: #1f2933; }}
button {{ margin: .2rem; padding: .45rem .7rem; }}
#items {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: .8rem; }}
.card {{ border: 1px solid #a8a29e; background: white; padding: .8rem; }}
.card.selected {{ outline: 3px solid #3568a8; }}
.bar {{ height: 12px; background: #3568a8; }}
.uncertainty {{ height: 8px; background: #d07b32; }}
small {{ color: #57534e; }}
</style>
<h1>Condition C — VIZZ candidata</h1>
<p data-information-signature="{data_signature}">{html.escape(state['query'])}</p>
<p>La interfaz permite ordenar y seleccionar; no recomienda ni decide.</p>
<div>
  <button data-sort="original">orden original</button>
  <button data-sort="expected_gain">ordenar por gain</button>
  <button data-sort="uncertainty">ordenar por uncertainty</button>
  <button data-sort="reuse_credit">ordenar por reuse credit</button>
</div>
<p id="selection">Selección humana: ninguna</p>
<section id="items"></section>
<script>
const branches = {payload};
const items = document.querySelector('#items');
const selection = document.querySelector('#selection');
function render(order) {{
  const values = [...branches];
  if (order !== 'original') values.sort((a,b) => b[order] - a[order]);
  items.replaceChildren(...values.map(branch => {{
    const card = document.createElement('article');
    card.className = 'card';
    card.dataset.branch = branch.id;
    card.innerHTML = `<h2>${{branch.id}}</h2><p>${{branch.kind}}</p>` +
      `<div class="bar" style="width:${{branch.expected_gain * 100}}%" title="expected gain"></div>` +
      `<div class="uncertainty" style="width:${{branch.uncertainty * 100}}%" title="uncertainty"></div>` +
      `<p>gain ${{branch.expected_gain.toFixed(2)}} · cost ${{branch.cost.toFixed(2)}} · uncertainty ${{branch.uncertainty.toFixed(2)}} · reuse ${{branch.reuse_credit.toFixed(2)}}</p>` +
      `<small>${{branch.evidence.join('; ')}}</small>`;
    card.addEventListener('click', () => {{
      document.querySelectorAll('.card').forEach(node => node.classList.remove('selected'));
      card.classList.add('selected');
      selection.textContent = `Selección humana: ${{branch.id}}`;
    }});
    return card;
  }}));
}}
document.querySelectorAll('button[data-sort]').forEach(button => button.addEventListener('click', () => render(button.dataset.sort)));
render('original');
</script>
"""


def main() -> None:
    state = load_state()
    branches = canonical_branches(state)
    data_signature = signature(branches)
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "table.html").write_text(table_html(state, data_signature), encoding="utf-8")
    (OUTPUT / "static.svg").write_text(static_svg(state, data_signature), encoding="utf-8")
    (OUTPUT / "vizz.html").write_text(interactive_html(state, data_signature), encoding="utf-8")
    manifest = {
        "source": "../decision-state.json",
        "data_signature": data_signature,
        "conditions": [
            {"id": "table", "path": "table.html", "mode": "static"},
            {"id": "static-graph", "path": "static.svg", "mode": "static"},
            {"id": "vizz-candidate", "path": "vizz.html", "mode": "interactive"},
        ],
        "human_authority": state["human_authority"],
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"data_signature": data_signature, "conditions": len(manifest["conditions"])}, indent=2))


if __name__ == "__main__":
    main()
