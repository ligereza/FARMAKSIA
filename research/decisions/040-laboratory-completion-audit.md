# Decisión 040 — auditoría de completitud de la fundación FARMAXIA

Fecha: 2026-08-24

## Criterio auditado

El objetivo de esta fase se considera cubierto cuando el repositorio es un
laboratorio reproducible, cada hipótesis tiene un prototipo mínimo o una
decisión fundada, la literatura y las herramientas están registradas, y los
desconocidos humanos permanecen explícitos. Esto no exige afirmar que VIZZ,
CODE-INE o X-ANA-X describan una experiencia neurobiológica real.

## Matriz requisito → evidencia

| Requisito | Evidencia actual | Resultado |
|---|---|---|
| suite reproducible y procedencia | `research/tools/run_suite.py`, validadores y `SUITE_VALID` | cubierto |
| VIZZ mínimo, contratos y límites | experimentos 013, 015, 022, 024, 025 y 028; literatura 010, 011, 014 | provisional; desconocidos humanos explícitos |
| CODE-INE mínimo y objetivo verificable | experimentos 016, 026, 027 y 029; decisiones 037 y 039; literatura 012, 013, 015 | provisional; oracle solo de fixture |
| X-ANA-X mínimo y comparación | experimentos 017, 018 y 019 | archivado como hipótesis independiente |
| KETAMINE | decisiones 008 y 032; controles 004–012 | cuarentena explícita |
| herramientas open source y adopción | decisiones 011, 024, 038 y 039; matrices de candidatos | herramientas candidatas registradas; runtime mínimo adoptado |
| kill tests, límites y decisiones | contratos y `provenance.json` de experimentos 013–029; suite integrada | cubierto |
| seguridad de datos y corpus | `research/corpus/manifest.json`, auditoría de estado y flags prohibidos | corpus vacío; sin datos humanos ni intoxicación |

## Resultado

`python research/tools/audit_lab_completion.py` devuelve `LAB_COMPLETION_VALID`.
La suite completa devuelve `SUITE_VALID` y la auditoría de estado devuelve
`LAB_STATE_VALID`.

La fundación reproducible de FARMAXIA queda completada para esta fase. VIZZ y
CODE-INE continúan como hipótesis provisionales con investigación futura
opcional; X-ANA-X queda archivado y KETAMINE permanece en cuarentena.

## Lo que no se afirma

No existe evidencia humana. Ningún resultado demuestra percepción, confort,
comprensión, ansiedad, sedación, intoxicación, neurotransmisores, receta
óptica, sueño ni valor artístico. Tampoco se afirma que el oracle ejecutable
sea independiente de todos los sesgos: solo es independiente del score dentro
de sus fixtures.

## Regla de reapertura

Un nuevo ciclo solo debe abrirse si aporta una pregunta, herramienta,
experimento o decisión que reduzca uno de esos desconocidos sin romper el
corpus vacío, la cuarentena de KETAMINE o la prohibición de experimentar bajo
intoxicación.
