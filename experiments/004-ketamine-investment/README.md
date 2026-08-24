# Experimento 004 — KETAMINE: inversión, crédito y deuda

## Pregunta

¿Una transformación de representación reduce el costo de un workload futuro
sin cambiar la consulta declarada, y qué información o capacidades sacrifica?

## Entrada

Se reutilizan `input.svg` y `events.json` del experimento 001. La procedencia
de ambos archivos se mantiene explícita; no se crea una copia silenciosa.

## Representaciones

1. `svg-source`: estructura geométrica y estilo extraídos del SVG.
2. `geometry-table`: tabla numérica preparada para consultas geométricas.
3. `indexed-table`: tabla que conserva estilo y materializa índices por estilo
   e intersección.
4. `relation-graph`: relaciones de intersección precalculadas.
5. `temporal-state`: geometría combinada con eventos externos; es control de
   frontera para X-ANA-X, no KETAMINE puro.

## Workload

- `q0`: regiones que intersectan la línea central;
- `q1`: regiones cuyo área supera el umbral;
- `q2`: regiones con estilo rojo;
- `q3`: relación precalculada con la línea central;
- `q-time`: regiones activas en `t = 0.25`.

Workloads repetidos incluyen `repeat-indexed` y `style-heavy` para observar
cuándo una inversión se amortiza.

## Medidas

- unidades de trabajo de preparación;
- unidades de trabajo por consulta;
- tamaño serializado;
- consultas respondibles;
- información/residuo;
- entradas externas;
- reversibilidad;
- costo total del workload;
- crédito o deuda según la consulta.

Las unidades de trabajo son un modelo explícito de comparación, no una medida
universal de CPU. No se reduce almacenamiento, tiempo, información y trabajo
humano a una sola cifra.

## Kill tests

KETAMINE queda debilitado si:

- ninguna representación ofrece crédito después de amortizar su preparación;
- el grafo solo es un caché de respuestas y no una representación reutilizable;
- la tabla no puede declarar qué consulta preserva y qué residuo deja;
- la transformación temporal parece KETAMINE solo porque se oculta la entrada
  externa;
- el ledger de costo no distingue inversión, deuda, crédito y pérdida.

## Estado

Diseñado para ejecución con Python estándar. No implementa KETAMINE como API.
