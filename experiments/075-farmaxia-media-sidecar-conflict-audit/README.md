# Experimento 075 — conflicto entre sidecars media

Este experimento prueba el caso que 074 todavía dejaba abierto: dos sidecars
editoriales pueden ser válidos por separado y aun así afirmar cosas distintas
sobre el mismo asset, timeline y versión.

El fixture usa dos sidecars `VERIFIED` para el mismo alcance:

```text
asset + hash + source_version + timeline
                    ↓
        sidecar A: marcador en frame 12
        sidecar B: marcador en frame 24
                    ↓
                 CONFLICT
```

La salida conserva ambos IDs, el alcance común y los campos discrepantes. No
aplica `last write wins`, no elige el sidecar más reciente y no convierte una
discrepancia en `COMPOSED_COMPATIBLE`.

## Resultado mínimo

- 2 candidatos: ambos `VERIFIED` y `COMPOSED_COMPATIBLE` por separado;
- conflicto: `CONFLICT` sin bloqueadores de ejecución;
- diferencia: `marker.marker_ref` y `marker.source_frame`;
- candidatos preservados: `editorial-sidecar-cut-01-v4-a` y `...-b`;
- selección: `null`;
- replay CloudEvents: 3 órdenes con la misma proyección;
- 10 kill tests bloquean candidatos ausentes/duplicados, identidad/hash/
  versión cruzados, escritura, acciones no dry-run, selección silenciosa,
  eventos ausentes y claims idénticos presentados como conflicto.

## Reproducir

```powershell
python experiments/075-farmaxia-media-sidecar-conflict-audit/run_experiment.py
python experiments/075-farmaxia-media-sidecar-conflict-audit/run_contract_test.py
python experiments/075-farmaxia-media-sidecar-conflict-audit/run_kill_test.py
```

El runner reutiliza el verificador 074 y el núcleo de CloudEvents. El caso es
sintético y read-only: no prueba firmas, autoridad editorial real, archivos
reemplazados, timestamps de publicación ni resolución legítima por parte de
una institución.
