# Resultados 071 — adapter de parche CODE-INE

**Fecha de ejecución:** 2026-08-27  
**Estado:** `CODEINE_CLOUDEVENTS_ADAPTER_VERIFIED`

## Evidencia obtenida

- una tercera superficie, no institucional y no documental, reutilizó el
  núcleo común `research/tools/cloudevents_contract.py`;
- 4 entregas sintéticas se redujeron a 3 eventos únicos y 1 duplicado, sin
  perder los sobres originales;
- tres permutaciones de llegada produjeron la misma firma y el mismo orden
  canónico: `ev-change-opened`, `ev-check-passed`, `ev-file-patch`;
- la identidad del cambio, el archivo objetivo, el `base_sha256` y los claims
  conservaron sus referencias de procedencia;
- el oráculo específico de CODE-INE verificó estado de revisión, suite de
  contratos aprobada, permiso de previsualización y coincidencia del hash base;
- la acción quedó en `DRY_RUN_ONLY`, requirió confirmación y no ejecutó código
  ni escribió en el workspace;
- los 9 kill tests bloquearon evento faltante, superficie equivocada,
  procedencia ausente, ejecución de código, escritura externa, permiso
  ausente, precondición vieja, check fallido y hash base desconocido.

## Interpretación

La tercera superficie cambió el significado del payload: ahora hay que
verificar un parche, su archivo objetivo, su hash base y una precondición de
revisión. Esa diferencia se resolvió dentro del adapter CODE-INE; no obligó a
crear otro ledger, otro sistema de replay ni otro contrato de procedencia.

La evidencia demuestra reutilización arquitectónica en un fixture sintético,
no compatibilidad automática con un repositorio real ni seguridad suficiente
para aplicar parches sin una política adicional.

## Seguridad y alcance

No hubo red, escritura externa, datos humanos, cámara, ejecución arbitraria ni
descargas. El adapter sólo propone una previsualización local y reversible.
Quedan fuera la aplicación real del parche, el análisis sintáctico, firmas de
commits, sandboxing de herramientas y cualquier integración con una API viva.

## Siguiente objetivo

Auditar una superficie media sólo si introduce una semántica materialmente
distinta —por ejemplo timeline, codec o sincronización audiovisual—. Si sólo
repite identidad, procedencia, permisos, replay y dry-run, se documentará como
no necesaria y no se añadirá otro adapter.
