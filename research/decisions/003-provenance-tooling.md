# Decisión 003 — procedencia experimental

Fecha: 2026-08-23

## Alternativas investigadas

| Alternativa | Aporta | Problema actual | Decisión |
|---|---|---|---|
| W3C PROV | modelo general de entidades, actividades, agentes y derivaciones | no es un parser/ejecutor local por sí mismo | adoptar como referencia conceptual |
| RO-Crate | paquete de investigación con contexto y archivos | demasiado amplio para el primer fixture | diferir |
| OpenLineage | eventos de ejecución para jobs/datasets y extensiones | unidad de lineage no coincide todavía con obra/hipótesis | diferir |
| JSON + biblioteca estándar | portable, inspeccionable, sin dependencia | no garantiza por sí solo semántica completa | adoptar como baseline local |

## Herramienta adoptada

JSON local validado por
`research/tools/validate_provenance.py`, con vocabulario mínimo inspirado en
PROV. El mismo validador ya acepta los manifiestos de los experimentos 001 y
002. No se instala un paquete externo.

## Condición de reemplazo

Evaluar RO-Crate u OpenLineage cuando exista más de un experimento, una
ejecución distribuida, un backend externo o necesidad real de interoperabilidad.
La adopción deberá demostrar que resuelve una medición que el manifiesto local
no puede resolver.

## Kill test del manifiesto

Modificar un archivo de entrada o eliminar una entidad referenciada. El
validador debe fallar y explicar si el problema es hash, referencia, autoridad
o derivación incompleta.
