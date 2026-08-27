# Decisión 073 — watermarks y eventos tardíos

**Estado:** experimental

## Decisión

Un watermark será tratado como un límite operacional para detectar eventos
tardíos, no como una prueba de completitud permanente. Los eventos posteriores
al watermark se conservarán en el ledger y reabrirán la proyección afectada.

```text
evento tardío
    ↓
ledger append-only
    ↓
replay de entidad afectada
    ↓
proyección provisional o revisada
```

Una proyección observada antes de un evento tardío puede ser correcta según la
información disponible, pero no debe presentarse como irreversible. La salida
debe conservar el momento de observación, el watermark vigente y si el estado
fue reabierto.

## Causalidad mínima

El fixture usa `parents` y `source_version`. Si llega un hijo antes que su
padre, queda pendiente y puede resolverse cuando el padre aparece. Si la
autoridad nunca llega, el claim permanece `UNKNOWN`. No se usa el orden de
llegada como causalidad.

El procesamiento de streams con eventos fuera de orden y semántica temporal
requiere distinguir el tiempo del evento de la observación y puede necesitar
semántica de tres valores para razonar en línea sin afirmar más de lo que se
sabe ([Runtime Verification of Temporal Properties over Out-of-order Data
Streams](https://arxiv.org/abs/1707.05555), [Consistent Streaming Through Time](https://arxiv.org/abs/cs/0612115)).

## Por qué no declarar éxito temprano

El watermark permite cerrar una ventana operativa, pero no elimina la
posibilidad de corrección posterior. Por eso la capa puede mostrar un estado
provisional para reducir latencia, pero un agente no debe ejecutar una acción
irreversible sólo porque la ventana se cerró.

## Límite

La decisión cubre un stream finito sintético. No resuelve todavía particiones,
relojes vectoriales, exactly-once, firmas, coordinación entre fuentes ni
atomicidad de una escritura externa.
