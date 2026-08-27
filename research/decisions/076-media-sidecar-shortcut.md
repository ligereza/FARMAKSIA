# Decisión 076 — atajo de sidecar para media

**Fecha:** 2026-08-27
**Estado:** adoptada para prototipo read-only

## Decisión

Cuando una fuente tipo `ffprobe` no contiene timeline editorial, FARMAKSIA
puede componerla con un sidecar separado, siempre que verifique conjuntamente:

```text
asset_ref + asset_sha256 + source_version
        ↓
rangos exactos + marcador + sincronía + procedencia
        ↓
COMPOSED_COMPATIBLE o BLOCKED
```

El sidecar no se convierte en una fuente universal ni obtiene permiso para
editar, exportar o reproducir. Su función es completar la representación que
falta y dejar visible qué parte proviene de cada fuente.

## Por qué es un atajo real

El experimento 073 ya mostró que no hacía falta inventar un parser nuevo: la
representación de streams tenía identidad, hash, codec y timebase, pero carecía
de edición. El 074 demostró que un sidecar puede aportar sólo esa semántica y
reutilizar el núcleo de CloudEvents, replay, procedencia y dry-run de los
experimentos anteriores.

Esto reduce el trabajo en tres sentidos:

- no instalamos OTIO ni FFmpeg para validar la decisión arquitectónica;
- no duplicamos el ledger ni el sistema de eventos;
- no convertimos una ausencia de metadata en una afirmación inventada.

## Evidencia y límites

El caso sintético terminó en `MEDIA_SIDECAR_COMPOSITION_VERIFIED`: sidecar
`VERIFIED`, composición `COMPOSED_COMPATIBLE`, marcador en frame 12 (`1/2`),
sincronía de 0 frames y 10 kill tests pasando. Esto demuestra una composición
lógica controlada, no interoperabilidad con archivos reales.

Quedan abiertos firmas de sidecar, autoridad editorial, reemplazos de archivos,
sidecars concurrentes, VFR, drop-frame, keyframes, efectos, derechos y player.
No se deben resolver seleccionando el sidecar más reciente sin comparar
provenance: el [experimento 075](../../experiments/075-farmaxia-media-sidecar-conflict-audit/README.md)
verificó que debe devolver `CONFLICT` o `UNKNOWN` ante dos versiones
incompatibles.

## Regla de adopción

Un adapter real sólo podrá usar este atajo si conserva las tres llaves, los
rangos exactos, las referencias de derivación, el modo read-only y la acción
dry-run. Una discrepancia debe conservar ambos inputs y bloquear la composición.
