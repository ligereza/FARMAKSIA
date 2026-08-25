# Decisión 065 — X-ANA-X como compilador de tutoriales transferibles

Fecha: 2026-08-25
Estado: Propuesta aplicada; no reabre el archivo de X-ANA-X como novedad computacional

## Pregunta

¿Qué necesita X-ANA-X para convertir documentación pública en una guía ejecutable
y para unir tutoriales de dos aplicaciones distintas sin confundir una analogía
con una acción segura?

## Respuesta corta

Una página pública o un PDF basta para producir un **borrador de enseñanza** si
contiene objetivo, conceptos, prerrequisitos, pasos, versión y evidencia de
origen. No basta para automatizar una aplicación. La automatización necesita
observar el estado actual, seleccionar un adaptador compatible, ejecutar una
acción con permiso y comprobar una postcondición.

La unidad que X-ANA-X debe transferir no es una frase sino un contrato:

```text
objetivo → precondición → acción → observación esperada → postcondición → verificador
```

Un tutorial compuesto tampoco se obtiene pegando dos listas. Se compone mediante
un puente explícito entre el estado final de la aplicación A y el estado inicial
de la aplicación B.

## Evidencia técnica revisada

### Documentos no son estado de aplicación

Microsoft UI Automation expone un árbol de controles, propiedades, eventos y
patrones de interacción para aplicaciones Windows fuera del proceso del
agente. Esto permite comprobar que un botón, campo o selección existe y que la
aplicación acepta una operación, en vez de inferirlo sólo desde una captura:

- [UI Automation Overview](https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-uiautomationoverview)
- [UI Automation Control Patterns](https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-controlpatternsoverview)

Para la web, Playwright recomienda locators semánticos y reintentos con espera
automática; su generador puede registrar acciones y aserciones. Eso es útil
para aprender un flujo observado, pero los selectores siguen necesitando una
verificación del estado posterior:

- [Playwright Locators](https://playwright.dev/docs/locators)
- [Playwright Test Generator](https://playwright.dev/docs/codegen)

Los agentes de interfaz como [UFO](https://github.com/microsoft/UFO) separan la
coordinación entre aplicaciones de los adaptadores específicos de cada app y
combinan información de controles con visión cuando la interfaz no es
semánticamente accesible. [OSWorld](https://arxiv.org/abs/2404.07972) muestra por
qué la evaluación debe ocurrir en aplicaciones y estados reales, no sólo sobre
texto documental.

### Un PDF requiere extracción con procedencia

La primera versión puede usar [MarkItDown](https://github.com/microsoft/markitdown)
o PyMuPDF para extraer texto y bloques. Para PDFs donde importan tablas,
jerarquía, figuras o coordenadas, [Docling](https://github.com/docling-project/docling)
ofrece una representación documental unificada. Ningún parser convierte
automáticamente una instrucción ambigua en una acción segura; cada paso debe
conservar página/sección, versión, URL, hash de recuperación y nivel de
confianza.

### Las aplicaciones creativas necesitan adaptadores nativos

En Blender existe una API Python (`bpy`) pero sus operadores dependen del
contexto activo y pueden fallar aunque la frase del tutorial sea correcta:

- [Blender Python API Quickstart](https://docs.blender.org/api/main/info_quickstart.html)

Maya ofrece `maya.cmds` y una Python API propia; sus objetos no deben asumirse
intercambiables con los de Blender:

- [Maya Python API 2.0](https://help.autodesk.com/cloudhelp/2025/ENU/MAYA-API-REF/py_ref/index.html)
- [Using Python in Maya](https://help.autodesk.com/cloudhelp/2024/ENU/Maya-Scripting/files/GUID-55B63946-CDC9-42E5-9B6E-45EE45CFC7FC.htm)

La conclusión práctica es priorizar API/command adapters cuando existan, usar
UI Automation o Playwright cuando la app lo permita y reservar visión o
coordenadas de pantalla como fallback frágil.

## Decisión

Construir X-ANA-X como un **compilador de tutoriales transferibles** con cinco
capas y tres estados de confianza:

```text
fuente pública
    ↓
extractor con procedencia
    ↓
grafo de conceptos y unidades de tarea
    ↓
adaptador de aplicación + contrato de estado
    ↓
puente entre aplicaciones + verificador
    ↓
enseñanza / dry-run / ejecución opt-in
```

Estados de confianza:

1. `TEACHING_DRAFT`: los documentos sostienen una explicación y una secuencia,
   pero no hay evidencia suficiente para operar la app.
2. `DRY_RUN_READY`: las precondiciones, acciones y postcondiciones están
   mapeadas; el sistema puede explicar qué haría y qué observaría sin ejecutar.
3. `EXECUTION_READY`: existe un adaptador permitido, el estado vivo satisface
   las precondiciones y un verificador puede confirmar cada postcondición. Si
   alguna parte es ambigua, el resultado es `UNKNOWN`, no una acción inventada.

La línea aplicada no modifica la decisión 028: X-ANA-X continúa archivado como
hipótesis independiente de operador o ventaja computacional. Esta decisión
abre una arquitectura de producto comprobable; no afirma que una analogía
mejore la comprensión humana.

## Contratos mínimos

### SourceCard

```json
{
  "source_id": "maya-official-python-2025",
  "uri": "https://...",
  "retrieved_at": "2026-08-25T00:00:00Z",
  "source_kind": "official_web|official_pdf",
  "license": "declared_or_unknown",
  "application": "maya",
  "application_version": "2025",
  "locale": "en",
  "prerequisites": ["scene_open"],
  "concepts": ["mesh", "export"],
  "steps": [
    {
      "id": "create-mesh",
      "preconditions": ["scene_open"],
      "action_family": "native_api|ui_control|browser_action|human_prompt",
      "action": "...",
      "expected_observation": "...",
      "postconditions": ["mesh_exists"],
      "evidence": {"url": "...", "section": "...", "page": 1}
    }
  ]
}
```

El extractor puede conservar un resumen y una referencia, no necesita copiar el
documento entero al corpus. Si falta versión, licencia, evidencia o una
postcondición, la tarjeta puede servir para explicar, pero queda bloqueada para
ejecución.

### TutorialUnit

```text
id
goal
input_state
concept_relation
action_family
tool_mapping
expected_state
verifier
risk
evidence
```

`concept_relation` distingue `equivalent`, `analogous`, `different` y
`unknown`. Una analogía de “construction history” de Maya con “modifier stack”
de Blender puede orientar la enseñanza, pero no se etiqueta como equivalencia
ni se usa sola para disparar comandos.

### BridgeContract

```text
from_application
from_state
artifact_or_transform
assumptions
to_application
to_state
verifier
residue
```

Ejemplo Maya→Blender:

```text
Maya: mesh_exists + object_named + export_completed
  -- FBX/OBJ explícito; unidades, ejes, escala y materiales declarados -->
Blender: artifact_imported + mesh_exists + scale_checked + object_selected
```

Si no existe el archivo, el formato no es compatible o no se puede verificar la
escala, X-ANA-X debe detenerse en `BRIDGE_BLOCKED`. No debe rellenar el hueco
con “equivalencias” lingüísticas.

## Qué significa que una página o PDF sea suficiente

| Uso | ¿Documento solo? | Evidencia adicional requerida |
|---|---:|---|
| Glosario y explicación | Sí, si tiene origen y versión | Citas y límites |
| Borrador de pasos | Generalmente sí | Prerrequisitos y resultado esperado |
| Dry-run | No | Contratos de estado y mapeo de adaptador |
| Ejecución en una app | No | Estado vivo, permisos, adaptador y verificador |
| Unión de dos apps | No | Artefacto/transformación y contrato puente |
| Recuperación ante fallo | No | Diagnóstico observable y acción reversible |

Una página puede describir “exportar el modelo”, pero no dice necesariamente
qué ventana está activa, si el archivo ya existe, qué unidades usa la escena,
si el menú cambió de versión o si el usuario quiere sobrescribir un archivo.
Esas variables pertenecen al estado y al consentimiento, no a la explicación.

## Flujo de ejecución propuesto

```text
1. Registrar objetivo del usuario y aplicaciones permitidas.
2. Ingerir fuentes con URL/hash/versión y extraer SourceCards.
3. Normalizar conceptos y convertir pasos en TutorialUnits.
4. Resolver cada unidad contra un AppAdapter disponible.
5. Construir BridgeContracts sólo cuando exista estado/artefacto compatible.
6. Mostrar plan, analogías, fuentes y riesgos.
7. En dry-run: simular acciones y evaluar verificadores.
8. En ejecución opt-in: comprobar precondición → ejecutar una acción → verificar.
9. Ante conflicto, falta de estado o acción destructiva: pausar y devolver UNKNOWN.
10. Guardar trazabilidad de fuente, acción, observación y postcondición.
```

El coordinador puede seguir el patrón HostAgent/AppAgent de UFO, pero FARMAXIA
no debe adoptar UFO como dependencia todavía. Primero se necesita probar el
contrato localmente y decidir qué superficie de control es confiable para cada
familia de aplicaciones.

## Open source que sí conviene estudiar/adaptar

| Problema | Referencia | Adopción propuesta |
|---|---|---|
| Web semántica y espera | Playwright | Adaptador web opt-in; locators y aserciones |
| Windows nativo | Microsoft UI Automation | Adaptador de observación y patrones de control |
| Coordinación multi-app | UFO | Patrón arquitectónico; no dependencia inmediata |
| Evaluación en estado real | OSWorld | Inspiración para fixtures y verificación por tarea |
| Extracción documental | MarkItDown/PyMuPDF/Docling | Empezar ligero; escalar a layout cuando sea necesario |
| DCC creativas | APIs oficiales Maya/Blender | Adaptadores nativos antes que clicks por coordenadas |

No se descargan modelos ni repositorios en este ciclo. La adopción queda sujeta
al contrato de procedencia, licencia, versión fijada, superficie mínima y kill
tests. Se excluyen corpus arbitrarios.

## Requisitos no funcionales y límites

- **Privacidad:** ingestión local por defecto; no capturar pantalla, cámara,
  teclado o archivos personales si no son necesarios para el tutorial.
- **Control:** lectura y dry-run antes de cualquier acción; ejecución opt-in;
  confirmación específica para exportar, sobrescribir, borrar o publicar.
- **Determinismo:** cada unidad debe poder ejecutarse en una fixture conocida y
  producir un estado verificable.
- **Portabilidad:** los conceptos se pueden transferir; los comandos no se
  transfieren sin adaptador.
- **Auditoría:** cada hecho debe conservar su fuente y cada acción su observación.
- **Honestidad:** una ruta que explica mejor no demuestra eficacia humana; una
  ruta que ejecuta no demuestra comprensión.

## Kill tests

1. Una SourceCard sin postcondición nunca alcanza `DRY_RUN_READY`.
2. Un tutorial compuesto sin `BridgeContract` nunca cruza de la app A a la B.
3. Una acción sin adaptador o sin verificador devuelve `UNKNOWN`.
4. Un cambio de versión no declarado invalida la ejecución, aunque el texto siga
   siendo semánticamente parecido.
5. Si la analogía y la ruta directa generan exactamente la misma decisión en un
   caso donde se esperaba una relación exclusiva, no se declara novedad de
   X-ANA-X; se conserva como explicación o state augmentation.

## Próximos pasos

1. Ejecutar el experimento 059 con tarjetas declarativas y un puente Maya→Blender
   sin abrir aplicaciones ni usar red.
2. Implementar un extractor local para una página oficial y un PDF oficial,
   almacenando sólo metadatos, resúmenes y evidencia.
3. Implementar un adaptador de observación web con Playwright y un adaptador
   Windows UIA de sólo lectura.
4. Añadir un dry-run que muestre el plan, sus analogías, sus puentes y sus
   verificadores antes de permitir acciones.
5. Reabrir la hipótesis computacional sólo si aparece una predicción relacional
   que cambie una decisión observable frente a un control directo más fuerte.

## Desconocidos

- Qué cobertura real tendrán UIA y APIs nativas en aplicaciones con canvas,
  plugins o interfaces personalizadas.
- Cuánta ambigüedad documental queda después de extraer tablas, imágenes y
  versiones.
- Si los puentes entre aplicaciones creativas requieren conversores propios,
  validación geométrica o intervención humana.
- Si una representación analógica aporta valor a una persona; eso requiere un
  protocolo humano posterior y no se infiere de este experimento.
