# Decisión 039 — CODE-INE usa oracle ejecutable antes de llamar `verified`

Fecha: 2026-08-24

## Evidencia

El experimento 029 proyectó la traza VIZZ a un contrato de cuatro campos y
ejecutó un oracle independiente de los scores. El kill test verificó además
que `objective_oracle.py` no contiene ni lee `objective_scores`.

| Estado | Casos |
|---|---:|
| `verified` | 3 |
| `conflict` | 2 |
| `unavailable` | 1 |
| `rejected` | 3 |

Las mutaciones de falla sostenida y recuperación produjeron `regressed` y
`recovered`; una acción incompatible produjo conflicto; el evento faltante
quedó no disponible; el ancla insuficiente, la mutación desconocida y el score
fuera de rango fueron rechazados. La transición base permaneció `c04 → c07`.

## Decisión

CODE-INE ya no tratará un mapa booleano declarado como la única forma de
oracle. Para el estado `verified` debe existir una especificación ejecutable,
un módulo separado del score, una procedencia explícita y kill tests que
detecten mutaciones. `verified` sigue significando solo coincidencia dentro
del fixture, no verdad de una tarea humana.

La biblioteca estándar local queda adoptada para el mutador explícito. `mutmut`
queda como candidato documentado, pero no se instala: su documentación exige
fork y ejecución en WSL, mientras que el laboratorio requiere una suite mínima
y portable en este entorno.

## Límite y siguiente paso

La especificación actual es una aceptación computacional declarada por el
laboratorio; no valida comprensión, ansiedad, sedación, intoxicación,
neurotransmisores ni experiencia subjetiva. La siguiente compuerta sería
definir un task outcome independiente y consensuado antes de cualquier sesión
humana, sin texto personal ni experimentación bajo intoxicación.
