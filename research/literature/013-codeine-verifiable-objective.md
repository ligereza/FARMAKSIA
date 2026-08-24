# Investigación 013 — verificación independiente del objetivo CODE-INE

Fecha: 2026-08-24

## El problema del oráculo

En testing, un resultado observado necesita una regla que distinga el
comportamiento correcto del incorrecto. La encuesta de Barr et al. describe
este `test oracle problem` y las soluciones basadas en especificaciones,
contratos, modelos y testing metamórfico; cuando ninguna basta, la
especificación informal humana sigue siendo una fuente de oracle:

- https://discovery.ucl.ac.uk/id/eprint/1471263/
- https://philmcminn.com/publications/barr2015.pdf

Para CODE-INE, un `objective_score` escrito por el mismo proceso no es un
oráculo independiente. Puede ser una señal declarada útil para explorar una
hipótesis, pero no verifica por sí solo que el objetivo se haya cumplido.

## Relación con comprensión de código

Los estudios de comprensión de código usan tareas con respuestas verificables,
como derivar la salida de una función, y separan desempeño, dificultad y
medidas neurofisiológicas. La red frontoparietal observada en código no
convierte los logs en medidas de neurotransmisores:

- https://elifesciences.org/articles/59340
- https://pubmed.ncbi.nlm.nih.gov/36825214/

Por eso FARMAXIA separa:

1. score declarado;
2. oracle sintético separado, por ejemplo un resultado de test o aceptación;
3. eventual evidencia humana, que no existe todavía.

## Consecuencia operacional

El experimento 027 compara score y oracle sobre la misma traza sintética. Si
coinciden, el resultado es `verified` solo dentro del fixture. Si falta el
oracle, es `declared_only`; si discrepan, es `conflict`; si el oracle es
incompleto o inválido, es `unavailable` o `rejected`.

Ninguna de estas categorías demuestra comprensión, deriva subjetiva, ansiedad,
intoxicación, sedación o química cerebral.
