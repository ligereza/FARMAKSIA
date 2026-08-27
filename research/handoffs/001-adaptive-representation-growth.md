# Handoff 001 — crecimiento agnóstico a dominios y adaptación entre aplicaciones

**Fecha:** 2026-08-27
**Estado:** activo
**Propósito:** convertir la visión general en un reto técnico real sin quedar
atados a nombres, títulos o a una sola interfaz

## Norte transferido

El proyecto no debe crecer como una aplicación que intenta incluir todas las
funciones. Debe crecer como un **sistema de transducción semántica entre
superficies**:

```text
superficie A → estado semántico → plan de representación → superficie B
                                      ↓
                               interacción reversible
                                      ↓
                              resultado verificable
```

La capa no reemplaza las aplicaciones. Las conecta, las interpreta y cambia la
forma en que la información puede recorrerse. El núcleo general puede servir a
varios dominios; la comprensión específica siempre exige un adaptador y un
verificador propios.

## Modelo técnico

```text
x_t = estado de una fuente o aplicación
g_t = objetivo de la persona
b_t = capacidades/preferencias declaradas y evidencia de interacción
r_t = representación elegida
a_t = acción explícita de persona o agente
o_t = resultado observable
```

La política selecciona una representación:

```text
r_t ~ π(r | x_t, g_t, b_t, contexto)
```

Y debe optimizar utilidad de tarea, costo de atención, riesgo, latencia y costo
computacional, sujeto a:

```text
preservación de consultas críticas
procedencia completa
reversibilidad cuando sea posible
verificación independiente
abstención si la identidad o el resultado son inciertos
```

No se infieren diagnósticos, emociones, intoxicación, comprensión o intención
oculta desde clicks, cámara, postura, tiempo de permanencia o eye tracking.

## Ejemplo real 1 — GitLab + Mattermost

### Por qué este par

Una institución de software, universidad o equipo técnico puede usar GitLab
para issues, merge requests, commits, pipelines y despliegues, y Mattermost
para conversación, coordinación y notificaciones. GitLab documenta webhooks
para eventos de issues, merge requests, comentarios y deployments, además de
una API REST para automatizar revisiones y bloqueos
([webhook events](https://docs.gitlab.com/user/project/integrations/webhook_events/),
[REST API](https://api.gitlab.com/rest/)). Mattermost ofrece webhooks HTTP con
payload JSON, comandos, plugins y REST API para integrar sistemas externos
([webhooks](https://docs.mattermost.com/integrations-guide/webhook-integrations.html),
[REST API](https://developers.mattermost.com/integrate/reference/rest-api/)).

### Desafío de adaptación

Construir una capa que permita que una persona que entiende la conversación de
Mattermost pueda comprender y operar un flujo de revisión de GitLab sin tener
que aprender de inmediato toda la interfaz de GitLab.

```text
Merge Request abierto en GitLab
        ↓
estado: cambios pendientes, pipeline fallido, revisión requerida
        ↓
Mattermost muestra una representación contextual:
qué cambió → qué bloquea → qué puede hacer la persona
        ↓
la persona solicita explicación, compara o confirma una acción
        ↓
GitLab verifica el estado real del Merge Request y del pipeline
```

No se copiaría GitLab dentro de Mattermost. Se conservarían sus entidades y
relaciones, pero se cambiaría la representación:

| GitLab | Modelo intermedio | Mattermost / capa adaptativa |
|---|---|---|
| Issue | `work_item` | resumen, estado y siguiente decisión |
| Merge Request | `change_proposal` | mapa de cambios, revisores y bloqueos |
| Pipeline | `execution_state` | línea temporal de éxito/fallo/reintento |
| Comment | `evidence_or_question` | conversación ligada a una fuente |
| Approval | `explicit_confirmation` | confirmación trazable |

### Automatización propuesta

1. GitLab emite un webhook firmado o autenticado.
2. El adaptador valida proyecto, evento, versión e identidad de la superficie.
3. Se normalizan sólo entidades necesarias; no se copia todo GitLab.
4. Se construye un grafo local con procedencia hacia el `project`, `issue` o
   `merge_request` original.
5. La política elige resumen, mapa, timeline o explicación relacional.
6. Mattermost recibe una representación con fuente, incertidumbre y acciones
   posibles.
7. Una acción sensible requiere confirmación explícita y usa la API de GitLab.
8. El verificador consulta nuevamente GitLab y sólo entonces declara el efecto.

### Problemas difíciles que deben resolverse

- eventos duplicados o fuera de orden;
- un mismo `iid` perteneciente a proyectos distintos;
- permisos diferentes entre GitLab y Mattermost;
- pipeline que cambia mientras se muestra la representación;
- comentarios que no equivalen a aprobación;
- links rotos, ramas eliminadas o merge requests cerradas;
- mensajes de Mattermost que parecen comandos pero no tienen autorización;
- no confundir “mensaje publicado” con “cambio aplicado”.

### Criterio de éxito

Con un fixture local, la capa debe poder explicar un merge request, mostrar
alternativas de representación y verificar una acción de bajo riesgo. Debe
detenerse ante identidad, permisos, versión o resultado inciertos.

La primera implementación recomendada es **read-only + dry-run**. El primer
write real debe ser publicar una notificación no sensible; aprobar, fusionar o
modificar código queda fuera hasta que exista un verificador fuerte.

## Ejemplo real 2 — OpenEMR + Nextcloud

### Por qué este par

Una clínica u hospital puede separar el sistema de registro clínico del sistema
de documentos y colaboración. OpenEMR documenta una API FHIR R4 con recursos
de pacientes, encuentros, documentos y autenticación OAuth/SMART
([FHIR API](https://github.com/openemr/openemr/blob/master/Documentation/api/FHIR_API.md),
[API overview](https://github.com/openemr/openemr/blob/master/Documentation/api/README.md)).
Nextcloud documenta APIs OCS con autenticación por app token u OIDC y operaciones
HTTP, además de sus superficies de archivos y compartición
([OCS API](https://docs.nextcloud.com/server/stable/developer_manual/client_apis/OCS/ocs-api-overview.html)).

### Desafío de adaptación

Representar el camino entre un encuentro clínico y un documento institucional
sin convertir la capa en un nuevo expediente ni duplicar información sensible:

```text
OpenEMR: encuentro/documento disponible
        ↓
relación semántica: quién puede revisar qué y por qué
        ↓
Nextcloud: archivo, carpeta, permiso o tarea correspondiente
        ↓
representación guiada para el rol autorizado
        ↓
verificación independiente de documento y permiso
```

### Restricciones

Este reto sólo puede comenzar con datos sintéticos. El adaptador debe usar
referencias opacas, mínimo privilegio, trazas minimizadas y ningún screenshot
persistente por defecto. No debe inferir diagnóstico ni recomendar decisiones
clínicas. El objetivo es navegación y coordinación documental, no asistencia
médica.

### Verificador

No basta con ver un banner de éxito. Hay que comprobar por API:

```text
document_reference válido
→ archivo esperado en Nextcloud
→ permiso esperado
→ hash o versión coincidente
→ actor y timestamp registrados
```

Si cualquiera falla, la salida es `UNKNOWN` o `REFUTED`, nunca `SUCCESS`.

### Por qué este segundo par es importante

Si la arquitectura sólo funciona en GitLab y Mattermost, puede ser un bot de
integración. Si conserva sus contratos al pasar a OpenEMR y Nextcloud, empieza
a demostrar que existe una capa general de representación y verificación.

## Contrato mínimo de adaptador

Todo primer producto debe exigir a cada plugin:

```text
SurfaceDescriptor
  tipo, instancia, versión, usuario y permisos

EntityRef
  tipo, id estable, fuente, versión y sensibilidad

Relation
  origen, destino, tipo, confianza y procedencia

ActionProposal
  precondiciones, alcance, reversibilidad y confirmación requerida

OutcomeVerifier
  consulta independiente, resultado esperado y clasificación final
```

El producto no debería tener una base de datos infinita como cerebro. Debe
conservar un registro acotado de fuentes, relaciones, patches y resultados;
para conocimiento externo, cada institución decide qué conector y qué fuente
autoriza.

## Cómo crece sin quedar encerrado

```text
núcleo semántico
    ↓
contrato de adaptadores
    ↓
primer par de aplicaciones
    ↓
segundo par de otro dominio
    ↓
SDK de plugins y verificadores
    ↓
paquetes institucionales
```

El primer producto puede ser un kit local que una dos aplicaciones existentes,
ofrezca representaciones alternativas y verifique los cambios. No necesita
ser propietario de ninguna de las aplicaciones ni reemplazarlas.

## Prioridad de implementación

### Ahora

- ~~fixture GitLab/Mattermost totalmente sintético~~ — implementado en
  [experimento 065](../../experiments/065-farmaxia-cross-application-evidence/README.md);
- ~~eventos, procedencia e idempotencia~~ — duplicados, orden temporal e
  identidad calificada verificados;
- ~~representación read-only~~ — claims con referencias a GitLab;
- ~~dry-run de acciones~~ — propuesta con precondiciones y confirmación;
- ~~verificador de estado~~ — consulta independiente al almacén fuente;
- ~~fallos de identidad, permisos y versión~~ — kill tests reproducibles.
- ~~replay temporal batch~~ — el orden de llegada ya no cambia la proyección;
  correcciones, conflictos y `UNKNOWN` quedan diferenciados en
  [experimento 066](../../experiments/066-farmaxia-temporal-evidence-replay/README.md).
- ~~watermarks y eventos tardíos~~ — los eventos fuera de ventana se conservan,
  reabren la proyección y se comparan con replay batch en
  [experimento 067](../../experiments/067-farmaxia-watermark-late-event-replay/README.md).
- ~~atajo de infraestructura~~ — se compararon CloudEvents, OpenLineage,
  Flink, Kafka Streams, EventSourcingDB, OPA, OpenFGA y Automerge. El núcleo
  local se conserva pequeño y la adopción queda condicionada a un adapter real
  en [decisión 074](../decisions/074-consolidated-foundations-shortcut.md).

### Después

- ~~fixture CloudEvents local~~ — el sobre estándar conserva identidad,
  procedencia y el evento interno sin red ni dependencia en
  [experimento 068](../../experiments/068-farmaxia-cloudevents-envelope/README.md);
- ~~primer adapter sobre el estándar~~ — CloudEvents alimenta el puente
  GitLab–Mattermost sin copiar su compilador, con procedencia y `DRY_RUN_ONLY`
  verificados en [experimento 069](../../experiments/069-farmaxia-cloudevents-cross-application-adapter/README.md).
- ~~segundo par de superficies~~ — OpenEMR y Nextcloud sintéticos reutilizan el
  mismo núcleo de CloudEvents, evidencia, procedencia, permisos y verificación
  en [experimento 070](../../experiments/070-farmaxia-openemr-nextcloud-adapter/README.md).
- ~~tercera superficie no institucional ni documental~~ — el adapter de parche
  CODE-INE reutiliza el mismo núcleo y añade sólo hash base, precondición y
  previsualización en [experimento 071](../../experiments/071-farmaxia-codeine-patch-adapter/README.md);
- ~~auditoría de media~~ — el [experimento 072](../../experiments/072-farmaxia-media-timeline-adapter/README.md)
  demostró una diferencia real en reloj de media, rangos, codec y sincronía,
  conservando el núcleo y sin justificar aún un renderer completo;
- ~~puente de representaciones media~~ — OTIO-style se normaliza como completo
  y ffprobe-style se abstiene como `PARTIAL_UNKNOWN` en el [experimento 073](../../experiments/073-farmaxia-media-representation-bridge/README.md);
- ~~composición de sidecar editorial~~ — ffprobe-style se completa sólo cuando
  coinciden identidad, hash y versión, con rangos exactos y política read-only,
  en el [experimento 074](../../experiments/074-farmaxia-media-sidecar-composition/README.md);
- ~~conflicto entre sidecars~~ — dos sidecars individualmente válidos pero con
  claims distintos producen `CONFLICT`, preservan ambos historiales y no
  seleccionan silenciosamente en el [experimento 075](../../experiments/075-farmaxia-media-sidecar-conflict-audit/README.md);
- ~~adopción de herramienta real Windows~~ — `pywinauto 0.6.9` con backend UIA
  enumeró ventanas y controles del desktop real en modo read-only en el
  [experimento 076](../../experiments/076-farmaxia-pywinauto-uia-adapter/README.md);
- ~~inventario de aplicaciones reales~~ — Excel `16.0` respondió por COM local y
  Blender `5.1.1` por su API Python en modo background; el
  [experimento 077](../../experiments/077-farmaxia-excel-blender-capability-inventory/README.md)
  confirma que UIA debe combinarse con estado nativo y no sustituye el modelo
  interno de cada aplicación;
- ~~kernel de transición nativa~~ — en sesiones efímeras reales, Excel y Blender
  observaron `create → select → modify → revert`, incluyendo cálculo de fórmula,
  selección de objeto, modificación espacial y restauración del contexto en el
  [experimento 078](../../experiments/078-farmaxia-native-transition-probe/README.md);
- ~~observer de input consentido~~ — una ejecución real observó actividad de
  teclado por conteo, aplicación allowlisted y rol UIA enfocado (`firefox:Group`)
  sin títulos, texto, teclas ni píxeles en el
  [experimento 079](../../experiments/079-farmaxia-consented-input-semantic-bridge/README.md);
- ~~correlación input/delta nativo~~ — Excel real produjo tres deltas en un
  scratch no guardado y, al no existir input humano, todos quedaron como
  `unassociated_native_delta`; el modo live queda preparado para asociaciones
  candidatas en el [experimento 080](../../experiments/080-farmaxia-input-native-delta-correlation/README.md);
- ~~prueba de ventana proxy~~ — una ventana propia fue capturada con
  `Windows.Graphics.Capture`, cuatro regiones fueron reordenadas y un clic
  reubicado volvió a la fuente mediante la transformación inversa en el
  [experimento 081](../../experiments/081-farmaxia-window-proxy-sandbox/README.md).
  Esto valida el renderer proxy como base, pero no input entre procesos ni
  reconocimiento semántico universal.
- preview pasivo de ventana externa — el experimento 082 ya compila el selector
  seguro y separa `BuildOnly` de la ejecución interactiva. La selección real y
  la observación de frames quedan pendientes de una ejecución manual con
  consentimiento.
- autorización por rol;
- redacción y retención mínima;
- pruebas de conflicto y fallos parciales;
- evaluación comparativa de resumen, mapa y guía.
- correlacionar input humano autorizado con un delta nativo de Excel o Blender,
  sin confundir actividad física con intención;
- medir el retardo entre input, UIA y delta nativo en una sesión humana
  explícitamente autorizada;
- construir una vista proxy en modo preview para una ventana seleccionada,
  usando UIA/OCR sólo como propuestas de regiones y sin interceptar input por
  defecto;

### Más adelante

- otros pares institucionales;
- plugins declarativos;
- adaptación de documentos, código, media y desktop;
- agente que proponga representaciones, sin autoridad para ejecutar por sí solo.

## Kill tests

- Si una acción no tiene fuente, identidad y postcondición, no se ejecuta.
- Si una representación altera el significado de una entidad o relación, se
  rechaza aunque sea más fácil de leer.
- Si Mattermost confirma un mensaje pero GitLab no cambió, el resultado no es
  éxito.
- Si el adaptador mezcla dos proyectos, pacientes, instancias o usuarios, se
  detiene.
- Si una API exige permisos superiores a los declarados, se bloquea.
- Si el sistema necesita capturar toda la pantalla para resolver un evento
  estructurado, se considera degradación y debe quedar registrada.
- Si el segundo par exige alterar el núcleo en vez de añadir un adapter, la
  abstracción es insuficiente.
- Si una mejora sólo reduce clicks pero empeora recuperación, trazabilidad o
  control, se descarta.

## Investigación de base

La idea combina interacción mixta, teoría de búsqueda de información,
compresión condicionada por tarea, analogía relacional, provenance y
verificación selectiva. No se presenta como una teoría clínica ni como prueba
de estados mentales. El agente puede proponer; la institución conserva la
autoridad, los permisos y el criterio de éxito.
