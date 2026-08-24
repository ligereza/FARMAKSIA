# Experimento 011 — frontera no rectangular de KETAMINE

## Pregunta

¿Un grafo que conserva bounding boxes preserva una consulta geométrica exacta
cuando la representación contiene polígonos no rectangulares?

## Diseño

Se generan 20 casos con tres polígonos por caso: uno que contiene el punto de
consulta, uno cuyo bounding box lo contiene pero cuya forma no, y uno
disjunto. Se comparan:

- geometría completa y tabla de vértices;
- grafo de bounding boxes;
- grafo de relaciones exactas precalculadas.

La consulta `contains_point` usa point-in-polygon; también se consulta estilo y
la relación exacta precalculada.

## Kill test

- Si la tabla de vértices no coincide con la geometría fuente, la medición
  exacta está rota.
- Si el grafo de bounding boxes coincide siempre, el residuo geométrico no
  importa para este dominio.
- Si aparece un falso positivo, queda demostrado que el bounding box no
  preserva la consulta exacta y que el resultado anterior de bounding boxes era
  específico de rectángulos.

El fixture es sintético y no representa una obra creativa.
