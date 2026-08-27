# Resultados 066

## Resultado reproducible

`TEMPORAL_REPLAY_VERIFIED`

El fixture procesó nueve entregas sintéticas, ocho eventos únicos y una
reentrega duplicada. El orden de recepción fue deliberadamente irregular. El
replay comparó tres permutaciones —entrada original, reversa y orden por
observación— y produjo la misma firma de proyección en todas.

La proyección resultante fue:

```text
merge_request/mr-7.state     → SUPPORTED("merged")
pipeline/pipe-3.status       → SUPPORTED("success")
deployment/deploy-9.status   → CONFLICT(failed, success)
merge_request/mr-7.approved  → UNKNOWN
```

El pipeline fallido no desapareció: la retractación lo dejó registrado como
`RETRACTED` y la nueva observación como `ACTIVE`. El conflicto de deployment no
se resolvió por orden de llegada ni se colapsó a un valor. La observación de
aprobación sin `source_version` ni `valid_time` permaneció explícitamente en la
proyección como `UNKNOWN`.

## Kill tests

`FARMAXIA_066_TEMPORAL_REPLAY_KILL_TESTS_VALID`

Se bloquearon siete mutaciones: evento sin autoridad temporal, retractación a
un evento inexistente, payload duplicado conflictivo, desaparición del conflicto
por cambio de versión, pérdida de la historia de retractación, promoción de
`UNKNOWN` a `set` sin autoridad y versión futura respecto de la fuente.

## Evidencia y límite

Este resultado demuestra replay batch determinista y una separación explícita
entre historial y proyección. No demuestra todavía ordenamiento en vivo,
watermarks, particiones, relojes causales, consenso distribuido, firmas de
eventos ni atomicidad frente a una escritura externa.
