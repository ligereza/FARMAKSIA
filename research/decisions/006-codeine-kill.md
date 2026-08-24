# Decisión 006 — matar la formulación estrecha de CODE-INE

Fecha: 2026-08-23

## Resultado

La formulación experimental `gain/cost + threshold` queda eliminada como
operador teórico independiente.

El kill test mostró que:

- reproduce un controlador de valor de computación en 4 de 5 escenarios;
- coincide con prioridad dinámica cuando el stopping no interviene;
- pierde frente a valor neto esperado en el escenario de costos desiguales.

## Decisión conceptual

No conservaré CODE-INE como nombre de una heurística de ratio. Esa idea ya está
contenida en familias conocidas de prioridad, bandits y metarazonamiento, y la
versión ensayada no es siquiera óptima bajo la utilidad declarada.

La pregunta más amplia queda en estado **abierto, no implementable**:

> ¿Existe una política de continuación específica para prácticas creativas que
> modele simultáneamente autoridad humana, irreversibilidad, reutilización de
> artefactos, cambio de representación y valor de opciones futuras?

Si esa pregunta no produce una diferencia medible frente a metarazonamiento
existente, CODE-INE será eliminado por completo o absorbido como vocabulario de
dominio.

## Próxima dirección

Abrir el ciclo VIZZ y probar si la visualización modifica decisiones humanas,
en lugar de continuar refinando una formulación ya falsada de CODE-INE.
