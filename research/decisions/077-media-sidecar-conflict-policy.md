# Decisión 077 — política de conflicto entre sidecars

**Fecha:** 2026-08-27
**Estado:** adoptada para prototipo read-only

## Decisión

Dos sidecars que son individualmente válidos no se pueden fusionar sólo porque
compartan asset y versión. Si afirman valores distintos dentro del mismo
alcance editorial, FARMAKSIA debe conservarlos y devolver `CONFLICT`:

```text
sidecar A ─┐
           ├─ mismo asset/hash/versión/timeline + claims distintos → CONFLICT
sidecar B ─┘                         └─ selección: null
```

La resolución requiere una autoridad explícita, una regla de precedencia
auditable o confirmación autorizada. El adapter no debe usar `last write wins`,
el nombre del archivo, el orden de llegada ni una predicción del agente como
autoridad.

## Evidencia

El experimento 075 validó el caso sintético: ambos sidecars fueron
`VERIFIED`/`COMPOSED_COMPATIBLE` por separado; uno apuntó al frame 12 y el otro
al frame 24; el resultado fue `CONFLICT`, con ambos IDs y las diferencias
`marker.marker_ref`/`marker.source_frame` preservadas. Diez kill tests bloquearon
entradas incompletas, inseguras o seleccionadas silenciosamente.

## Regla de producto

La interfaz puede mostrar “hay dos versiones incompatibles” y explicar qué
campos difieren. Puede solicitar a una persona o sistema autorizado que elija,
pero esa decisión debe ser un nuevo evento con actor, permiso, alcance,
precondición, motivo y timestamp. Hasta entonces, el estado operativo es
`CONFLICT`/`UNKNOWN`, no una timeline compuesta.

## Límite

El fixture no determina autoridad institucional, firmas, publicación temporal,
versiones concurrentes ni equivalencia editorial completa. No se incorpora un
selector automático ni una base de datos nueva.
