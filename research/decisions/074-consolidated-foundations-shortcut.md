# Decisión 074 — atajo con fundamentos consolidados

**Fecha:** 2026-08-27  
**Estado:** adoptada  
**Frentes:** FARMAKSIA, CODE-INE, X-ANA-X, VIZZ

## Pregunta

¿Conviene seguir creando experimentos propios para eventos, tiempo, linaje,
permisos y sincronización, o podemos apoyarnos en proyectos maduros?

## Respuesta corta

Sí hay un atajo, pero no consiste en importar una plataforma enorme. Consiste
en adoptar los contratos que ya tienen una comunidad y una especificación, y
mantener pequeño el núcleo que FARMAKSIA sí necesita controlar.

```text
estándar probado → contrato FARMAKSIA → adapter reversible → verificador propio
```

FARMAKSIA conserva la autoridad sobre significado, procedencia, `UNKNOWN`,
conflictos, confirmación y resultado verificado. Los proyectos externos pueden
transportar, almacenar o evaluar una parte; no pueden decidir por sí solos que
una representación es verdadera.

## Qué reutilizamos

| Necesidad | Referencia consolidada | Uso en FARMAKSIA |
| --- | --- | --- |
| Sobre común para eventos | [CloudEvents](https://github.com/cloudevents/spec) | Adoptar el sobre `specversion`, `id`, `source`, `type`, `time`, `subject` y `data` para futuros adapters. `source + id` será la identidad de entrega. |
| Linaje de procesos y datasets | [OpenLineage](https://openlineage.io/docs/) | Usarlo para describir jobs, runs y datasets cuando el flujo deje de ser un fixture local. El ledger de claims seguirá siendo más detallado que OpenLineage. |
| Tiempo de evento y retrasos | [Apache Flink](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/) y el [Dataflow Model](https://research.google/pubs/the-dataflow-model-a-practical-approach-to-balancing-correctness-latency-and-cost/) | Adoptar la distinción event-time/processing-time y watermark/late-event. El experimento 067 queda como prueba local mínima, no como reemplazo de Flink. |
| Log y proyecciones | [EventSourcingDB](https://docs.eventsourcingdb.io/) o una biblioteca de event sourcing | Considerarlos sólo cuando necesitemos persistencia, suscripciones, snapshots o replay operativo. Hoy el fixture append-only es suficiente y más auditable. |
| Política de autorización | [Open Policy Agent](https://www.openpolicyagent.org/docs) | Candidato para decisiones declarativas de acceso y ejecución. No instalarlo hasta tener un adapter real que necesite separar policy decision de enforcement. |
| Permisos por relaciones | [OpenFGA](https://github.com/openfga/openfga) | Candidato si una institución necesita expresar relaciones como paciente→equipo→servicio. No sustituye la identidad ni la autoridad de la fuente. |
| Edición concurrente local | [Automerge](https://github.com/automerge/automerge) | Reservarlo para documentos multiusuario/local-first. No usar CRDT para resolver automáticamente conflictos de una fuente institucional autoritativa. |
| Stream processing con garantías | [Kafka Streams](https://kafka.apache.org/documentation/streams/) | Considerarlo si aparecen tópicos reales, recuperación y garantías de procesamiento que el runtime local no puede ofrecer. No introducir un broker para un fixture sintético. |

## Decisión de implementación

1. **No crear ahora el experimento 068 de particiones y relojes vectoriales.**
   Es una buena prueba académica, pero no cambia todavía una decisión de
   producto: no tenemos dos writers reales ni un adapter institucional en
   producción.
2. **No descargar ni instalar nada en este ciclo.** La investigación muestra
   qué piezas existen; la adopción debe esperar a una superficie concreta,
   datos sintéticos y un contrato de reemplazo.
3. **Normalizar el siguiente adapter alrededor de CloudEvents**, conservando
   los campos FARMAKSIA en `data` o como extensiones namespaced. Así no
   inventamos otro formato de mensajes para cada aplicación.
4. **Mantener el replay y los kill tests locales.** Sirven como oráculo pequeño
   y rápido aunque después el transporte sea Flink, Kafka o un event store.
5. **Medir antes de escalar.** Sólo se agrega infraestructura cuando el
   volumen, latencia, persistencia, recuperación o permisos hagan fallar el
   camino local.

## Por qué esto es un atajo real

Imagina que FARMAKSIA es un adaptador de enchufes. No fabricamos una central
eléctrica para probar si dos aparatos pueden conectarse: usamos una forma
común para el enchufe, dejamos nuestro adaptador pequeño y comprobamos que la
energía llegó al aparato correcto.

067 ya comprobó la idea mínima de “llega una carta atrasada y reabrimos el
estado”. Flink documenta ese mismo problema como event time, watermark y late
element. Repetir el concepto con otra maqueta no aporta suficiente información
ahora. El trabajo valioso es hacer que el contrato de FARMAKSIA pueda viajar
en un sobre estándar y que un verificador independiente siga sabiendo qué
fuente lo respalda.

## Límites y kill tests

- CloudEvents normaliza el sobre; no valida que el contenido sea verdadero.
- OpenLineage describe linaje de ejecuciones; no reemplaza provenance de un
  claim ni una autoridad de dominio.
- Flink/Kafka resuelven infraestructura de stream; no resuelven identidad,
  semántica ni permisos institucionales.
- Event sourcing conserva historia; no convierte dos valores incompatibles en
  uno correcto.
- OPA/OpenFGA autorizan decisiones; no deben recibir una identidad incompleta
  como si fuera válida.
- Automerge puede fusionar documentos colaborativos; no debe ocultar un
  conflicto entre observaciones autoritativas.

La adopción queda bloqueada si:

- obliga a enviar datos humanos o pantalla fuera del equipo sin autorización;
- no permite conservar `source_ref`, versión, hash y padres de derivación;
- cambia el resultado según el orden de llegada sin declararlo;
- no puede reproducirse el replay sin el servicio externo;
- añade una dependencia sin un beneficio medido en latencia, recuperación,
  costo o cobertura;
- declara `verified` cuando sólo existe una respuesta del transporte o del
  agente.

## Siguiente paso

El fixture local de CloudEvents ya fue implementado en el
[experimento 068](../../experiments/068-farmaxia-cloudevents-envelope/README.md).
Conserva el sobre original, deduplica por `source + id` y mantiene el mapeo
interno de FARMAKSIA. El primer adapter sintético ya fue verificado en el
[experimento 069](../../experiments/069-farmaxia-cloudevents-cross-application-adapter/README.md):
reutiliza el compilador 065, conserva los resultados y mantiene `DRY_RUN_ONLY`.
El segundo par sintético ya fue verificado en el
[experimento 070](../../experiments/070-farmaxia-openemr-nextcloud-adapter/README.md):
cambió la superficie y las entidades sin cambiar el núcleo. La tercera
superficie sintética, un parche de código CODE-INE, fue verificada en el
[experimento 071](../../experiments/071-farmaxia-codeine-patch-adapter/README.md):
añadió sólo semántica específica de parche —hash base, precondición y
previsualización— y conservó el mismo sobre, replay, procedencia y permisos.
La auditoría media sintética fue verificada en el
[experimento 072](../../experiments/072-farmaxia-media-timeline-adapter/README.md):
timeline, codec y sincronización sí introdujeron semántica real, pero se
encapsularon sin cambiar el núcleo. El siguiente objetivo es comparar el
contrato con representaciones read-only sintéticas de OTIO y `ffprobe`. Ese
puente fue verificado en el [experimento 073](../../experiments/073-farmaxia-media-representation-bridge/README.md):
OTIO-style conserva la edición y ffprobe-style exige un sidecar editorial. El
siguiente objetivo es probar esa composición por hash/versiones, sin construir
aún un renderer ni añadir infraestructura por anticipación.

## Fuentes revisadas

- [CloudEvents: especificación y sobre JSON](https://github.com/cloudevents/spec)
- [OpenLineage: modelo de jobs, runs y datasets](https://openlineage.io/docs/)
- [Apache Flink: event time, watermarks y late elements](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/)
- [Apache Kafka Streams: estado y garantías de procesamiento](https://kafka.apache.org/33/streams/core-concepts/)
- [Open Policy Agent: policy decision separada del enforcement](https://www.openpolicyagent.org/docs)
- [OpenFGA: autorización basada en relaciones](https://openfga.dev/docs/modeling/getting-started)
- [Automerge: CRDT para documentos concurrentes](https://github.com/automerge/automerge)
- [EventSourcingDB: event sourcing y observación de eventos](https://docs.eventsourcingdb.io/)
