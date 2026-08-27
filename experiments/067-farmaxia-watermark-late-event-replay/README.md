# Experimento 067 — watermarks, eventos tardíos y causalidad

## Pregunta

¿Qué debe hacer la capa cuando un evento llega después del watermark, cuando
una corrección cambia una proyección que parecía cerrada y cuando un evento
depende de otro que todavía no fue observado?

## Método

El fixture representa un stream sintético GitLab con tres watermarks. Un
pipeline aparece como exitoso, después llega una corrección tardía que lo marca
fallido. Un deployment recibe dos valores de la misma versión y queda en
`CONFLICT`. Un evento causal llega antes que su padre y se resuelve cuando el
padre aparece. Otro evento carece de autoridad causal y queda en `UNKNOWN`.

La política es `append_and_replay`: un evento tardío nunca se elimina. Se
incorpora al ledger, reabre la proyección afectada y se compara con un replay
batch independiente. El watermark es un límite operativo para detectar
latencia, no una prueba de que nunca llegarán datos más antiguos.

## Resultado esperado

```text
antes de la corrección tardía: pipeline = success
después del replay:            pipeline = failed
deployment:                    CONFLICT
padre causal tardío:           resuelto
autoridad causal ausente:      UNKNOWN
```

## Reproducir

```powershell
python experiments/067-farmaxia-watermark-late-event-replay/run_experiment.py
python experiments/067-farmaxia-watermark-late-event-replay/run_contract_test.py
python experiments/067-farmaxia-watermark-late-event-replay/run_kill_test.py
```

## Límite

Es un stream finito y local. No implementa particiones, watermarks distribuidos,
exactly-once, relojes vectoriales completos, firmas, transacciones externas ni
consenso. La causalidad se representa con IDs de padres para probar el contrato
mínimo; no se afirma que eso sustituya un reloj causal en producción.
