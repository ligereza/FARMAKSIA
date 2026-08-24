# Experimento 012 — curvas, agujeros y capas

## Pregunta

¿Qué se pierde cuando KETAMINE conserva bounding boxes de curvas cerradas y
elimina los contornos o el orden de composición?

## Diseño

Se generan 20 escenas sintéticas con tres formas Bézier cerradas:

- una elipse sólida que contiene el punto consultado;
- un anillo con agujero que comparte el bounding box del punto, pero no lo
  contiene;
- una forma desplazada que no participa en la consulta.

El anillo tiene una capa superior. La consulta pide la forma visible en el
punto, por lo que geometría y orden de capa deben conservarse conjuntamente.

Se comparan fuente de curvas muestreada, tabla de vértices, grafo de bounding
boxes y relación visible precalculada.

## Kill tests

- Si la tabla de vértices no conserva la forma visible, la aproximación está
  mal definida.
- Si el grafo de bounding boxes devuelve el anillo como visible, el agujero es
  residuo perdido y la generalización geométrica falla.
- Si se pierde la capa pero se conserva la forma, la visibilidad aún puede
  cambiar; composición y geometría son invariantes separados.

Los casos son sintéticos y no constituyen corpus creativo.
