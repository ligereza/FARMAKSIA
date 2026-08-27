# Resultados — experimento 078

## Evidencia local

La ejecución verificada usa Excel `16.0` mediante COM y Blender `5.1.1` en
modo background. En Excel se observó el cálculo `2 + 3 = 5` dentro de un libro
efímero y, después de limpiar el rango, cero celdas no vacías. En Blender se
observó la creación de un objeto temporal, su selección como objeto activo, el
cambio de `location.x` a `2.0` y el retorno al conteo inicial de objetos tras
eliminarlo.

Los valores anteriores son evidencia de ejecución de laboratorio, no datos de
usuario ni benchmark de rendimiento.

## Resultado conceptual

La unidad de traducción más prometedora es la transición tipada. Excel aporta
un grafo de valores y fórmulas; Blender aporta un grafo de objetos y propiedades.
El primer kernel común es `create`, `select`, `modify`, `revert`. El input humano
debe alimentar ese kernel después, una vez que se pueda observar con seguridad
qué estado cambió.

## Límites

- Las transiciones fueron controladas por las APIs nativas, no por una persona.
- No se ha demostrado todavía que UIA pueda identificar de forma suficiente el
  target semántico dentro del viewport de Blender.
- No se ha implementado una traducción automática ni una acción en la aplicación
  del usuario.
- La reversión del scratch no prueba por sí sola que una acción real de usuario
  sea siempre reversible.
