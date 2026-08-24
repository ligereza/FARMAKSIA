# Decisión 011 — compuerta de adopción de herramientas

Fecha: 2026-08-23

## Sondeo del entorno

El ciclo 013 se ejecutó con Python estándar para mantener un control legible y
reemplazable. El entorno tiene `numpy`, Node.js `v24.15.0` y FFmpeg `9.0`; no
están disponibles DuckDB, PyArrow, pandas, NetworkX ni RDFLib.

## Decisión

No se instala ni se adopta una dependencia nueva en este ciclo. La medición
actual cabe en fixtures pequeños y no necesita SQL, formato columnar, grafos
externos ni procesamiento audiovisual. Añadir una biblioteca ahora ocultaría
qué parte de la evidencia proviene del modelo y cuál del sistema.

Node.js permanece adoptado solo como verificador sintáctico del piloto VIZZ.
FFmpeg queda diferido: su adopción requiere primero un fixture audiovisual y
una consulta que mida transcodificación, extracción temporal o pérdida de
representación.

## Umbrales para reabrir la decisión

- Adoptar DuckDB si el workload necesita consultas relacionales sobre un corpus
  que ya no sea razonable medir con estructuras estándar.
- Adoptar PyArrow si la pregunta pasa a ser costo de representación columnar,
  intercambio o serialización entre procesos.
- Adoptar OpenImageIO o FFmpeg solo con un corpus raster/video real y un kill
  test de pérdida o reversibilidad.
- Adoptar Vega-Lite o Cytoscape.js solo cuando VIZZ tenga una condición humana
  que necesite comparar una vista interactiva con su control estático.

La instalación de una herramienta no contará como avance por sí sola: debe
mejorar una medición, declarar versión/licencia, conservar exportación y dejar
un reemplazo mínimo.
