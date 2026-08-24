# Experimento 018 — control de reformulación para X-ANA-X

Fecha: 2026-08-24

## Pregunta

Aplicada a un problema real pequeño del repositorio —la compuerta de fallo de
`research/tools/run_suite.py`—, ¿la ruta X-ANA-X produce una decisión que no
produce una lectura directa/reformulación del mismo código?

## Diseño

Se comparan dos rutas con la misma entrada:

1. **Reformulación directa:** inspecciona el AST y pregunta qué protege el
   marcador final `SUITE_VALID`.
2. **X-ANA-X:** selecciona la fuente declarada `gated-pipeline`, mapea
   `stage → gate → stop-on-failure → release marker` y predice la misma
   condición.

La prueba no premia que la analogía use palabras distintas. Solo hay ganancia
si cambia una decisión verificable o revela un residuo que la ruta directa no
puede obtener.

## Límites

El análisis es estático y se limita al wrapper reutilizable `command()` y a la
presencia de guardas de retorno. No demuestra que cada posible futura edición
de la suite mantenga la propiedad, ni demuestra que una persona comprenda
mejor el código mediante una analogía. No hay red, corpus, modelo generativo ni
datos humanos.

## Kill tests

- Una modificación adversarial del comparador `!=` a `==` debe eliminar la
  guarda detectada.
- Quitar `SUITE_VALID` debe eliminar el marcador terminal.
- Si ambas rutas producen los mismos hechos y decisión, X-ANA-X no puede
  reclamar novedad en este problema.

Ejecutar:

```text
python experiments/018-xanax-reformulation-control/run_experiment.py
python experiments/018-xanax-reformulation-control/run_kill_test.py
```
