# Experimento 005 — composición X-ANA-X / KETAMINE

## Pregunta

¿Conmutan una transformación de representación y una reformulación que añade
un observable temporal?

La notación `A_after_B` significa aplicar primero `B` y después `A`.

## Operadores experimentales

### KETAMINE-table

Transforma el SVG en una tabla que conserva geometría suficiente para
recalcular intersecciones. Pierde estilos y tags originales, pero no la
geometría usada por el experimento.

### KETAMINE-graph

Transforma el SVG en un grafo de relaciones precalculadas. Conserva IDs y
relaciones, pero pierde coordenadas; es deliberadamente un caso lossy.

### X-ANA-X-temporal-intersection

Combina geometría con `events.json` y cambia el observable desde intersección
espacial estática hacia intersección activa en un instante `t`. Requiere
geometría para calcular la relación.

## Composiciones

- `X_after_K_graph`: el grafo pierde coordenadas antes de que X pueda calcular
  el nuevo observable; debe fallar o declarar desconocido.
- `K_graph_after_X`: X calcula el observable con geometría y K lo materializa
  como relaciones temporales; debe poder responder la consulta declarada.
- `X_after_K_table`: la tabla conserva geometría y X puede añadir el observable.
- `K_table_after_X`: X añade el estado y K lo vuelve tabular.

El experimento debe distinguir no-conmutatividad real de simple diferencia de
serialización. Dos composiciones solo “conmutan” si preservan las mismas
consultas, invariantes y residuo relevante.

## Kill test

X-ANA-X queda debilitado si puede calcular el observable temporal sobre el grafo
sin geometría, porque entonces no cambió realmente el espacio requerido. KETAMINE
queda absorbido por conversión si las composiciones siempre producen la misma
capacidad y residuo sin importar el orden.

## Estado

Diseñado para ejecución con Python estándar. No implementa una API de operadores.
