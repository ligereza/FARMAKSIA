# Experimento 073 — puente de representaciones media

Este experimento compara dos formas consolidadas de describir media sin
instalarlas ni leer archivos reales:

- una representación estilo OpenTimelineIO, orientada a edición y timeline;
- un reporte estilo `ffprobe`, orientado a streams, codec, timebase y duración.

La misma película puede tener ambas descripciones, pero no dicen lo mismo.
OTIO-style permite reconstruir la timeline, el rango fuente y el marcador; el
reporte ffprobe-style identifica el asset y sus streams, pero no contiene por
sí solo el montaje editorial ni la posición del marcador. En vez de rellenar
esa ausencia, el puente devuelve `PARTIAL_UNKNOWN` y pide un sidecar o una
fuente editorial adicional.

## Resultado mínimo

- OTIO-style: `COMPATIBLE` con el contrato media 072;
- ffprobe-style: `PARTIAL_UNKNOWN`;
- asset, hash, codec y timebase coinciden entre ambas representaciones;
- equivalencia completa: `false`;
- replay CloudEvents: tres órdenes con la misma proyección;
- operación: read-only, sin decodificación ni escritura.

## Reproducir

```powershell
python experiments/073-farmaxia-media-representation-bridge/run_experiment.py
python experiments/073-farmaxia-media-representation-bridge/run_contract_test.py
python experiments/073-farmaxia-media-representation-bridge/run_kill_test.py
```

Los fixtures son sintéticos. No se instalaron OpenTimelineIO ni FFmpeg, no se
ejecutó `ffprobe`, no se decodificó media y no se afirmó compatibilidad con
VFR, drop-frame, keyframes, transiciones, efectos, derechos o un player real.
