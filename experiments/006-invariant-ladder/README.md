# Experimento 006 — escalera de invariantes

## Pregunta

¿El beneficio atribuido a KETAMINE depende solamente de materializar datos,
índices o relaciones conocidas, o aparece una capacidad adicional cuando se
varía de forma controlada el residuo de la representación?

## Diseño

Se reutiliza el SVG del experimento 001 y se comparan siete representaciones:

- `source`: estructura completa consultada como baseline.
- `geometry-table`: coordenadas y dimensiones; pierde estilo, tags y sintaxis
  SVG.
- `attribute-table`: añade estilo y tag al registro geométrico.
- `indexed-table`: la misma tabla con índices materializados para consultas
  repetidas; es un control explícito de vista/índice conocido.
- `relation-graph`: conserva relaciones precalculadas, pero pierde geometría.
- `attributed-graph`: conserva relaciones y bounding boxes, pero no estilo ni
  tags; permite probar cuánto basta una geometría resumida.
- `temporal-state`: tabla con intervalos derivados de `events.json`; se marca
  como salida con entrada externa, no como conversión pura.

## Consultas y mediciones

Las consultas cubren intersección espacial, área, estilo, tag, relación
precalculada y estado temporal. Se registra capacidad (`available` o
`unavailable`), respuestas, unidades de trabajo, preparación, tamaño
serializado, residuo y workloads repetidos.

## Kill tests

- Si `indexed-table` explica todo el crédito de `KETAMINE`, el fenómeno se
  clasifica como índice/vista materializada, no como novedad.
- Si `attributed-graph` responde todas las consultas geométricas del baseline,
  la hipótesis de que el grafo exige geometría continua queda debilitada.
- Si las diferencias desaparecen al incluir la preparación y el residuo, el
  crédito era solo de consulta y no de representación.

No se implementa una API de operadores ni se usa una base de datos externa.
