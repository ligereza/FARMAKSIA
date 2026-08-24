# Resultados 007 — frontera amplia de CODE-INE

Fecha: 2026-08-23

## Ejecución

Se compararon seis escenarios con Python estándar. El control `constrained_voc`
usa los mismos campos que la política candidata: ganancia, costo, crédito de
reutilización, valor de opción, riesgo irreversible y autorización humana.

| Escenario | CODE-INE | Control | Coincide |
|---|---|---|---:|
| `reuse-safe` | `reuse-C` | `reuse-C` | sí |
| `future-option` | `continue-A` | `continue-A` | sí |
| `irreversible-veto` | `continue-A` | `continue-A` | sí |
| `human-authority-veto` | `stop` | `stop` | sí |
| `stop-negative` | `stop` | `stop` | sí |
| `reuse-preference-tie` | `reuse-C` | `continue-A` | no |

Coincidencia: `5/6`.

## Análisis del desacuerdo

El único desacuerdo se produce porque CODE-INE añade un bono configurable de
`0.02` a una reutilización verificada. Sin ese bono, ambas acciones tienen
utilidad `0.30`; el control conserva la primera acción por desempate estable y
CODE-INE prefiere reutilizar. El desacuerdo no exige una capacidad nueva: es una
preferencia política parametrizable.

Los casos de autoridad humana, irreversibilidad, valor de opción y detención
negativa no separan las políticas. Todos quedan expresados como restricciones o
componentes de utilidad en el control estándar.

## Kill test y decisión provisional

La hipótesis “CODE-INE es un operador independiente por integrar continuar,
cambiar, reutilizar, detener, autoridad, irreversibilidad y opción futura” no
supera este kill test. En el dominio probado, la conducta queda explicada por
metarazonamiento/valor de computación más una política de desempate o bono.

CODE-INE queda eliminado como operador independiente por ahora. Puede
conservarse como nombre de una configuración política si ayuda a discutir
preferencias, pero no se implementará como módulo ni API. La pregunta más
amplia sobre aprendizaje online, no estacionariedad y preferencias humanas
queda fuera de este fixture y no se presenta como resuelta.
