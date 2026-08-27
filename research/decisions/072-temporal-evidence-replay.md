# Decisión 072 — replay temporal de evidencia

**Estado:** experimental

## Decisión

FARMAXIA separará el registro histórico de evidencia de la proyección actual.
La evidencia será append-only; la proyección se reconstruirá mediante una
función determinista que no dependa del orden de llegada.

Cada observación debe distinguir como mínimo:

```text
valid_time   = cuándo era válida en la fuente
observed_at  = cuándo fue recibida por FARMAXIA
source_version = versión o autoridad de la fuente
```

Una corrección agregará una retractación o revisión y nunca borrará el evento
original. Dos valores incompatibles de la misma versión producirán `CONFLICT`.
La falta de versión o tiempo válido producirá `UNKNOWN`.

## Base técnica

W3C PROV ya define relaciones de derivación, invalidación, generación,
ordenamiento y restricciones de consistencia para historiales de procedencia
([PROV Constraints](https://www.w3.org/TR/prov-constraints/)). La investigación
de bases temporales distingue el tiempo válido del tiempo de transacción, una
separación necesaria para no confundir cuándo ocurrió un hecho con cuándo fue
registrado ([Temporal Data Models](https://www2.cs.arizona.edu/~rts/pubs/VLDBJ99.pdf)).

OpenLineage aporta un patrón complementario: eventos de ejecución acumulativos,
entidades versionadas y metadatos extensibles por facets
([OpenLineage specification](https://github.com/OpenLineage/OpenLineage/blob/main/spec/OpenLineage.md)).

## Por qué no CRDT todavía

Un CRDT es apropiado cuando múltiples réplicas pueden escribir y fusionarse sin
una autoridad central. En el primer puente, GitLab sigue siendo la fuente de
verdad y Mattermost es destino de representación. La prioridad es detectar
conflictos y conservar correcciones, no ocultarlos mediante una fusión
automática.

## Kill tests

El contrato se considera fallido si una permutación cambia la proyección, una
retractación borra su historia, un conflicto produce un valor soportado, o una
observación temporalmente insuficiente se presenta como un hecho.

## Límite

La decisión sólo cubre replay batch sintético. No resuelve todavía streams
particionados, watermarks, firmas de eventos, consistencia transaccional,
concurrencia real ni la autorización de acciones externas.
