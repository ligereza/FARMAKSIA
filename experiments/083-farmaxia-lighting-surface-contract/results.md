# Resultados 083 — contrato de superficie grandMA3 → Titan

**Fecha de ejecución:** 2026-08-27
**Estado:** `LIGHTING_SURFACE_CONTRACT_VERIFIED`

## Evidencia obtenida

- el contrato cubre cinco tareas canónicas;
- `fixture_selection` y `attribute_control` se mantienen como compatibles a
  nivel de tarea;
- `reusable_value`, `cue_sequence` y `playback_control` quedan como `partial`;
- las cinco transformaciones normalizadas regresan a su origen con error menor
  o igual a `1e-12`;
- las regiones de destino no se solapan;
- la capacidad de ejecución queda bloqueada;
- no hubo red, input inyectado, escritura de fuente ni superficies observadas.

## Decisión

El contrato es suficientemente preciso para alimentar un renderer de preview,
pero todavía no es un adaptador de producción. La próxima evidencia debe venir
de UIA/captura de grandMA3 onPC y Titan Simulator en las versiones concretas.
No se puede aceptar un mapa basado sólo en texto, posición o analogía de
  vocabulario.
## Desconocidos

- qué roles y rectángulos expone grandMA3 onPC por UIA;
- qué roles y rectángulos expone Titan Simulator por UIA;
- cómo cambian las superficies al abrir layouts, ventanas o showfiles;
- si un operador familiarizado con Titan localiza más rápido las tareas;
- si alguna función avanzada requiere `PARTIAL` o `UNSUPPORTED`.
