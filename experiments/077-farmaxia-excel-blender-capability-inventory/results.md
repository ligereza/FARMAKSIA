# Resultados — experimento 077

## Evidencia observada

La ejecución local debe producir dos observaciones independientes:

1. Excel respondió mediante COM como versión `16.0`, build `20326.0`, con cero
   libros adjuntos. Su objeto de aplicación reportó miembros para libros,
   hojas, rangos, evaluación de fórmulas, gráficos y nombres. Hojas, gráficos,
   nombres, cachés y conexiones no deben interpretarse como capacidades
   documentales observadas hasta abrir un libro de prueba controlado.
2. Blender 5.1.1 respondió en modo background mediante su API Python y expuso
   contexto, objetos, colecciones, materiales, escenas, árboles de nodos,
   sockets, dependency graph y operaciones de undo/redo. La disponibilidad del
   módulo GPU también fue observada.

Los valores concretos de versión pertenecen a la máquina y no se convierten en
un benchmark universal.

## Interpretación

Esto cambia el diseño de FARMAKSIA: UIA es una capa de superficie, pero el
ensamblaje semántico necesita adaptadores de estado nativos. Excel ofrece un
grafo de valores y dependencias; Blender ofrece un grafo de escena, nodos y
evaluación. El puente común debe trabajar con transiciones tipadas, no con
coordenadas ni coincidencia de botones.

La observación es más fuerte para Blender que para Excel: Blender fue
consultado con una sesión de fábrica sin datos; Excel fue adjuntado sin libro.
Por tanto, todavía no hemos observado una celda real ni una escena real y no
debemos afirmar que sus transiciones ya son equivalentes.

## Desconocido

- qué eventos mínimos permiten observar una transición sin capturar contenido
  privado;
- si una selección en Excel y una selección en Blender comparten suficiente
  semántica para una tarea concreta;
- cómo verificar una modificación futura sin que el verificador dependa de la
  misma fuente que produjo la acción;
- qué parte del viewport de Blender queda fuera de UIA y exige la API nativa.
