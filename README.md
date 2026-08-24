# FARMAKSIA

Laboratorio independiente de investigación computacional, matemática y
artística. El repositorio conserva hipótesis, antecedentes, fixtures,
experimentos, kill tests, procedencia y decisiones de adopción.

Los nombres CODE-INE, X-ANA-X, KETAMINE y VIZZ son hipótesis de trabajo, no
compromisos de producto. Pueden fusionarse, redefinirse o eliminarse.

## Estado actual

| Hipótesis | Estado |
|---|---|
| CODE-INE | descriptor provisional con oracle ejecutable 029; interoperable con VIZZ; operador independiente eliminado |
| X-ANA-X | archivado como hipótesis independiente; protocolo de analogía conservado |
| KETAMINE | en cuarentena; sin prototipo activo ni teoría forzada |
| VIZZ | compuerta 028 de calidad/procedencia gaze-contingent; instrumentación manual opt-in; sin datos humanos, eficacia desconocida |

No se implementan operadores como API ni se fija arquitectura mientras sus
kill tests sigan abiertos.

## Ejecutar la suite

Desde la raíz del repositorio:

```text
python research/tools/run_suite.py
```

La suite usa Python estándar, valida la procedencia de todos los experimentos,
regenera y verifica el piloto VIZZ y confirma explícitamente `NO_HUMAN_DATA`
cuando no existe un archivo humano.

## Leer el laboratorio

- [Protocolo del loop](RESEARCH_LOOP.md)
- [Auditoría consolidada](research/decisions/009-laboratory-audit.md)
- [Kill test amplio de CODE-INE](experiments/007-codeine-general-boundary/results.md)
- [Transición de sesión CODE-INE](experiments/016-codeine-session-state/results.md)
- [Frontera de X-ANA-X](experiments/008-xanax-boundary/results.md)
- [Cadena de analogía X-ANA-X](experiments/017-xanax-analogy-chain/results.md)
- [Control X-ANA-X frente a reformulación](experiments/018-xanax-reformulation-control/results.md)
- [Auditoría final y archivo X-ANA-X](experiments/019-xanax-provenance-archive-audit/results.md)
- [Kill test metodológico de VIZZ](research/decisions/015-vizz-carryover-kill.md)
- [Piloto VIZZ contrabalanceado](experiments/009-vizz-counterbalanced/results.md)
- [Kill test poligonal de KETAMINE](experiments/011-nonrectangular-boundary/results.md)
- [Kill test de curvas y capas](experiments/012-curves-layers-boundary/results.md)
- [Prototipo VIZZ de adaptación perceptual](experiments/013-vizz-perceptual-adaptation/results.md)
- [Consulta VIZZ de entrada en repetición](experiments/014-vizz-decision-query/results.md)
- [Contrato VIZZ de sesión](experiments/015-vizz-session-contract/results.md)
- [Puente VIZZ → CODE-INE](experiments/020-vizz-codeine-event-bridge/results.md)
- [Compuerta del adaptador manual VIZZ](experiments/021-manual-adapter-gate/results.md)
- [Puente largo VIZZ → CODE-INE](experiments/022-vizz-codeine-long-bridge/results.md)
- [Frontera de observabilidad VIZZ → CODE-INE](experiments/023-vizz-codeine-observability-boundary/results.md)
- [Frontera de latencia y cobertura VIZZ](experiments/024-vizz-latency-coverage-boundary/results.md)
- [Invariancia de condición de display VIZZ](experiments/025-vizz-display-condition-invariance/results.md)
- [Señal de objetivo CODE-INE](experiments/026-codeine-objective-signal/results.md)
- [Oráculo de objetivo CODE-INE](experiments/027-codeine-objective-oracle/results.md)
- [Oracle ejecutable y mutación CODE-INE](experiments/029-codeine-executable-oracle/results.md)
- [Compuerta de calidad gaze-contingent VIZZ](experiments/028-vizz-gaze-quality-gate/results.md)
- [Auditoría consolidada de estado](research/decisions/032-laboratory-state-audit.md)
- [Decisión de latencia y cobertura VIZZ](research/decisions/034-vizz-latency-coverage-boundary.md)
- [Decisión de condición de display VIZZ](research/decisions/035-vizz-display-condition-invariance.md)
- [Literatura de observabilidad VIZZ](research/literature/010-vizz-observability-boundary.md)
- [Literatura de condiciones de display VIZZ](research/literature/011-vizz-display-conditions.md)
- [Literatura de señal objetiva CODE-INE](research/literature/012-codeine-objective-signal.md)
- [Literatura de oráculos verificables CODE-INE](research/literature/013-codeine-verifiable-objective.md)
- [Literatura de oracle ejecutable y mutation testing CODE-INE](research/literature/015-codeine-executable-oracle-mutation.md)
- [Decisión de oracle ejecutable CODE-INE](research/decisions/039-codeine-executable-oracle.md)
- [Auditoría de completitud de la fundación](research/decisions/040-laboratory-completion-audit.md)
- [Literatura de calidad de mirada y herramientas VIZZ](research/literature/014-vizz-gaze-quality-tools.md)
- [Decisión de compuerta gaze-contingent VIZZ](research/decisions/038-vizz-gaze-quality-gate.md)
- [Contrato de ingreso de corpus](research/corpus-intake.md)
- [Piloto humano VIZZ](experiments/003-vizz-decision/pilot_protocol.md)
- [Compuerta de adopción de herramientas](research/decisions/011-tool-adoption-gate.md)

## Regla de honestidad

La automatización puede demostrar estructura, costo, preservación,
procedencia y falsación lógica. No puede demostrar percepción humana, valor
artístico ni autoridad de decisión.
