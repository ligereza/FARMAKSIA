# Resultados — experimento 029

El oracle ejecutable leyó únicamente la traza mutada y la especificación; el
kill test confirmó que no contiene una referencia a `objective_scores`. La
matriz produjo:

| Estado | Casos |
|---|---:|
| `verified` | 3 |
| `conflict` | 2 |
| `unavailable` | 1 |
| `rejected` | 3 |

Las mutaciones de falla sostenida y recuperación cambiaron el oracle a
`regressed` y `recovered`, respectivamente. Una mutación de acción incompatible
generó conflicto con el score estable. El evento faltante quedó no disponible;
la ganancia insuficiente del ancla, la mutación desconocida y el score fuera de
rango fueron rechazados.

La transición base permaneció `c04 → c07`. El resultado fortalece la separación
entre señal declarada y aceptación computable, pero sigue siendo evidencia del
fixture: no demuestra que la especificación sea una tarea humana válida ni que
la deriva objetiva corresponda a sedación, ansiedad, intoxicación,
neurotransmisores o experiencia subjetiva.
