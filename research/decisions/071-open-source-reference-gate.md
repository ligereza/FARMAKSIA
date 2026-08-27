# Decisión 071 — compuerta de adopción de referencias externas

**Fecha:** 2026-08-27
**Estado:** adoptada
**Frentes:** CODE-INE, X-ANA-X, VIZZ, RepresentationSpace

## Decisión

FARMAKSIA no incorporará la lista externa como una colección de dependencias.
Cada referencia deberá pasar por una compuerta de capacidad, evidencia,
procedencia, seguridad y reemplazabilidad.

```text
referencia → capacidad concreta → contrato local → prueba → adopción limitada
```

El repositorio propio continúa siendo la autoridad para:

- significado y consultas críticas;
- procedencia y versión de fuente;
- planes de representación;
- privacidad y capacidades autorizadas;
- preview, commit, undo y rollback;
- verificación de resultado;
- clasificación `verified`, `refuted` y `unknown`.

Un proyecto externo puede implementar una pieza, pero no puede redefinir esos
contratos por defecto.

## Capas de adopción

### Capa A — núcleo inmediato

- **RFC 6902:** formato de patch para cambios declarativos, revisión y undo.
- **WAI:** restricciones de accesibilidad, teclado, movimiento y
  personalización.
- **DTCG 2025.10:** vocabulario portable de tokens visuales; se documentará
  como Community Group Report, no como estándar W3C.
- **Pydantic:** candidato para validar fronteras de runtime cuando los
  diccionarios actuales se conviertan en modelos versionados.
- **Hypothesis:** candidato de desarrollo para generar estados adversariales y
  probar leyes de representación; no es dependencia de distribución.

No se instala nada de esta capa sólo por prestigio. Cada incorporación debe
reemplazar una validación duplicada o hacer visible un fallo que antes podía
pasar silenciosamente.

### Capa B — adaptadores condicionados

Se habilitarán sólo cuando exista una superficie concreta y un fixture que la
necesite:

- Tree-sitter para anclas sintácticas de CODE-INE;
- Playwright + CDP/ARIA para una superficie web;
- UI Automation/pywinauto para una superficie Windows;
- Windows Graphics Capture para geometría/composición VIZZ;
- Style Dictionary para exportar tokens a varios renderers;
- NetworkX para operaciones de grafo que superen las estructuras locales;
- Submodlib para selección a escala que permita comparar contra el greedy 064;
- OR-Tools para restricciones explícitas de layout o scheduling.

Cada adapter debe declarar identidad de superficie, permisos, datos que lee,
datos que persiste, tiempo de vida, apagado, fallback y verificador. Si falta
uno de esos campos, el adapter no se activa.

### Capa C — investigación separada

OSWorld, Windows Agent Arena, OpenCUA, Computer Agent Arena, OpenAdapt Evals,
OpenAdapt ML, OpenAdapt Retrieval, OpenAdapt Grounding, OmniParser y UFO se
mantienen fuera del runtime. Se pueden leer, comparar o reproducir en un
entorno aislado; no se convierten en dependencias del producto.

La política vigente de FARMAKSIA también prohíbe descargar pesos o datasets
desde Hugging Face para este frente. Un repositorio GitHub reputado no convierte
automáticamente sus modelos o datos externos en material aprobado.

## Gates obligatorios

Antes de añadir una dependencia o corpus:

1. **Capacidad:** ¿qué operación concreta habilita?
2. **Contrato:** ¿qué entrada/salida tipada produce?
3. **Evidencia:** ¿qué medición mejora y cómo se falsaría?
4. **Identidad:** ¿cómo se sabe que observa la superficie correcta?
5. **Privacidad:** ¿qué queda local, qué persiste y qué sale del equipo?
6. **Licencia:** ¿se revisaron código, dependencias, assets, modelos y datos?
7. **Reemplazo:** ¿FARMAKSIA conserva un camino mínimo sin ella?
8. **Costo:** ¿latencia, VRAM, CPU, almacenamiento o complejidad son
   proporcionales a la medición?
9. **Kill test:** ¿qué resultado bloquea la adopción?

La instalación por sí sola no cuenta como avance.

## Criterio para aprender de interacción

No se aceptará ninguna de estas inferencias sin un diseño humano explícito:

```text
click = comprensión
primera opción = preferencia
tiempo visible = utilidad
abandono = fracaso de contenido
posición = relevancia
repetición = aprendizaje
```

El evento local debe registrar exposición, orden, alternativa disponible,
input explícito y resultado verificable. Si en el futuro se aprende de slates,
se deberá conservar política de logging y propensities; de lo contrario, la
selección sólo será una política de presentación, no un modelo de preferencia.

## Consecuencias por compuesto

### CODE-INE

Prioridad: contrato tipado → patch → ancla Tree-sitter → preview → oracle.
OpenAdapt Flow se usa como referencia de gobernanza, especialmente por separar
compilación determinista, reparación acotada, halt y verificación independiente.
No se importa un agente VLM para compensar una fuente o un oracle débiles.

### X-ANA-X

Prioridad: `source_ref` → alineamiento relacional → predicción → diferencia →
ruptura. Structure-Mapping y provenance son las referencias conceptuales
principales. Una superficie bonita sin mapeo verificable queda `unavailable`.

### VIZZ

Prioridad: capa sin cámara → capacidades de teclado/mouse/foco → geometría
declarada → adapter UIA/CDP/Playwright/pywinauto cuando corresponda →
cámara/eye tracking sólo como capacidad opt-in. Ninguna señal ocular se usará
para inferir diagnóstico, intoxicación, comprensión o emoción.

### RepresentationSpace

La facility-location de 064 permanece como baseline. MMR queda como control de
redundancia. El próximo avance debe medir exposición y resultado del plan, no
reemplazar el selector por una librería más grande.

## Siguiente trabajo autorizado

El contrato de adopción consolidada queda descrito en la
[decisión 074](074-consolidated-foundations-shortcut.md) y su fixture local fue
verificado en el [experimento 068](../../experiments/068-farmaxia-cloudevents-envelope/README.md).
El adapter sintético ya fue verificado en el [experimento 069](../../experiments/069-farmaxia-cloudevents-cross-application-adapter/README.md).
El segundo par sintético fue verificado en el
[experimento 070](../../experiments/070-farmaxia-openemr-nextcloud-adapter/README.md).
El siguiente paso es auditar una superficie de código o media sin instalar
agentes externos. No se inicia todavía una captura humana, un benchmark en
VM, una descarga de modelos ni una instalación de agentes.

El segundo adapter deberá conservar las mismas preguntas que ya respondió el
fixture y el primer adapter:

```text
qué se mostró
por qué se mostró
qué fuente lo respalda
qué input explícito ocurrió
qué quedó desconocido
qué efecto fue verificado
```

## Kill tests de esta decisión

- Si una dependencia exige red, telemetría opaca o modelo no auditable para el
  camino sano, queda fuera del núcleo.
- Si un peso o dataset no tiene términos y procedencia individuales, no se
  descarga ni se distribuye.
- Si el adapter no puede apagarse o conservar un fallback mínimo, no se adopta.
- Si una representación no conserva las consultas críticas de 063, queda
  inválida aunque mejore estética, velocidad o clicks.
- Si una política aprendida usa exposición o posición como relevancia sin
  propensities, se bloquea.
- Si una mejora sólo aparece en frames mezclados o en la misma sesión, no se
  acepta como evidencia de generalización.

## Fuentes

- [Auditoría completa de referencias 023](../literature/023-open-source-reference-audit.md)
- [RFC 6902](https://www.rfc-editor.org/rfc/rfc6902)
- [DTCG 2025.10](https://www.designtokens.org/TR/2025.10/)
- [OpenAdapt Flow](https://github.com/OpenAdaptAI/openadapt-flow)
- [OpenAdapt Grounding](https://github.com/OpenAdaptAI/openadapt-grounding)
- [Google: relevance and bias](https://research.google/pubs/towards-disentangling-relevance-and-bias-in-unbiased-learning-to-rank/)
