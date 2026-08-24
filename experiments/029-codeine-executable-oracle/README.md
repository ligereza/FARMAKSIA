# Experimento 029 — oracle ejecutable y mutación CODE-INE

## Pregunta

¿Un oracle ejecutable basado en una especificación separada detecta mutaciones
de la tarea CODE-INE y evita llamar `verified` a un score que contradice el
resultado del task?

## Diseño

La sesión sintética VIZZ 022 se normaliza y conserva la transición base
`c04 → c07`. Un módulo independiente (`objective_oracle.py`) recibe los
eventos y `oracle_spec.json`; nunca lee `objective_scores`.

Los perfiles mutan solo el fixture de eventos o el score declarado:

- traza de referencia estable;
- falla sostenida después del ancla;
- falla seguida de recuperación;
- acción incompatible;
- ancla con ganancia insuficiente;
- evento faltante;
- mutación desconocida;
- score fuera de rango.

El resultado es `verified` solo cuando score y oracle ejecutable coinciden;
`conflict` cuando discrepan; `unavailable` cuando faltan eventos; y `rejected`
cuando la especificación, la mutación o el score son inválidos.

## Kill tests

- El oracle no puede leer ni derivar su resultado desde el score.
- Las mutaciones de error, recuperación y acción deben cambiar el resultado
  del oracle de forma observable.
- Un conflicto no puede producir `verified`.
- Un evento faltante, una mutación desconocida o un score inválido no pueden
  cruzar la compuerta.
- La transición base debe conservar `c04 → c07`.
- No hay datos humanos, red, dispositivos ni inferencia farmacológica.

Ejecutar:

```text
python experiments/029-codeine-executable-oracle/run_experiment.py
python experiments/029-codeine-executable-oracle/run_kill_test.py
```
