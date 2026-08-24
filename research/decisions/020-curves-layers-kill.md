# Decisión 020 — curvas y capas amplían el residuo de KETAMINE

Fecha: 2026-08-23

## Evidencia

El experimento 012 comparó curvas Bézier cerradas, un anillo con agujero y
capas sobre 20 escenas sintéticas. La tabla de contornos conservó la forma
visible en `20/20`; el grafo de bounding boxes coincidió en `0/20` y produjo
falsos positivos en `20/20`. La relación visible precalculada coincidió en
`20/20`.

## Decisión

KETAMINE debe distinguir al menos:

- contornos y aproximación geométrica;
- regla de relleno y agujeros;
- estilos y metadata;
- orden/capa de composición;
- relaciones visibles ya materializadas.

Un bounding box no preserva visibilidad de curvas con agujeros. Un grafo puede
responder una relación ya precalculada, pero no reconstruir una consulta nueva.
Esto debilita aún más la novedad conceptual frente a representaciones
geométricas y caches conocidos.

## Alcance

El resultado es sintético y usa curvas Bézier de tipo elipse. El próximo
ingreso relevante debe ser una obra autorizada o un SVG real con paths, capas y
metadata; no se implementará API por este resultado.
