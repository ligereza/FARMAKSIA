# Experimento 020 — puente VIZZ → CODE-INE

Fecha: 2026-08-24

## Pregunta

¿El envelope opt-in de VIZZ puede alimentar el detector de transición CODE-INE
sin duplicar captura ni introducir campos crudos?

## Contrato

El puente consume únicamente `event_id`, `t_ms`, `action_class`, `gain` y
`errors`, que son suficientes para la validación y clasificación mínima de
CODE-INE. Conserva la procedencia del envelope VIZZ y declara los campos VIZZ
que no pasan al detector. No convierte `display_condition`, `phase` u
`objective_id` en una inferencia humana.

La muestra opt-in contiene tres eventos: `s02` es la última mejora
significativa y `s03` es el único evento posterior. Por eso el puente debe
devolver repetición no disponible, no inventar una transición.

## Kill tests

- El estado seguro por defecto no puede alimentar un detector con cero eventos.
- Si se elimina `action_class`, VIZZ puede aceptar el envelope, pero el puente
  debe rechazarlo porque CODE-INE perdería la variable de repetición.
- El puente no puede iniciar dispositivos, red o captura cruda.

El experimento es una prueba de interoperabilidad computacional sobre fixtures
sintéticos, no una sesión humana ni una medición neurobiológica.

Ejecutar:

```text
python experiments/020-vizz-codeine-event-bridge/run_experiment.py
python experiments/020-vizz-codeine-event-bridge/run_kill_test.py
```
