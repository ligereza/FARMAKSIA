# Resultados 075 — conflicto entre sidecars media

**Fecha de ejecución:** 2026-08-27
**Estado:** `CONFLICT`

## Evidencia obtenida

- ambos sidecars pasaron el verificador 074 como `VERIFIED` y
  `COMPOSED_COMPATIBLE`;
- ambos compartieron `asset_ref`, hash, `source_version=4`, timeline y
  timebase;
- el sidecar A ubicó el marcador en frame 12 (`1/2`) y el B en frame 24
  (`1/1`);
- la proyección devolvió `CONFLICT`, conservó ambos sidecar IDs y dejó
  `selection: null`;
- la diferencia fue localizada en `marker.marker_ref` y
  `marker.source_frame`, no en el asset ni en el rango audiovisual;
- 4 entregas se redujeron a 3 eventos únicos y las 3 permutaciones produjeron
  el mismo replay;
- los 10 kill tests bloquearon claims incompletos, identidad cruzada,
  versiones/hash obsoletos, escritura, acción no dry-run, selección silenciosa
  y el falso conflicto entre claims idénticos;
- no hubo red, ejecución externa, datos humanos, decodificación ni escritura.

## Interpretación

La regla de no elegir silenciosamente funciona en el caso controlado. “Válido”
significa que cada sidecar es consistente con sus fuentes; no significa que dos
claims incompatibles puedan fusionarse. El conflicto debe viajar como estado
visible para que una autoridad autorizada lo resuelva.

## Límites y desconocidos

No se determina cuál sidecar tiene autoridad, cuál fue publicado primero ni si
una firma es legítima. Tampoco se prueba un vector de versión real, reemplazo
de archivos, edición concurrente, VFR, derechos ni un servicio institucional.

## Próximo objetivo

Definir el contrato mínimo de autoridad y resolución explícita para sidecars
concurrentes, manteniendo el default `CONFLICT`/`UNKNOWN` y sin incorporar un
selector automático.
