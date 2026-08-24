# Resultados — experimento 023

El baseline sintético conserva la transición:

`última mejora = c04 → entrada en repetición = c07`

Las tres mutaciones estructurales fueron rechazadas: campo `action_class`
ausente, tiempo no monótono e identificador duplicado. Las tres mutaciones
semánticas pasaron el envelope VIZZ, pero cambiaron la transición calculada;
por ello se clasificaron como `ambiguous`, no como equivalentes disponibles.

| Caso | Resultado |
|---|---|
| baseline | `available` |
| campo de acción ausente | `rejected` |
| tiempo no monótono | `rejected` |
| identificador duplicado | `rejected` |
| ancla `c04` eliminada | `ambiguous` |
| ganancia de `c04` reducida | `ambiguous` |
| `c07` reclasificado como `build` | `ambiguous` |

El resultado descubre un límite importante: la forma del evento no demuestra
que la etiqueta de ganancia o de acción sea verdadera. CODE-INE no debe elevar
una secuencia manual formalmente válida a estado humano sin una fuente de
objetivo, cobertura y revisión explícitas.

No hubo participantes, cámara, mirada, red, escritura de sesión ni inferencia
farmacológica.
