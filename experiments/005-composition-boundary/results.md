# Resultados 005 — composición X-ANA-X / KETAMINE

Fecha: 2026-08-23

## Ejecución

Se ejecutó el arnés con Python estándar sobre el SVG y el registro temporal del
experimento 001. `A_after_B` significa aplicar primero `B` y luego `A`.

| Composición | Consulta temporal | Resultado | Residuo relevante |
|---|---|---|---|
| `K_graph_after_X` | disponible → `left-region` | responde | pierde estilo y geometría continua después de materializar relaciones |
| `X_after_K_graph` | no disponible | falla explícitamente | faltan coordenadas para calcular el observable |
| `X_after_K_table` | disponible → `left-region` | responde | pierde estilos y tags, conserva geometría |
| `K_table_after_X` | disponible → `left-region` | responde | conserva el estado temporal solo en forma tabular |

## Interpretación

El par gráfico no conmuta. `KETAMINE-graph` elimina coordenadas antes de que
X-ANA-X pueda calcular la intersección activa; si X-ANA-X se aplica primero,
KETAMINE puede materializar el nuevo observable como relación temporal.

El par tabla es equivalente para la consulta del fixture porque la tabla
conserva los invariantes geométricos requeridos. Esto evita una afirmación
absoluta de “nunca conmutan”: la conmutatividad depende del contrato de
representación y del observable que X necesita.

## Falsación

La hipótesis “cambiar representación y cambiar espacio del problema siempre son
operaciones separadas por nombre” queda falsada. La frontera real depende de:

- información retenida;
- precondiciones de la reformulación;
- consulta declarada;
- residuo;
- orden de composición.

También queda falsada la hipótesis inversa de que nunca pueden conmutar: el par
tabla conmuta para este observable porque conserva suficiente geometría.

## Decisión provisional

X-ANA-X y KETAMINE son distinguibles como contratos, no como transformaciones
nominales:

- X-ANA-X cambia el espacio de observables/estados y puede requerir información
  que la representación anterior no contiene.
- KETAMINE elige una representación con invariantes y residuo declarados.

La no-conmutatividad es condicional y debe formar parte de cualquier futura
especificación, si ambas hipótesis sobreviven.
