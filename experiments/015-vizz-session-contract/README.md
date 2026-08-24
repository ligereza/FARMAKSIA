# Experimento 015 — contrato seguro de instrumentación VIZZ

Fecha: 2026-08-24

## Pregunta

¿Puede una sesión VIZZ producir eventos de tarea suficientes para repetir la
consulta 014 sin capturar pantalla, teclado, cámara, audio, URLs ni contenido
personal por defecto?

## Contrato mínimo

El envelope declara explícitamente `consent`, `capture` y `events`.

- El estado por defecto es `enabled=false`, `granted=false`, `scope=none` y
  cero eventos.
- La activación exige consentimiento y el único alcance admitido es
  `task_events_only`.
- Los eventos solo contienen tiempo relativo, clase de acción, fase, ganancia,
  errores, objetivo abstracto y condición declarada de display.
- Se rechazan campos o fuentes de captura de pantalla, teclado, cámara, audio,
  URLs, texto libre, archivos, coordenadas de mirada y vídeo.
- El runner valida sintaxis, orden temporal, identificadores únicos, límites y
  ausencia de esos campos; no inicia ningún dispositivo ni recopila una sesión.

## Fixture y límites

Los tres casos incluidos son fixtures sintéticos: estado seguro por defecto,
opt-in con eventos abstractos y un caso adversarial con texto crudo. No son
datos humanos. La validación demuestra una frontera de entrada, no que el
registro sea suficiente para inferir percepción, fatiga, ansiedad,
neurotransmisores o comprensión.

## Kill tests

- El envelope desactivado no puede contener eventos.
- El opt-in no puede ampliar el alcance ni introducir captura cruda.
- Un campo adversarial (`text`) debe ser rechazado sin imprimir su contenido.
- La suite no debe necesitar WebGazer, Pupil Core, PsychoPy, webcam ni red.

Ejecutar:

```text
python experiments/015-vizz-session-contract/run_experiment.py
python experiments/015-vizz-session-contract/run_kill_test.py
```
