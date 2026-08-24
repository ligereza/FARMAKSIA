# Resultados 004 — KETAMINE: inversión, crédito y deuda

Fecha: 2026-08-23

## Ejecución

Se reutilizaron `input.svg` y `events.json` del experimento 001. Se ejecutó el
arnés con Python estándar. Las unidades de trabajo son un modelo explícito de
operaciones, no una medición universal de CPU.

| Representación | Clasificación | Bytes | Setup | Spatial-core | Relation-heavy | Full-mixed |
|---|---|---:|---:|---:|---:|---|
| SVG source | baseline | 199 | 4 | 10 | 16 | no disponible (`q-time`) |
| geometry table | KETAMINE candidato | 171 | 10 | 16 | 22 | no disponible (`q2`, `q-time`) |
| indexed table | índice/vista materializada existente | 323 | 14 | 18 | 20 | no disponible (`q-time`) |
| relation graph | KETAMINE/cache boundary | 154 | 3 | no disponible (`q1`, `q2`) | 9 | no disponible |
| temporal state | X-ANA-X candidato | 274 | 6 | 12 | 18 | 16 |

Workloads adicionales:

| Representación | repeat-indexed (`q0,q2,q3` × 6) | style-heavy (`q2` × 12) |
|---|---:|---:|
| SVG source | 40 | 28 |
| indexed table | 32 | 26 |
| temporal state | 42 | 30 |

## Lectura

### Geometry table

Preserva `q0`, `q1` y `q3`, pero pierde `q2`, que depende del estilo. En este
fixture su inversión no genera crédito: `spatial-core` cuesta `16` frente a
`10` del SVG source y `relation-heavy` cuesta `22` frente a `16`.

Eso no invalida la representación en general; muestra que una inversión solo es
crédito relativa a un workload y a un modelo de costo. En este caso es deuda o
inversión no amortizada.

### Relation graph

Para `relation-heavy`, el grafo cuesta `9` frente a `16` del source. Tiene
crédito para esa consulta, pero no puede responder `q1` ni `q2` porque destruyó
coordenadas, dimensiones y estilo. Es un caso límite entre representación
semántica y caché de respuestas precalculadas.

### Indexed table

La tabla con estilo e índices obtiene crédito solo en workloads suficientemente
repetidos: `32` frente a `40` en `repeat-indexed` y `26` frente a `28` en
`style-heavy`. En `spatial-core` cuesta `18` frente a `10`, y en
`relation-heavy` cuesta `20` frente a `16`.

Este comportamiento es exactamente el esperado de un índice o una vista
materializada: el crédito depende de la distribución de consultas. No es
evidencia de una teoría nueva de KETAMINE.

### Temporal state

Responde `q-time`, pero necesita `events.json`. No es una conversión que
preserva una dimensión del SVG: incorpora estado externo. Se clasifica como
X-ANA-X candidato, no como KETAMINE puro.

## Falsación

La intuición “más estructura siempre genera crédito” queda falsada. La misma
transformación puede ser deuda para un workload y crédito para otro. También
queda falsada la idea de que una representación que responde una consulta
preserva automáticamente la capacidad de responder consultas relacionadas.

## Decisión provisional

KETAMINE sobrevive solo como operador condicionado por una consulta declarada,
un workload y un contrato de residuo. No sobrevive como nombre para cualquier
conversión de formato ni para cualquier caché de resultados.

La frontera con X-ANA-X se mantiene provisionalmente: el estado temporal
requiere una entrada adicional y habilita `q-time`, mientras la tabla y el grafo
reorganizan la capacidad de consulta sobre el mismo input espacial.

## Kill test conceptual

La tabla indexada ya obtiene crédito después de suficientes consultas. Ese
crédito es indistinguible de índices y vistas materializadas existentes.
KETAMINE deberá aportar un contrato de representación, residuo y consulta en
dominios creativos; si no, se fusionará con esas teorías.
