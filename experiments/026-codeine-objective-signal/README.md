# Experimento 026 — CODE-INE y señal de objetivo declarada

## Pregunta

¿Puede CODE-INE distinguir una traza estable, regresada o recuperada respecto
de un objetivo sin inventar deriva cuando la señal de objetivo falta o es
inválida?

## Diseño

Se reutiliza la sesión sintética VIZZ 022, que mantiene la transición base
`c04 → c07`. Se añaden perfiles de `objective_score` por evento:

- `stable`: la puntuación posterior conserva el nivel de `c04`;
- `regressed`: desciende más que la tolerancia declarada;
- `recovered`: desciende y luego vuelve al nivel de referencia;
- `no_objective` y `missing_tail_score`: la señal no está disponible;
- `out_of_range`: la señal viola el contrato y se rechaza.

La señal es un fixture declarado, no una medición humana ni una verdad externa.
La transición base se reporta separada de la relación con objetivo.

## Kill tests

- Los perfiles con objetivo no pueden cambiar artificialmente la transición
  base `c04 → c07`.
- Sin score completo, `drift` debe ser `unavailable`.
- Un score fuera de `[0, 1]` debe ser rechazado.
- `regressed` y `recovered` deben depender de la regla declarada, no de la
  cantidad de actividad.
- No se emiten etiquetas farmacológicas, neuroquímicas o humanas.

Esto demuestra una compuerta computacional de objetivo; no demuestra deriva
subjetiva, comprensión, ansiedad, intoxicación ni carga cognitiva.

Ejecutar:

```text
python experiments/026-codeine-objective-signal/run_experiment.py
python experiments/026-codeine-objective-signal/run_kill_test.py
```
