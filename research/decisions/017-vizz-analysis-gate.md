# Decisión 017 — compuerta de análisis VIZZ multi-sesión

Fecha: 2026-08-23

## Herramienta adoptada

`experiments/009-vizz-counterbalanced/aggregate_pilot.py` valida varias
exportaciones VIZZ 0.2 antes de agregarlas. Rechaza participantes anónimos o
duplicados, sesiones incompletas, firmas incorrectas y asignaciones inválidas.
Reporta balance, métricas por condición y diferencias pareadas frente a la
vista estática.

## Límites deliberados

La salida siempre marca `inference_status=DESCRIPTIVE_ONLY`; no calcula
significancia, no interpreta valor artístico y no convierte una muestra
pequeña en evidencia causal. El análisis sin archivos produce
`NO_HUMAN_DATA`.

## Decisión

Se adopta como guardia de ingestión y análisis descriptivo. Cualquier análisis
inferencial posterior necesitará una decisión metodológica separada, datos
identificables de forma controlada, balance real entre participantes y revisión
humana de las explicaciones.
