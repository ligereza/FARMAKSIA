# Experimento 016 — CODE-INE como transición de sesión

Fecha: 2026-08-24

## Pregunta

¿Puede una traza abstracta de desarrollo distinguir actividad, mejora y entrada
en repetición sin convertir CODE-INE en un operador ni inferir un estado
neuroquímico?

## Contrato

La traza declara únicamente tiempo relativo, clase de acción, ganancia y
errores. El detector calcula:

`actividad → última mejora significativa → repetición`

La entrada en repetición exige que, después de la última mejora (`gain >= 0.2`),
una clase de acción vuelva a aparecer. Una señal de baja ganancia y errores sin
clase de acción solo puede llamarse proxy; no localiza la repetición. La deriva
respecto de un objetivo queda explícitamente no disponible porque la traza no
contiene una medida de objetivo o distancia.

CODE-INE aquí es un nombre de estado descriptivo y de política de registro,
no una API, operador independiente ni equivalente de codeína, sedación,
dopamina o cualquier neurotransmisor.

## Fixture y límites

La traza es sintética y controlada. No contiene commits, texto de usuario,
pantalla, teclado, intoxicación ni datos humanos. El experimento prueba la
frontera computacional del registro mínimo y no demuestra que una persona esté
en rush, sedada, ansiosa, comprendiendo menos o desviándose del objetivo.

## Kill tests

- Sin `action_class`, la repetición exacta debe quedar no disponible aunque
  sobreviva la señal de baja ganancia.
- Sin una señal de objetivo, la deriva debe permanecer no disponible.
- Una suma de actividad, ganancia y errores no puede ubicar el evento de
  entrada en repetición.
- El resultado no debe emitir etiquetas farmacológicas o neuroquímicas.

Ejecutar:

```text
python experiments/016-codeine-session-state/run_experiment.py
python experiments/016-codeine-session-state/run_kill_test.py
```
