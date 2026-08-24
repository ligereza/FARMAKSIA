# Resultados 002 — CODE-INE frente a scheduling

Fecha: 2026-08-23

## Ejecución

Se ejecutó `run_experiment.py` con Python 3.13.15 y biblioteca estándar.
Los tres controladores recibieron los mismos costos y ganancias esperadas.
`FIFO` y `priority` solo pudieron operar sobre `static_queue`; la política
candidata además pudo cambiar de rama, reutilizar y detenerse.

La utilidad fue:

`quality final - 0.1 × costo consumido`

| Escenario | FIFO | priority | continuation-candidate | Acción distintiva |
|---|---:|---:|---:|---|
| deep-path | 0.44 | 0.44 | 0.44 | ninguna; continuar era correcto |
| dead-end | 0.20 | 0.36 | 0.60 | `switch_B → reuse` |
| reuse-credit | 0.38 | 0.64 | 0.68 | `reuse → switch_B` |
| stop-now | 0.77 | 0.84 | 0.85 | detenerse sin consumir presupuesto |

Promedios sobre los cuatro escenarios:

- FIFO: utilidad `0.4475`, costo `1.25`;
- priority: utilidad `0.5700`, costo `0.65`;
- continuation-candidate: utilidad `0.6425`, costo `1.00`.

## Qué demuestra

El resultado no prueba novedad teórica, pero sí una diferencia operacional
frente a un scheduler de orden:

- en `dead-end`, la candidata cambia la trayectoria y alcanza calidad `0.70`;
- en `reuse-credit`, reutiliza y luego cambia de rama;
- en `stop-now`, detiene el proceso por valor esperado bajo el umbral;
- en `deep-path`, coincide con los schedulers porque continuar era la decisión
  correcta.

La coincidencia en `deep-path` es importante: la candidata no gana por
definición en todos los casos.

## Límite de la evidencia

El escenario es pequeño, determinista y sus ganancias esperadas fueron
declaradas manualmente. Además, `switch_B` no pertenece a la cola estática.
Esto demuestra la frontera entre reordenar una cola y modificar la trayectoria,
pero todavía no compara contra un scheduler dinámico que pueda crear tareas.

## Decisión provisional

CODE-INE sobrevive como candidato operacional solo si su dominio incluye:

- acciones semánticas de continuar, cambiar, reutilizar y detener;
- estado observable del proceso;
- costos y valor esperado;
- posibilidad de modificar la trayectoria;
- autoridad para conservar o descartar presupuesto.

No sobrevive como teoría nueva todavía. Su comportamiento está muy cerca de
metarazonamiento, optimal stopping y algorithm selection.

## Próximo kill test

Comparar la candidata contra un controlador de valor de computación y un
scheduler dinámico que pueda generar `switch_B`. Si ambos reproducen las mismas
decisiones y utilidad, CODE-INE debe absorberse en metarazonamiento existente.
