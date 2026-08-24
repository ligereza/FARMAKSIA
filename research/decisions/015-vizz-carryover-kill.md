# Decisión 015 — kill test de arrastre en VIZZ

Fecha: 2026-08-23

## Evidencia

`audit_pilot_design.py` encuentra una sola firma de estado en tabla, vista
estática y VIZZ. El piloto aleatoriza el orden de las condiciones, pero no
aleatoriza ni cambia el estímulo: la misma persona ve el mismo problema tres
veces.

## Decisión

El instrumento conserva valor para verificar paridad, accesibilidad,
procedencia y autoridad humana, pero no está aprobado para inferencia causal
sobre una mejora de VIZZ. El riesgo de arrastre es alto y la suite lo reporta
como condición explícita.

No se recogen ni se interpretan datos humanos con la versión actual.

## Corrección requerida

Crear al menos tres conjuntos de estímulos con la misma regla analítica y
estructura de tarea, pero valores/evidencia distintos. Cada participante debe
ver cada condición una vez y cada conjunto una vez, con una asignación
balanceada que permita separar condición, conjunto y orden. El exportado debe
registrar ambos identificadores y el análisis debe incluir el efecto de
conjunto.

## Residuo

La paridad de información actual está demostrada solo para un fixture. El
efecto humano de VIZZ, la percepción de incertidumbre y la autoridad sobre la
decisión siguen desconocidos. Este kill test no mata VIZZ como concepto; mata
la interpretación causal del piloto actual.
