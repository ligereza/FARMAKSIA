# Decisión 069 — Preservación semántica relativa a consultas

**Estado:** adoptada como contrato experimental  
**Fecha:** 2026-08-27  
**Frentes:** RepresentationSpace, X-ANA-X, CODE-INE, VIZZ

## Decisión

La afirmación “una representación conserva la fuente” se interpretará como
equivalencia observacional respecto de un conjunto explícito de consultas
críticas `Q`, no como igualdad visual ni como isomorfismo total del grafo.

Para cada vista `R_i` y consulta `q` del contrato:

```text
answer(q, source) == answer(q, R_i)
```

Las entidades y relaciones usan referencias estables. Las relaciones críticas
conservan tipo y extremos. Los `UNKNOWN` permanecen explícitos. Todo claim
visible puede regresar a su fuente mediante `source_ref`.

## Implicaciones

- Una vista puede ocultar, agrupar, ordenar o traducir mientras preserve las
  consultas que la tarea declara críticas.
- `show_full` sigue siendo necesario para consultar información fuera de `Q`.
- No se acepta una tasa promedio si una consulta crítica falla; los contratos
  críticos requieren coincidencia exacta.
- La procedencia es parte del dato representado, no una nota posterior.
- El número de consultas debe crecer con la tarea; seis consultas son sólo el
  fixture de 063.

## Métricas y gates

Registrar `query_preservation_rate`, `semantic_hallucination_rate`,
`unknown_escalation_rate`, `provenance_completeness` y, cuando la vista sea
editable, `round_trip_loss`.

Para una rama crítica se exige:

```text
QPR = 1
semantic_hallucination_rate = 0
unknown_escalation_rate = 0
provenance_completeness = 1
```

Si una vista edita la fuente, deberá añadir una operación reversible y evaluar
las leyes de round-trip antes de ser aceptada.

## Trade-off

Un contrato de consultas es más pequeño y auditable que intentar preservar todo,
pero puede omitir una pregunta que nadie declaró. La salida segura es versionar
`Q`, permitir `show_full` y tratar cualquier consulta no cubierta como
`UNKNOWN`, nunca como respuesta garantizada.

## Próximo gate

El siguiente desarrollo debe seleccionar ramas por cobertura semántica y costo
visual, no por un número fijo. Esa selección puede reutilizar la fuente de 063,
pero debe conservar las mismas consultas críticas después de elegir el subset.
