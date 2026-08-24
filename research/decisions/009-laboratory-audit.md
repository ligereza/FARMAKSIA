# Auditoría 009 — estado real del laboratorio

Fecha: 2026-08-23

## Suite ejecutada

Se ejecutaron:

- compilación de todos los scripts Python;
- experimento 001 y su control temporal;
- experimento 002 y kill test dinámico;
- paridad y piloto VIZZ;
- auditoría de arrastre metodológico del piloto VIZZ;
- analizador VIZZ sin datos;
- experimento 004 de inversión KETAMINE;
- experimento 005 de composición X-ANA-X/KETAMINE;
- experimento 006 de escalera de invariantes;
- experimento 007 de kill test amplio CODE-INE;
- experimento 008 de frontera X-ANA-X;
- experimento 009 de piloto VIZZ contrabalanceado;
- experimento 010 de familia metamórfica X-ANA-X/KETAMINE;
- experimento 011 de frontera no rectangular KETAMINE;
- experimento 012 de curvas, agujeros y capas KETAMINE;
- doce validaciones de procedencia.

Todos terminaron con código `0`. Las salidas críticas fueron:

- `CONDITIONS_VALID`;
- `PILOT_VALID`;
- `PROVENANCE_VALID` para los doce experimentos;
- `NO_HUMAN_DATA` para el analizador VIZZ.

## Matriz de hipótesis

| Nombre | Hipótesis actual | Analogía existente | Estado | Evidencia | Kill test pendiente |
|---|---|---|---|---|---|
| CODE-INE | política que decide continuar, cambiar, reutilizar o detener bajo estado y costo | metarazonamiento, value-of-computation, optimal stopping, bandits | operador independiente eliminado; vocabulario opcional | [kill test 002](../../experiments/002-continuation-boundary/results-kill.md), [kill test amplio 007](../../experiments/007-codeine-general-boundary/results.md), [decisión 012](012-codeine-general-kill.md) | solo reabrir con una propiedad no expresable por utilidad, restricciones o preferencias parametrizadas |
| X-ANA-X | modifica variables, observables, estados o preguntas disponibles | reformulación, abstracción, state augmentation, cambio de coordenadas | contrato provisional; novedad no demostrada | [decisión 002](002-boundary-decision.md), [resultados 001](../../experiments/001-representation-boundary/results.md), [composición 005](../../experiments/005-composition-boundary/results.md), [frontera 008](../../experiments/008-xanax-boundary/results.md), [metamórfico 010](../../experiments/010-metamorphic-boundary/results.md), [decisión 013](013-xanax-boundary.md) | probar una reformulación creativa no reducible a consulta, vista o state augmentation conocida |
| KETAMINE | transforma representación bajo consulta, workload, invariantes, residuo y costo | IR, vistas materializadas, índices, cachés, abstracción | provisional; novedad muy debilitada por pérdidas geométricas y compositivas conocidas | [resultados 004](../../experiments/004-ketamine-investment/results.md), [decisión 008](008-ketamine-investment.md), [composición 005](../../experiments/005-composition-boundary/results.md), [escalera 006](../../experiments/006-invariant-ladder/results.md), [metamórfico 010](../../experiments/010-metamorphic-boundary/results.md), [poligonal 011](../../experiments/011-nonrectangular-boundary/results.md), [curvas 012](../../experiments/012-curves-layers-boundary/results.md), [decisiones 019–020](019-nonrectangular-kill.md) | probar corpus creativo real; si el crédito sigue explicado por materialización conocida, eliminar el nombre |
| VIZZ | hace perceptible estructura computacional para una decisión humana | visual analytics, external cognition, HCI, mixed-initiative | no validado; piloto 0.2 preparado | [resultados 003](../../experiments/003-vizz-decision/results.md), [resultados 009](../../experiments/009-vizz-counterbalanced/results.md), [decisiones 015–016](015-vizz-carryover-kill.md) | obtener datos humanos, verificar balance real y superar la vista estática sin añadir información |

## Herramientas adoptadas

| Herramienta | Uso | Estado |
|---|---|---|
| Python estándar | fixtures, parsers, arneses y verificadores | adoptada |
| Node.js local | comprobación sintáctica del piloto | adoptada como verificación |
| Git | trazabilidad del worktree | adoptada |
| JSON/HTML/SVG | fixtures, procedencia y estímulos | adoptados como formatos mínimos |
| validador PROV-inspirado | hashes, entidades, actividades y agentes | adoptado |
| arnés `research/tools/run_suite.py` | repetición, regresión y coherencia de generadores | adoptado |
| validador `research/tools/validate_corpus_manifest.py` | autoridad, licencia, hash y consulta de cada entrada | adoptado |
| auditor `experiments/003-vizz-decision/audit_pilot_design.py` | detectar arrastre por estímulo repetido | adoptado como guardia metodológica |
| agregador `experiments/009-vizz-counterbalanced/aggregate_pilot.py` | validar sesiones y producir métricas descriptivas | adoptado como guardia de ingestión |

## Herramientas deliberadamente no adoptadas

DuckDB, Apache Arrow, OpenImageIO, Vega-Lite, Cytoscape.js, OpenLineage,
RO-Crate, ASlib, SMAC3 y frameworks de bandits permanecen diferidos. El
laboratorio tiene evidencia suficiente para investigar sus conceptos, pero no
un workload que justifique introducir sus dependencias. La regla sigue siendo:
instalar una herramienta solo cuando mejore una medición concreta y pueda
reemplazarse sin imponer arquitectura.

## Auditoría de alcance

Cumplido:

- investigación científica e informática inicial;
- búsqueda de equivalentes y contraejemplos;
- experimentos mínimos reproducibles;
- kill test de CODE-INE estrecho;
- kill test amplio de CODE-INE y eliminación provisional del operador;
- frontera de entrada/pregunta/observable de X-ANA-X;
- frontera provisional X-ANA-X/KETAMINE;
- composición condicional y no-conmutatividad parcial X-ANA-X/KETAMINE;
- escalera de invariantes y control explícito de índices/vistas;
- piloto VIZZ instrumentado;
- kill test metodológico de arrastre VIZZ;
- piloto VIZZ contrabalanceado preparado;
- compuerta de análisis multi-sesión VIZZ;
- robustez metamórfica limitada de X-ANA-X/KETAMINE;
- kill test no rectangular de KETAMINE;
- kill test de curvas, agujeros y capas KETAMINE;
- procedencia y residuos registrados;
- adopción prudente de herramientas.

No cumplido todavía:

- evidencia humana de VIZZ;
- piloto VIZZ con conjuntos balanceados;
- evidencia humana de VIZZ 0.2;
- kill test definitivo de X-ANA-X;
- demostración de novedad de KETAMINE frente a índices/vistas;
- decisión final sobre la pregunta amplia de CODE-INE;
- corpus creativo real y workload representativo;
- geometría no rectangular y composición rica;
- SVG real con paths, capas y metadata;
- implementación de operadores sobrevivientes.

## Regla de continuación

El laboratorio no debe pasar a una API de operadores mientras cualquiera de
estas afirmaciones siga siendo solo provisional. El próximo avance de mayor
valor es obtener evidencia humana de VIZZ y, en paralelo, llevar la escalera de
invariantes a un corpus creativo real. La decisión de herramientas queda
registrada en [011](011-tool-adoption-gate.md) y [014](014-suite-runner-adoption.md).
