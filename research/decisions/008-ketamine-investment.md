# Decisión 008 — KETAMINE depende del workload

Fecha: 2026-08-23

## Evidencia

El experimento 004 comparó cuatro representaciones y tres workloads:

- `geometry-table` preserva consultas geométricas, pero pierde estilo y no
  obtiene crédito en los workloads pequeños (`16` frente a `10`, `22` frente a
  `16`).
- `indexed-table`, que conserva estilo y materializa índices, obtiene crédito
  solo en workloads repetidos (`32` frente a `40`, `26` frente a `28`) y tiene
  deuda en workloads cortos (`18` frente a `10`, `20` frente a `16`).
- `relation-graph` obtiene crédito en `relation-heavy` (`9` frente a `16`),
  pero no responde consultas de área o estilo.
- `temporal-state` responde `q-time` solo porque incorpora `events.json`.

## Decisión

KETAMINE no significa “transformar a una representación más estructurada”. Su
definición debe incluir:

- consulta declarada;
- workload;
- inversión inicial;
- residuo e información no preservada;
- reversibilidad;
- costos separados;
- entradas externas y autoridad.

El crédito es relacional: una representación puede ser crédito para una familia
de consultas y deuda para otra.

La tabla indexada confirma que este fenómeno ya tiene la forma de un índice o
una vista materializada: preparación, mantenimiento y beneficio dependen del
workload.

## Estado conceptual

KETAMINE sobrevive provisionalmente como contrato de transformación de
representación orientado a una consulta. El grafo permanece en la frontera con
caching/materialized views, y la tabla indexada es explícitamente un análogo
existente, no una afirmación de novedad. La dimensión temporal continúa siendo
candidata a X-ANA-X, no una conversión de representación pura.

## Kill test siguiente

Ampliar la tabla para conservar estilo y medir un workload suficiente para
amortizar preparación. Si el único crédito proviene de precalcular respuestas
concretas, fusionar KETAMINE con caching/materialized views.
