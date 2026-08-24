# Kill test 002 — CODE-INE frente a controladores dinámicos

Fecha: 2026-08-23

## Baselines

Se conservaron las mismas acciones, costos y ganancias esperadas de los cuatro
escenarios originales y se añadió `cost-shape-adversary`.

- `dynamic-priority`: puede elegir cualquier acción, pero siempre consume la
  mejor razón ganancia/costo disponible.
- `value-of-computation`: puede elegir cualquier acción y detiene cuando la
  ganancia esperada neta (`gain - 0.1 × cost`) deja de ser positiva.
- `continuation-candidate`: política original de razón ganancia/costo con
  umbral `0.1`.

## Resultado

| Escenario | Coincide con dynamic-priority | Coincide con value-of-computation | Utilidad candidata | Mejor control |
|---|---|---|---:|---:|
| deep-path | Sí | Sí | 0.44 | 0.44 |
| dead-end | Sí | Sí | 0.60 | 0.60 |
| reuse-credit | Sí | Sí | 0.68 | 0.68 |
| stop-now | No | Sí | 0.85 | 0.85 |
| cost-shape-adversary | Sí | No | 0.30 | 0.40 |

En `cost-shape-adversary`, la candidata elige `option_A` porque su ratio es
`0.30`, aunque `option_B` produce mayor utilidad neta esperada (`0.20` frente a
`0.10`). La diferencia es una debilidad de la heurística, no evidencia de una
nueva teoría.

## Falsación

La formulación actual de CODE-INE como “maximizar ganancia/costo y detener bajo
un umbral” queda falsada como operador independiente:

1. En cuatro escenarios reproduce un controlador de valor de computación.
2. En el escenario adversarial es inferior a ese controlador.
3. En todos los casos coincide con una prioridad dinámica cuando no aplica
   stopping.

## Qué queda vivo

No se elimina la pregunta general sobre políticas de continuación en flujos
creativos. Se elimina esta definición estrecha. Para sobrevivir, una futura
formulación tendría que aportar algo que no esté en valor de computación,
optimal stopping, bandits o metarazonamiento: por ejemplo, autoridad humana,
irreversibilidad, reutilización de artefactos y cambio de representación como
opciones de trayectoria medibles.
