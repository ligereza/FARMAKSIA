# Resultados 074 — composición media por sidecar

**Fecha de ejecución:** 2026-08-27
**Estado:** `MEDIA_SIDECAR_COMPOSITION_VERIFIED`

## Evidencia obtenida

- `ffprobe-style` conservó asset, hash, codec H.264 y timebase `24/1`, pero no
  inventó timeline editorial: quedó en `PARTIAL_UNKNOWN`;
- el sidecar sintético fue `VERIFIED` al coincidir `asset_ref`,
  `asset_sha256` y `source_version=4`, además de sus referencias de asset,
  timeline y marcador;
- la composición alcanzó `COMPOSED_COMPATIBLE` con rango fuente audiovisual
  común, marcador en frame 12 (`1/2`) y sincronía de 0 frames;
- 4 entregas de eventos se redujeron a 3 únicas, conservando el duplicado, y
  las 3 permutaciones produjeron el mismo orden canónico;
- los 10 kill tests bloquearon hash/versiones obsoletos, identidad cruzada,
  rango fuera del asset, marcador inconsistente, drift A/V, procedencia
  incompleta, escritura, acción no dry-run y evento requerido;
- la política de seguridad resultó negativa para red, ejecución externa,
  datos humanos, decodificación y escritura de la fuente.

## Interpretación

El atajo funciona en el caso sintético: no necesitamos crear otro parser ni
otro ledger. El reporte de streams puede conservar su papel y el sidecar puede
completar únicamente la semántica editorial que falta, con una unión auditable.
La corrección de importación del normalizador 073 también dejó explícito que
los adapters deben cargarse con nombres de módulo propios para no confundirse
con su runner cuando se prueban como biblioteca.

## Límites y desconocidos

No se ha probado un `ffprobe` real, una firma criptográfica de sidecar, un
reemplazo de archivo, VFR, drop-frame, keyframes, time-warp, transiciones,
efectos, derechos, reloj de hardware ni compatibilidad con un player. Tampoco
se afirma que el hash por sí solo pruebe autoridad editorial.

## Próximo objetivo

Auditar conflictos entre dos sidecars válidos y versiones concurrentes. La
regla será conservar ambos historiales y devolver `CONFLICT`/`UNKNOWN` cuando
las fuentes discrepen; no seleccionar silenciosamente el último sidecar.
