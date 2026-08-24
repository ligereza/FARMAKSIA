# Auditoría metodológica del piloto VIZZ

Fecha: 2026-08-23

## Hallazgo

Las condiciones tabla, estática y VIZZ comparten una única firma de estado y
el piloto presenta las tres condiciones a la misma persona. El orden se
aleatoriza, pero la identidad del estímulo no cambia.

Esto crea riesgo de arrastre: una persona puede recordar valores, evidencia o
la acción elegida en una condición anterior. Una diferencia en la tercera
condición no podría atribuirse únicamente a la representación.

`audit_pilot_design.py` informa:

```text
CARRYOVER_RISK=high
RECOMMENDATION=counterbalance_distinct_trial_sets_before_causal_inference
```

## Kill test

El piloto actual no debe producir una afirmación causal de que VIZZ mejora la
decisión. Si se analizara como comparación causal sin controlar aprendizaje,
el diseño quedaría invalidado por confusión entre condición y exposición.

## Corrección requerida

Preparar al menos tres conjuntos de prueba con la misma tarea y regla
analítica, pero con estados numéricos y evidencia distintos. Asignar condición
y conjunto mediante un cuadrado latino o una asignación balanceada; registrar
ambos factores y analizar el efecto de conjunto junto al efecto de condición.

La paridad debe verificarse dentro de cada conjunto, no solo con una firma
global. Hasta completar esa corrección, VIZZ queda instrumentado pero no listo
para inferencia humana causal.
