# Resultados 067

## Resultado reproducible

`WATERMARK_LATE_REPLAY_VERIFIED`

El stream procesó 11 mensajes: tres watermarks y ocho entregas de eventos. Siete
eventos fueron únicos y una entrega fue duplicada. El watermark final fue 300 y
se mantuvo monotónico.

Dos eventos llegaron tarde, después de que el watermark ya había cerrado la
ventana operativa: `ev-pipeline-failed-correction` y `ev-deploy-green`. Ambos
fueron conservados y dispararon replay; ninguno fue descartado.

La secuencia observable del pipeline fue:

```text
watermark 300       → success (estado provisional)
corrección tardía   → failed  (proyección reabierta)
```

El replay batch en tres órdenes produjo la misma proyección final que el
procesamiento del stream. La proyección final fue:

```text
pipeline/pipe-3.status       → SUPPORTED("failed")
deployment/deploy-9.status   → CONFLICT(failed, success)
review_note/note-1.state     → SUPPORTED("ready")
merge_request/mr-7.approved  → UNKNOWN
```

El hijo causal `ev-review-child` llegó antes que su padre, quedó pendiente y se
resolvió cuando llegó `ev-review-parent`. La aprobación sin autoridad causal
permaneció `UNKNOWN`. La observación anterior del pipeline quedó como
`SUPERSEDED`, no fue borrada.

## Kill tests

`FARMAXIA_067_WATERMARK_LATE_REPLAY_KILL_TESTS_VALID`

Se bloquearon ocho mutaciones: descartar el evento tardío, cambiar la política
a `drop`, retroceder el watermark, alterar una reentrega, quitar la relación de
reemplazo, promover un claim sin autoridad causal, desconectar un hijo causal y
aceptar una versión futura.

## Evidencia y límite

El resultado demuestra una política local de append-and-replay y una frontera
explícita entre estado provisional, replay y desconocido. No demuestra todavía
watermarks distribuidos, particiones, relojes vectoriales, exactly-once,
firmas, consenso ni atomicidad con acciones externas.
