# FARMAKSIA

Laboratorio independiente de investigación computacional, matemática y
artística. El repositorio conserva hipótesis, antecedentes, fixtures,
experimentos, kill tests, procedencia y decisiones de adopción.

Los nombres CODE-INE, X-ANA-X, KETAMINE y VIZZ son hipótesis de trabajo, no
compromisos de producto. Pueden fusionarse, redefinirse o eliminarse.

## Estado actual

| Hipótesis | Estado |
|---|---|
| CODE-INE | descriptor provisional de transición; interoperable con VIZZ 020; operador independiente eliminado |
| X-ANA-X | archivado como hipótesis independiente; protocolo de analogía conservado |
| KETAMINE | contrato provisional; novedad muy debilitada frente a índices y pérdidas geométricas/compositivas conocidas |
| VIZZ | compuerta 021 de consulta, exposición e instrumentación manual opt-in; sin datos humanos, eficacia desconocida |

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
- [Contrato de ingreso de corpus](research/corpus-intake.md)
- [Piloto humano VIZZ](experiments/003-vizz-decision/pilot_protocol.md)
- [Compuerta de adopción de herramientas](research/decisions/011-tool-adoption-gate.md)

## Regla de honestidad

La automatización puede demostrar estructura, costo, preservación,
procedencia y falsación lógica. No puede demostrar percepción humana, valor
artístico ni autoridad de decisión.
