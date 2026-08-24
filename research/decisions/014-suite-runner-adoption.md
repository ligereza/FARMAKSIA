# Decisión 014 — adopción del arnés de suite

Fecha: 2026-08-23

## Herramienta

`research/tools/run_suite.py`, construido con Python estándar (`3.13.15`),
ejecuta compilación, validación del manifiesto de corpus, experimentos, kill
tests, generación/verificación del piloto VIZZ y validación de procedencia.
Comprueba también invariantes mínimos de los resultados de los experimentos
007 y 008. El validador de corpus permanece deliberadamente en cero entradas
hasta que exista autoridad real.

## Evidencia

La ejecución completa terminó con `SUITE_VALID` y validó ocho manifiestos de
procedencia. Al regenerar VIZZ, el piloto y sus hashes permanecen coherentes;
la suite evita que el generador vuelva a divergir del artefacto que se entrega
a participantes.

## Decisión de adopción

Se adoptan como herramientas internas del laboratorio el runner y el validador
de manifiesto. Cumplen la compuerta:

- resuelve una operación concreta: repetición y regresión del ciclo;
- no agrega dependencias externas ni arquitectura;
- expone comandos y errores;
- puede reemplazarse por ejecución manual o por otro runner;
- mejora la medición de reproducibilidad y evita conclusiones sobre una suite
  incompleta.

No se adopta todavía DuckDB, PyArrow, Vega-Lite, Cytoscape.js, OpenImageIO ni
FFmpeg: el corpus real y sus workloads aún no justifican esas dependencias.
