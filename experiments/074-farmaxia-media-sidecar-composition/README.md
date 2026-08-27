# Experimento 074 — composición media por sidecar

Este experimento prueba el atajo operativo que faltaba en 073: cuando una
fuente tipo `ffprobe` conoce el asset, sus streams y su timebase, un sidecar
editorial autorizado puede aportar la timeline, el rango de origen y los
marcadores que no están en el reporte de streams.

La unión sólo se acepta si coinciden tres llaves:

1. `asset_ref` — identidad declarada del asset;
2. `asset_sha256` — contenido/versionado del asset;
3. `source_version` — versión vigente de la fuente.

Después se comprueban rangos racionales, sincronía audio/video, marcador dentro
del clip, procedencia completa y políticas read-only/dry-run. Si una llave,
rango o permiso falla, el resultado es `BLOCKED`; no se rellena la ausencia con
una inferencia.

## Resultado mínimo

- `ffprobe-style` antes de componer: `PARTIAL_UNKNOWN`;
- sidecar editorial: `VERIFIED`;
- composición: `COMPOSED_COMPATIBLE`;
- marcador: frame 12, tiempo `1/2`;
- desfase audio/video: 0 frames;
- replay: 3 permutaciones con la misma proyección;
- 10 kill tests bloquean hash, versión, identidad, rango, marcador, sincronía,
  procedencia, escritura, acción no dry-run y evento requerido.

## Reproducir

```powershell
python experiments/074-farmaxia-media-sidecar-composition/run_experiment.py
python experiments/074-farmaxia-media-sidecar-composition/run_contract_test.py
python experiments/074-farmaxia-media-sidecar-composition/run_kill_test.py
```

El runner reutiliza el fixture 072, el normalizador 073 y el núcleo común de
CloudEvents; no instala OTIO/FFmpeg, no ejecuta `ffprobe`, no decodifica media,
no usa red y no escribe la fuente. El fixture es sintético: todavía no prueba
sidecars firmados, archivos reemplazados, VFR, drop-frame, keyframes,
transiciones, efectos, derechos ni un editor/player real.
