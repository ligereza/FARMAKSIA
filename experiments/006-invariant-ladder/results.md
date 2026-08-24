# Resultados 006 — escalera de invariantes

Fecha: 2026-08-23

## Capacidades observadas

El arnés se ejecutó con Python estándar sobre el SVG del experimento 001.
`q-temporal` consulta el estado a `t = 0.75`; `q-relation` consulta la
relación precalculada con la línea central.

| Representación | Espacial | Área | Estilo | Tag | Relación | Temporal |
|---|---:|---:|---:|---:|---:|---:|
| `source` | sí | sí | sí | sí | no | no |
| `geometry-table` | sí | sí | no | no | no | no |
| `attribute-table` | sí | sí | sí | sí | no | no |
| `indexed-table` | sí | sí | sí | sí | no | no |
| `relation-graph` | no | no | no | no | sí | no |
| `attributed-graph` | sí | sí | no | no | sí | no |
| `temporal-state` | sí | sí | sí | sí | no | sí |

El grafo atribuido responde espacialmente porque el fixture usa rectángulos y
sus bounding boxes son suficientes para estas consultas. Eso no demuestra que
sea equivalente para geometría continua, curvas o predicados arbitrarios.

## Costos de workloads

Las cifras son unidades de trabajo declaradas por el arnés e incluyen
preparación.

| Representación | Preparación | Una espacial | 20 espaciales | 12 de estilo | Temporal |
|---|---:|---:|---:|---:|---:|
| `source` | 6 | 8 | 46 | 30 | no disponible |
| `geometry-table` | 10 | 12 | 50 | no disponible | no disponible |
| `attribute-table` | 14 | 16 | 54 | 38 | no disponible |
| `indexed-table` | 18 | 19 | 38 | 30 | no disponible |
| `relation-graph` | 4 | no disponible | no disponible | no disponible | no disponible |
| `attributed-graph` | 12 | 14 | 52 | no disponible | no disponible |
| `temporal-state` | 18 | 20 | 58 | 42 | 22 |

## Interpretación

El índice materializado solo obtiene crédito claro en la repetición espacial:
`38` frente a `46` del baseline, después de pagar preparación. En la consulta
espacial única cuesta `19` frente a `8`, y en el workload de estilo empata con
el baseline (`30`). El beneficio queda explicado por un índice conocido y por
la forma del workload.

El grafo relacional tiene una capacidad distinta y barata para una consulta
relacional, pero no sustituye a una representación geométrica. El grafo con
atributos recupera espacialidad y área a partir de bounding boxes, debilitando
la hipótesis de que un grafo siempre exige geometría continua; la pérdida de
estilo, tags y formas no rectangulares sigue siendo observable.

`temporal-state` solo responde la consulta temporal porque incorpora
`events.json`. Por procedencia, eso es un candidato a X-ANA-X con entrada
externa, no evidencia de que una conversión de SVG por sí sola haya creado el
tiempo.

## Falsación y decisión provisional

- No aparece una capacidad adicional atribuible a KETAMINE más allá de tablas,
  índices, grafos y estados conocidos.
- Se debilita la afirmación de que el grafo pierde toda consulta geométrica:
  un resumen geométrico basta para este dominio limitado.
- Se mantiene abierta la hipótesis en un corpus creativo real, donde el
  residuo puede incluir curvas, topología, estilos, capas y reversibilidad.

KETAMINE queda como contrato experimental útil para declarar consulta,
workload, inversión, residuo y autoridad, pero su novedad conceptual no está
demostrada. No se adopta una dependencia externa ni se implementa una API.
