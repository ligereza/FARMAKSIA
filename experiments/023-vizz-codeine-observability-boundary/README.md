# Experimento 023 — frontera de observabilidad VIZZ → CODE-INE

## Pregunta

¿El puente VIZZ → CODE-INE distingue una transición realmente observable de
una entrada estructuralmente inválida o de una sesión formalmente válida pero
semánticamente incompleta?

## Motivación

El experimento 022 demuestra que un fixture sintético completo puede expresar
`c04 → c07`. No demuestra que una captura parcial, una etiqueta alterada o una
ganancia mal declarada deban producir la misma lectura. Un contrato cerrado
puede rechazar campos ausentes y aun así aceptar una secuencia cuya semántica
ya no está garantizada.

La distinción es importante para VIZZ: una vista focalizada, una actualización
con latencia o una captura manual incompleta no deben convertirse
silenciosamente en una afirmación de CODE-INE.

## Diseño

Se reutiliza el fixture sintético 022 y se aplican mutaciones declaradas:

- `baseline`: secuencia completa;
- `missing_action_class`, `non_monotonic_time`, `duplicate_event_id`:
  defectos estructurales que deben rechazarse;
- `remove_anchor`, `change_anchor_gain`, `relabel_repetition`:
  mutaciones semánticas que todavía cumplen el envelope VIZZ, pero cambian la
  transición calculada.

La clasificación es conservadora:

- `available`: la transición coincide exactamente con el baseline;
- `rejected`: la validación VIZZ o el puente bloquea la entrada;
- `ambiguous`: la entrada pasa la forma, pero ya no conserva la misma
  transición y no puede interpretarse como equivalente.

## Kill tests

- Ninguna mutación estructural puede cruzar el puente.
- Ninguna mutación semántica puede conservar silenciosamente la etiqueta
  `available`.
- El baseline debe conservar `última mejora = c04` y `entrada en repetición =
  c07`.
- El runner no inicia dispositivos, no usa red, no escribe sesiones y no
  contiene datos humanos.

Esto es una auditoría de observabilidad computacional. No mide mirada,
latencia perceptual, comodidad, comprensión, ansiedad, intoxicación ni
neurotransmisores.

Ejecutar:

```text
python experiments/023-vizz-codeine-observability-boundary/run_experiment.py
python experiments/023-vizz-codeine-observability-boundary/run_kill_test.py
```
