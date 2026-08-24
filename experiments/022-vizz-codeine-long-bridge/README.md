# Experimento 022 — secuencia larga VIZZ → CODE-INE

Fecha: 2026-08-24

## Pregunta

¿La compuerta manual VIZZ puede representar una secuencia sintética de ocho
eventos y alimentar CODE-INE hasta localizar la transición `c04 → c07`, sin
escribir una sesión ni añadir captura?

## Diseño

La sesión declarada conserva los campos VIZZ permitidos y reproduce la
estructura de la traza CODE-INE 016: dos mejoras, mantenimiento y repetición.
El adaptador se ejecuta con `--consent --dry-run`; la salida debe indicar que no
se escribió ningún archivo. Después, el puente 020 normaliza los cinco campos
que CODE-INE necesita.

El resultado esperado es una capacidad del contrato de eventos:

`última mejora = c04; entrada en repetición = c07`

No es un resultado humano. Es un control de interoperabilidad para saber qué
podría medir una futura sesión manual.

## Kill tests

- La secuencia sin consentimiento debe bloquearse.
- La secuencia con `action_class` eliminado no puede producir entrada exacta en
  repetición.
- El dry-run debe dejar cero archivos creados.
- El resultado no puede afirmar datos humanos, farmacología ni deriva.

No se ejecuta una sesión real y no se incorpora corpus externo.

Ejecutar:

```text
python experiments/022-vizz-codeine-long-bridge/run_experiment.py
python experiments/022-vizz-codeine-long-bridge/run_kill_test.py
```
