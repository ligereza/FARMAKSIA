# Decisión 001 — herramientas del baseline

Fecha: 2026-08-23

## Capacidades locales verificadas

- Python 3.13.15.
- NumPy 2.5.2.
- FFmpeg 9.0.
- Git.
- Node.js 24.15.0.

No están disponibles localmente, por ahora, Pillow, NetworkX, DuckDB,
PyArrow, Matplotlib, CairoSVG ni OpenImageIO.

## Adopción provisional

Se adoptan para el primer experimento:

1. Python estándar para leer XML/SVG y registrar mediciones.
2. NumPy únicamente para cálculos geométricos numéricos, si hacen falta.
3. Git como registro de cambios y reproducibilidad.

FFmpeg queda adoptado solo para el futuro experimento de video/playback; no se
introduce en el experimento SVG porque no interviene en la pregunta.

## Motivo

El experimento debe aislar la frontera entre cambio de representación y cambio
del espacio del problema. Instalar un parser o una base de datos ahora podría
ocultar esa frontera bajo una dependencia. El baseline será deliberadamente
pequeño y reemplazable.

## No-adopción todavía

- DuckDB: útil cuando exista una carga de consultas que medir.
- PyArrow: útil para comparar memoria/intercambio, no necesario para el primer
  objeto geométrico.
- NetworkX/Cytoscape.js: útiles después de demostrar que el grafo responde una
  consulta nueva.
- OpenImageIO: útil para imágenes grandes y formatos heterogéneos.
- Vega-Lite: útil para el experimento VIZZ, después de definir la decisión
  humana que debe mejorar.

## Criterio de reversión

Si el baseline estándar no puede expresar la consulta o registrar la pérdida,
se incorporará una sola dependencia adicional y se repetirá el experimento.
La adopción se registrará aquí antes de modificar el entorno.
