# Research 023 — auditoría profunda de referencias externas

**Fecha:** 2026-08-27
**Entrada:** lista de 66 referencias y 9 organizaciones compartida para
auditar FARMAKSIA  
**Alcance:** CODE-INE, X-ANA-X, VIZZ, RepresentationSpace y la capa común de
representación

## Veredicto

La lista es valiosa, pero no es todavía un plan de instalación. Mezcla cuatro
cosas distintas:

```text
dependencia reutilizable
      ≠ adaptador de plataforma
      ≠ benchmark o dataset
      ≠ evidencia científica / hipótesis de diseño
```

El patrón externo que sí merece entrar en FARMAKSIA es:

```text
fuente → contrato tipado → representación declarativa → interacción reversible
      → evidencia de exposición → verificador independiente
```

Esto coincide con la dirección ya adoptada en 063–064, pero la auditoría cambia
la prioridad: no se instalarán todos los proyectos ni se usarán clicks como
proxy de utilidad. La próxima unidad de trabajo será un **contrato de evidencia
de representación**, no otra colección de widgets ni otro agente autónomo.

## Cómo se hizo la auditoría

Se leyó la lista completa, incluyendo sus notas de licencia, y cada grupo se
contrastó con la fuente primaria disponible: repositorio oficial, documentación
del mantenedor, estándar o publicación académica. Se registró por separado:

1. problema que resuelve;
2. madurez declarada por el propio proyecto;
3. unidad que sería reutilizable en FARMAKSIA;
4. dependencia técnica, corpus, modelo o infraestructura que exigiría;
5. riesgo de confundir una señal de interacción con comprensión o corrección;
6. condición que debe cumplirse antes de adoptar.

“Licencia apta para uso comercial” no significa “aprobado para integrar”. La
licencia del repositorio no necesariamente cubre dependencias transitivas,
pesos, datasets, fuentes, iconos, marcas ni servicios externos. La revisión
legal de distribución sigue pendiente.

## Correcciones importantes a la lista original

| Afirmación o atajo | Resultado de la revisión | Consecuencia |
|---|---|---|
| A2UI como protocolo listo para producto | El repositorio se declara **early-stage public preview** y su especificación sigue evolucionando | Estudiarlo como transporte agente→renderer; no convertirlo en contrato semántico estable |
| DTCG 2025.10 como estándar W3C | Es un **Stable Final Community Group Report**, no un W3C Standard ni está en el W3C Standards Track | Usarlo como vocabulario portable de tokens; no venderlo como estándar W3C |
| OpenTelemetry como esquema completamente estable | En OpenTelemetry Python, traces y metrics figuran como estables; logs siguen en desarrollo | Mantener un esquema FARMAKSIA local y exportar sólo cuando el evento esté congelado |
| “OpenAdapt” como una única pieza | La organización separa `openadapt-flow`, capture, grounding, ML, retrieval, privacy y evals, con estados diferentes | Citar y evaluar el repositorio exacto; estudiar `flow` y capture, no importar el ecosistema completo |
| OpenCUA y OmniParser como código automáticamente reutilizable | Los repositorios separan código, pesos y datos; varios modelos se distribuyen desde Hugging Face y OmniParser declara términos mixtos para sus componentes | No descargar pesos ni datos; estudiar arquitectura y usar sólo código con licencia y procedencia revisadas |
| Progressive Formalization como una única referencia | La etiqueta mezcla trabajos distintos de Shipman/Marshall | Citar el trabajo exacto según la afirmación: informalidad inicial, formalización incremental o substrate |
| Choice overload como ley | Dos meta-análisis encuentran resultados condicionados o efecto medio casi nulo | No penalizar opciones por cantidad sola; medir tarea, dificultad, preferencia e incertidumbre |
| Click o primera rama elegida como preferencia | La literatura de unbiased LTR muestra position bias y confusión entre relevancia y exposición | Registrar exposición y propensities antes de aprender de una elección |
| “Comercial” como despeje legal | GitHub explica que la licencia es lo que concede permisos; sin licencia aplican derechos de autor por defecto | Crear un inventario de componentes, versiones y avisos antes de distribuir |

Fuentes primarias especialmente relevantes: [A2UI](https://github.com/a2ui-project/a2ui),
[DTCG 2025.10](https://www.designtokens.org/TR/2025.10/),
[OpenTelemetry Python](https://github.com/open-telemetry/opentelemetry-python),
[OpenAdapt Flow](https://github.com/OpenAdaptAI/openadapt-flow),
[OpenAdapt Capture](https://github.com/OpenAdaptAI/openadapt-capture),
[OpenCUA](https://github.com/xlang-ai/OpenCUA),
[OmniParser](https://github.com/microsoft/OmniParser) y la guía de
[licencias de GitHub](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-a-license-to-a-repository).

## Matriz completa de utilidad

Las etiquetas significan:

- **NÚCLEO SIGUIENTE:** se puede convertir en contrato o prueba local sin
  añadir una plataforma pesada;
- **ADAPTADOR CONDICIONADO:** útil cuando exista esa superficie, escala o tarea;
- **REFERENCIA:** se extrae diseño, matemática o método, no código de runtime;
- **RESEARCH-ONLY:** necesita modelos, VMs, datasets o una madurez que no
  corresponde al núcleo actual;
- **NO ADOPTAR AHORA:** la idea puede ser útil, pero la forma propuesta es
  demasiado ambigua, riesgosa o prematura.

### A. Piezas técnicas open source

| # | Referencia | Lectura técnica | Decisión |
|---:|---|---|---|
| 1 | [Pydantic](https://github.com/pydantic/pydantic) | Validación desde type hints, discriminated unions y JSON Schema. La licencia principal observada es MIT. | **NÚCLEO SIGUIENTE**, cuando `RepresentationPlan`, `Patch` y `EvidenceEvent` sean fronteras de runtime. No reemplaza las invariantes semánticas. |
| 2 | [NetworkX](https://github.com/networkx/networkx) | Manipulación de grafos, paths y consultas. BSD-3-Clause. | **ADAPTADOR CONDICIONADO**. El fixture actual cabe en estructuras estándar; no adoptar para aparentar que un grafo es comprensión. |
| 3 | [Hypothesis](https://github.com/HypothesisWorks/hypothesis) | Property-based testing con generación de casos extremos y shrinking; el repo declara MPL-2.0 para su código propio, con excepciones señaladas. | **NÚCLEO SIGUIENTE DEV** para `apply/compare/commit/revert`, invariantes y máquinas de estado. No es dependencia de distribución. |
| 4 | [OR-Tools](https://github.com/google/or-tools) | CP-SAT, programación lineal, redes y optimización combinatoria; Apache-2.0. | **ADAPTADOR CONDICIONADO**. Sólo si aparecen restricciones reales de layout, scheduling o asignación; no para generar creatividad. |
| 5 | [Tree-sitter](https://github.com/tree-sitter/tree-sitter) | Árbol sintáctico incremental, tolerante a errores y actualizado durante la edición; MIT. | **ADAPTADOR CODE-INE** cuando exista un flujo de código real que necesite anclaje AST. Es preferible a colorear texto por heurística. |
| 6 | [Submodlib](https://github.com/decile-team/submodlib) | Implementaciones escalables de funciones submodulares para summarization y subset selection; MIT. | **CONDICIONADO A ESCALA**. El greedy propio de 064 es más auditable para fixtures pequeños; comparar contra Submodlib cuando haya cientos/miles de candidatos. |
| 7 | [Playwright](https://github.com/microsoft/playwright) | Automatización y snapshots de Chromium, Firefox y WebKit; Apache-2.0. | **ADAPTADOR WEB**. Puede aportar DOM/ARIA y actionability, pero no es un automatizador de escritorio ni una prueba de efecto semántico. |
| 8 | [axe-core](https://github.com/dequelabs/axe-core) | Auditoría automática de accesibilidad HTML; MPL-2.0 y avisos de terceros. Marca casos incompletos para revisión manual. | **GATE WEB**. Sirve para bloquear regresiones, no para afirmar que una representación es comprensible. |
| 9 | [OpenTelemetry Python](https://github.com/open-telemetry/opentelemetry-python) | Traces y metrics estables; logs con estado de desarrollo en el repositorio. Apache-2.0. | **REFERENCIA DE EXPORTACIÓN**. Primero congelar eventos locales y privacidad; después mapearlos a semantic conventions. |
| 10 | [pywinauto](https://github.com/pywinauto/pywinauto) | Automatización Win32/UI Automation y lectura de controles; BSD-3-Clause. | **ADOPTADO EN 076** como adapter Windows read-only. Es evidencia de plataforma, no autoridad de intención ni comprensión. |
| 11 | [A2UI](https://github.com/a2ui-project/a2ui) | Mensaje declarativo agente→cliente, IDs estables, catálogo confiable y updates incrementales; Apache-2.0, pero preview temprano. | **REFERENCIA / ADAPTADOR FUTURO**. Tomar separación datos/código y catálogo; mantener `RepresentationPlan` propio. |
| 12 | [Style Dictionary](https://github.com/style-dictionary/style-dictionary) | Compila design tokens a CSS, native y otros destinos; Apache-2.0. | **ADAPTADOR VISUAL**. Sólo después de definir tokens semánticos y límites de contraste/movimiento; no es el motor de experiencia. |
| 13 | [OpenAdapt](https://github.com/OpenAdaptAI/OpenAdapt) y [openadapt-flow](https://github.com/OpenAdaptAI/openadapt-flow) | Compila demostraciones en programas deterministas; camino sano sin llamadas de modelo, re-resolución gobernada y verificación independiente. | **REFERENCIA ARQUITECTÓNICA PRIORITARIA**. Tomar record→compile→gate→replay→verify; no incorporar su runtime completo. |
| 14 | [OpenAdapt Evals](https://github.com/OpenAdaptAI/openadapt-evals) | Infraestructura de investigación para comparar replay/agent, silent wrong-action, over-halt, costo y latencia. | **RESEARCH-ONLY** hasta que exista un backend y un verificador FARMAKSIA. Extraer la taxonomía de fallos. |
| 15 | [Microsoft UFO/UFO³](https://github.com/microsoft/UFO) | Arquitectura amplia de agentes Windows, coordinación y DAGs multi-dispositivo; MIT, con marcas y disclaimers. | **REFERENCIA**. No copiar un agente general; estudiar separación planner/adapter/actuator y límites de autoridad. |

### B. Benchmarks, datasets y trayectorias

| # | Referencia | Qué puede enseñar | Decisión |
|---:|---|---|---|
| 16 | [OSWorld / Verified](https://github.com/xlang-ai/OSWorld) | Tareas de escritorio, ambientes y verificadores en computadoras reales; requiere infraestructura externa. | **RESEARCH-ONLY**. Usar como fuente de diseño de tareas/verify, no como dependencia ni corpus automático. |
| 17 | [Windows Agent Arena](https://github.com/microsoft/WindowsAgentArena) | Benchmark Windows multimodal reproducible mediante VMs/cloud; MIT. | **RESEARCH-ONLY**. Útil para un futuro adapter Windows; demasiado grande para el laboratorio local actual. |
| 18 | [OpenCUA](https://github.com/xlang-ai/OpenCUA) | Modelos, trayectorias, anotación y benchmark para computer-use; la documentación vincula modelos/datos externos. | **RESEARCH-ONLY**. No descargar HF ni aceptar pesos/datasets como si fueran código MIT. |
| 19 | [Computer Agent Arena](https://github.com/xlang-ai/computer-agent-arena) | Comparación humana side-by-side, votos y Elo sobre agentes; MIT. | **RESEARCH-ONLY**. Su idea fuerte es el juicio comparativo, pero no sustituye una tarea con éxito verificable. |
| 20 | [OpenAdapt demonstrations/trajectories](https://github.com/OpenAdaptAI) | Grabaciones, estados, acciones y workflows para compilar o estudiar políticas. | **REFERENCIA CON PROCEDENCIA**. No ingresar demostraciones externas al corpus sin licencia, consentimiento, redacción y contrato de datos. |
| 21 | [OpenAdapt Grounding](https://github.com/OpenAdaptAI/openadapt-grounding) | Anclaje OCR local y suavizado temporal; declara que es research y que los modelos son fallback opcional. | **REFERENCIA / ADAPTADOR FUTURO**. La idea de ladder barato→caro y temporal smoothing es útil; sus cifras deben replicarse. |
| 22 | [OpenAdapt ML](https://github.com/OpenAdaptAI/openadapt-ml) | SFT, grounding, trayectorias y experimentos RL para agentes VLM; el README lo declara experimental y separado del replay determinista. | **RESEARCH-ONLY**. No usar MLP/VLM para ocultar falta de contrato, datos o verificador. |
| 23 | [OpenAdapt Retrieval](https://github.com/OpenAdaptAI/openadapt-retrieval) | Embeddings multimodales, FAISS y recuperación de demos; depende de modelos externos. | **RESEARCH-ONLY** y sin descarga de pesos HF. El patrón de recuperar precedentes puede reaparecer como índice local de metadatos declarativos. |

### C. Visión, grounding y plataforma

| # | Referencia | Lectura | Decisión |
|---:|---|---|---|
| 24 | [OmniParser](https://github.com/microsoft/OmniParser) | Convierte screenshots en regiones/interactables; el repo declara licencias distintas para código, detector heredado y modelos. | **RESEARCH-ONLY**. No integrar pesos sin auditoría individual de licencia, origen y riesgo. |
| 25 | UI Automation / accessibility trees | Roles, labels, states, focus y patterns de la plataforma. | **ADAPTADOR CONDICIONADO**. Combinar con screenshot, geometría y resultado; el árbol no cubre todo lo que ve el usuario. |
| 26 | Chrome DevTools accessibility tree / CDP | Acceso estructurado a DOM y accesibilidad del navegador. | **ADAPTADOR WEB** junto a Playwright; no es aplicable a todas las ventanas ni garantiza que la acción logró su efecto. |
| 27 | Windows Graphics Capture | Captura de ventana/monitor y composición a nivel sistema. | **ADAPTADOR VIZZ** para geometría/overlay; no aporta semántica ni debe persistir píxeles por defecto. |

### D. Estándares y formatos

| # | Referencia | Utilidad exacta | Decisión |
|---:|---|---|---|
| 28 | [DTCG Design Tokens 2025.10](https://www.designtokens.org/TR/2025.10/) | Intercambio de color, tipografía, dimensiones, alias y temas. | **NÚCLEO DE VOCABULARIO VISUAL**, con la corrección de que no es estándar W3C. No define atención, ritmo ni significado por sí solo. |
| 29 | [RFC 6902 JSON Patch](https://www.rfc-editor.org/rfc/rfc6902) | Operaciones `add/remove/replace/move/copy/test` para cambios explícitos. | **NÚCLEO SIGUIENTE** como formato de revisión, undo, branch y replay. `test` ayuda a precondiciones; no convierte un efecto externo en reversible. |
| 30 | [WAI / accessibility](https://www.w3.org/WAI/standards-guidelines/) | Restricciones de contraste, teclado, movimiento, personalización y alternativas. | **GATE NÚCLEO**. Accesibilidad es una condición de representación, no una teoría de carga cognitiva completa. |
| 31 | [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/) | Vocabulario común para eventos y atributos observables. | **MAPEO FUTURO**. No introducir dependencia hasta congelar el contrato privado y las reglas de minimización. |

### E. Matemática, bases de datos y reversibilidad

| # | Referencia | Aporte | Decisión |
|---:|---|---|---|
| 32 | View determinacy / query preservation | Define igualdad operacional como preservación de consultas, no igualdad visual. | **REFERENCIA CENTRAL**; ya operacionalizada en 063 con `Q` explícita. |
| 33 | [Provenance semirings](https://doi.org/10.1145/1265530.1265535) | Propaga por qué una salida depende de fuentes a través de transformaciones relacionales. | **REFERENCIA CENTRAL** para `source_ref`, derivación y no confundir transformación con evidencia nueva. |
| 34 | [Provenance for database transformations](https://doi.org/10.1145/1739041.1739043) | Trata queries, views y mappings con anotaciones y transformaciones. | **REFERENCIA** para diseñar el historial de representación; no implementar una base de datos de provenance completa ahora. |
| 35 | [ProvSQL](https://github.com/PierreSenellart/provsql) / [paper](https://arxiv.org/abs/2504.12058) | Extensión PostgreSQL que materializa circuitos de provenance y análisis de probabilidad/Shapley. | **RESEARCH-ONLY**. Es una implementación real para aprender, pero pesada frente al fixture y al modelo local actuales. |
| 36 | [Bidirectional transformations / contract lenses](https://doi.org/10.1017/S0956796823000059) | Leyes `GetPut`/`PutGet` y contratos para vistas parciales. | **REFERENCIA CENTRAL** para distinguir un render editable de una proyección sólo lectura. |
| 37 | [Effectful lenses](https://doi.org/10.1145/3747523) | Extiende lenses a efectos distintos y no cancelables. | **REFERENCIA FUTURA**. Sirve para pensar ejecución externa, pero no promete que una acción de UI tenga undo real. |
| 38 | [Provenance Meets Bidirectional Transformations](https://www.usenix.org/system/files/tapp2019-paper-anjorin.pdf) | Conecta estructuras auxiliares de consistencia con provenance. | **REFERENCIA CENTRAL** para el cruce X-ANA-X/CODE-INE: cada traducción debe conservar origen y límites. |

### F. Selección y ranking

| # | Referencia | Lectura correcta | Decisión |
|---:|---|---|---|
| 39 | Facility location / submodular optimization | Cobertura con rendimientos decrecientes para escoger alternativas representativas. | **YA USADO** en 064 como política sintética auditable. No llamarlo preferencia humana. |
| 40 | [Sequential Facility Location, ICML 2019](https://proceedings.mlr.press/v97/elhamifar19a/elhamifar19a.pdf) | Extiende selección representativa a estructura secuencial. | **REFERENCIA SIGUIENTE** si RepresentationSpace incorpora orden, recorrido o presupuesto temporal. |
| 41 | [MMR, Carbonell & Goldstein](https://www.cs.cmu.edu/afs/cs/Web/People/jgc/publication/MMR_DiversityBased_Reranking_SIGIR_1998.pdf) | Mezcla relevancia de consulta y novedad frente a lo ya elegido; `lambda` es una política configurable. | **CONTROL DIAGNÓSTICO**. No es una teoría de comprensión ni autoridad de orden; 064 lo usa correctamente como diagnóstico. |
| 42 | [Choice overload meta-analysis](https://doi.org/10.1016/j.jcps.2014.08.002) y [meta-análisis contrario](https://doi.org/10.1086/651235) | El efecto depende de complejidad, tarea, incertidumbre y preferencias; el promedio no es universal. | **CRITERIO DE DISEÑO**, no fórmula. La UI debe permitir explorar y cerrar, no reducir opciones por reflejo. |
| 43 | [Unbiased LTR](https://www.cs.cornell.edu/~tj/publications/joachims_etal_17a.pdf) | Clicks y dwell están contaminados por posición/exposición. | **FUTURO**, sólo con logs de exposición y propensities. Nunca entrenar desde primera elección sin control. |
| 44 | [Off-policy evaluation for slate recommendation](https://arxiv.org/abs/1605.04812) | Estima una política nueva desde slates registrados bajo supuestos de logging. | **FUTURO**. No aplicable al fixture sin exposición aleatorizada ni política de logging documentada. |
| 45 | [Doubly robust OPE/LTR](https://proceedings.mlr.press/v119/su20a/su20a.pdf) | Combina modelo de recompensa y corrección por propensities para reducir sesgo/varianza bajo supuestos. | **FUTURO / MÉTODO DE ANÁLISIS**, nunca garantía automática de utilidad. |
| 46 | [Disentangling Relevance and Bias](https://research.google/pubs/towards-disentangling-relevance-and-bias-in-unbiased-learning-to-rank/) | La torre de bias puede quedar confundida con relevancia porque la política previa decide la posición. | **ALERTA CENTRAL** para 064: posición, exposición y relevancia deben separarse antes de aprender. |

### G. HCI, aprendizaje y filosofía de producto

| # | Referencia | Aporte verificable | Decisión |
|---:|---|---|---|
| 47 | [Shipman & Marshall, Formality Considered Harmful](https://people.engr.tamu.edu/shipman/viki/papers/tochi/tochi.html) y [incremental formalization](https://doi.org/10.1145/306686.306690) | Permitir expresión informal y formalizar gradualmente mientras evoluciona el espacio de información. | **PRINCIPIO X-ANA-X/CODE-INE**: no exigir una especificación perfecta al inicio; sí debe existir un punto explícito de consolidación. |
| 48 | [Horvitz, Mixed-Initiative Interaction](https://doi.org/10.1145/302979.303030) | Distribuir iniciativa entre humano y sistema según incertidumbre, costo, momento y capacidad. | **PRINCIPIO NÚCLEO**: propuesta, preview, corrección y aceptación proporcional al riesgo. |
| 49 | [Ability-Based Design / SUPPLE](https://www.eecs.harvard.edu/~kgajos/papers/2011/wobbrock11abd.shtml) | Diseñar según capacidades en contexto y minimizar esfuerzo estimado, no clasificar personas por etiqueta. | **PRINCIPIO VIZZ**: observar capacidades disponibles y preferencias declaradas; no diagnosticar. |
| 50 | [Structure-Mapping Theory](https://doi.org/10.1207/s15516709cog0702_3) | Una analogía útil alinea relaciones y roles, no sólo apariencia superficial. | **PRINCIPIO X-ANA-X**: cada analogía necesita mapeo, predicción, diferencia y ruptura explícitos. |
| 51 | [Creativity Support Tools](https://doi.org/10.1145/1323688.1323689) | Explorar, comparar, volver y experimentar con bajo costo. | **PRINCIPIO RepresentationSpace**: preservar alternativas sin convertir la primera en autoridad. |
| 52 | [Low Floor / Wide Walls / High Ceiling](https://plix.mit.edu/facilitator-resources/facilitation-resources/facilitating-creative-learning-course-2021-week-2) | Heurística educativa de entrada accesible, exploración amplia y profundidad. | **HEURÍSTICA**, no ley científica ni métrica de producto. |
| 53 | [Jelly, CHI 2025](https://doi.org/10.1145/3706598.3713285) | Interfaces generativas/maleables cuyo modelo puede evolucionar con la tarea. | **REFERENCIA DE DISEÑO** para RepresentationPlan mutable; no dependencia ni prueba de que la maleabilidad mejore aprendizaje. |
| 54 | [Reflective AI, CHI 2026](https://doi.org/10.1145/3772318.3791691) | Propone frenar la obsesión por velocidad y conservar reflexión/agencia. | **GUARDRAIL NÚCLEO**: optimizar comprensión y control, no permanencia ni velocidad a cualquier costo. |
| 55 | [Desirable Difficulties review](https://pubmed.ncbi.nlm.nih.gov/41508718/) | Algunas dificultades favorecen transferencia; la fricción sola puede aumentar carga y no siempre enseña. | **MODO DE APRENDIZAJE CONDICIONADO**: usar predicción/recuperación sólo con evaluación de transferencia y salida fácil. |

### H. Evaluación humana y estadística

| # | Referencia | Uso correcto | Decisión |
|---:|---|---|---|
| 56 | GLMMs in HCI | Separar representación, participante, tarea y dificultad con efectos aleatorios. | **PLAN DE EVALUACIÓN**, no runtime. |
| 57 | Survival analysis | Modelar tiempo a acción, abandono y censura sin borrar casos difíciles. | **PLAN DE EVALUACIÓN** para VIZZ/X-ANA-X. |
| 58 | Latin / balanced Latin squares | Controlar efectos de orden en medidas repetidas. | **PLAN DE DISEÑO** cuando comiencen sesiones humanas. |
| 59 | Pairs of Latin squares | Contrabalancear simultáneamente representación y tarea/estímulo. | **PLAN DE DISEÑO** si se prueban familias de representaciones. |
| 60 | Crossover designs | Modelar periodo, secuencia y carryover. | **PLAN DE DISEÑO**; especialmente importante para VIZZ y ritmos adaptativos. |
| 61 | Equivalence testing / SESOI | Distinguir ausencia de evidencia de equivalencia práctica. | **GATE DE ACEPTACIÓN**: fijar SESOI antes de mirar el test. |
| 62 | [`lme4`](https://cran.r-project.org/package=lme4) | Mixed models en R. | **ANÁLISIS OFFLINE**, no dependencia de producto. |
| 63 | [`glmmTMB`](https://cran.r-project.org/package=glmmTMB) | GLMMs con sobredispersión y zero-inflation. | **ANÁLISIS OFFLINE** cuando los datos lo justifiquen. |
| 64 | [`survival`](https://cran.r-project.org/package=survival) | Modelos de supervivencia y tiempo a evento. | **ANÁLISIS OFFLINE**. |
| 65 | [`emmeans`](https://cran.r-project.org/package=emmeans) | Contrastes y medias marginales estimadas. | **ANÁLISIS OFFLINE**. |
| 66 | [`simr`](https://cran.r-project.org/package=simr) | Potencia por simulación para modelos mixtos. | **ANÁLISIS OFFLINE** antes de prometer tamaño muestral. |

### I. Organizaciones a seguir

Microsoft Research, xLang/OSWorld, OpenAdaptAI, Google, W3C/DTCG, Deque,
CNCF/OpenTelemetry, el ecosistema de provenance de Tannen/Senellart y las
comunidades CHI/UIST/TOCHI se mantienen como **fuentes de vigilancia**. Seguir
una organización no implica adoptar sus repositorios, pesos, benchmarks o
claims.

## Lo que realmente entra en FARMAKSIA

La lista no se debe convertir en una suma de herramientas. Se destila en cinco
interfaces de evidencia:

```text
EvidenceEvent
  qué ocurrió, dónde, cuándo, con qué capacidad y con qué privacidad

RepresentationPlan
  qué relación se quiere hacer visible, con qué tokens, ritmo y controles

SemanticPatch
  qué cambio declarativo se propone, contra qué versión y con qué precondición

InteractionTrace
  qué se expuso, qué se abrió/cerró, qué input explícito ocurrió y qué no se sabe

OutcomeVerifier
  qué resultado independiente confirma, refuta o deja UNKNOWN
```

La cadena de adopción queda así:

| Horizonte | Entrada | No se permite |
|---|---|---|
| Ahora | JSON Patch como semántica de cambio, WAI como gate, DTCG como vocabulario, Pydantic/Hypothesis como candidatos de contrato/pruebas | Instalar un agente general, capturar pantalla por defecto o usar clicks como reward |
| Siguiente | Tree-sitter para CODE-INE, adapters UIA/CDP/Playwright/pywinauto, eventos locales mapeables a OTel | Conectar un adaptador sin identidad de superficie, procedencia, apagado y verificador |
| Condicionado a escala | NetworkX, Submodlib, OR-Tools, Style Dictionary, OpenTelemetry completo | Introducir complejidad antes de superar el fixture local o perder auditabilidad |
| Research | OpenAdapt Evals/ML/Retrieval, OSWorld, WAA, OpenCUA, Computer Agent Arena, OmniParser, UFO | Descargar HF, incorporar corpus arbitrario o llamar “aprendizaje” a un benchmark sin protocolo |
| Evaluación humana | GLMM, survival, contrabalanceo, equivalencia, potencia simulada | Inferir comprensión, ansiedad, preferencia o discapacidad desde telemetría pasiva |

## Consecuencia para cada compuesto

### CODE-INE

La referencia más fértil no es un generador de código aislado. Es la combinación
de Tree-sitter, JSON Patch, provenance/BX, oracle independiente y el patrón
record→compile→verify de OpenAdapt Flow. El producto conceptual es un compilador
de intención a transformación inspeccionable:

```text
intención informal → estructura provisional → patch → preview → ejecución
                    → verificador → consolidación o rollback
```

### X-ANA-X

La referencia científica dominante es Structure-Mapping, no el chatbot ni una
galería de componentes. Una analogía debe preservar fuente, roles, relaciones,
predicción, diferencia y punto de ruptura. La formalización incremental permite
comenzar con lenguaje humano, pero el resultado debe volverse explícito antes
de actuar.

### VIZZ

VIZZ se beneficia de Ability-Based Design, mixed-initiative, WAI, UIA/CDP y
captura de geometría. El eye tracking queda como capacidad opcional; la capa
base debe funcionar con foco, teclado, mouse, layout y señales declaradas.
OpenAdapt Grounding aporta una idea importante para cualquier grounding futuro:
usar una escalera de evidencia barata y estable antes de invocar un modelo
costoso, y detenerse si la identidad no se puede resolver.

### RepresentationSpace

064 tiene una base correcta y limitada: facility location selecciona cobertura
semántica bajo costo, MMR audita redundancia y las ramas permanecen recuperables.
El siguiente paso no es reemplazarlo por Submodlib; es registrar exposición,
orden, tiempo disponible y resultado verificable. Sólo después podría estudiarse
si una política de selección ayuda a la persona.

## Siguiente experimento propuesto

### 065 — contrato de evidencia de representación

**Pregunta:** ¿podemos registrar lo que una representación hizo sin afirmar que
la persona la entendió?

**Fixture:** la misma fuente semántica de 063, tres subsets seleccionados por
064 y una secuencia de patches RFC 6902.

**Cada evento debe conservar:**

- `source_ref` y versión de la fuente;
- `representation_id`, subset y orden de exposición;
- `query_set_version` y consultas cubiertas;
- timestamp monotónico, duración y motivo del cambio;
- input explícito: teclado, mouse, confirmación, undo, solicitud de ayuda;
- capacidades habilitadas y estado de privacidad;
- `outcome`: `verified`, `refuted` o `unknown`;
- `provenance_complete` y `reversible`.

**Kill tests:**

1. reordenar la lista no puede cambiar la fuente ni ocultar una rama sin dejar
   registro;
2. un patch sin `test` de versión o identidad se rechaza;
3. un click en una rama no se convierte en `preference=true`;
4. una representación que pierde una consulta crítica queda `invalid` aunque
   sea visualmente atractiva;
5. un outcome no verificable no puede finalizar `success`;
6. una sesión sin cámara debe producir exactamente el mismo contrato esencial
   de representación;
7. ningún evento persiste píxeles, audio, texto sensible o trayectoria ocular
   si la capacidad no fue autorizada explícitamente.

**Criterio de éxito:** el sistema puede explicar qué se mostró, por qué se
mostró, qué fuente lo respalda, qué input ocurrió y qué resultado fue
verificado, sin inventar comprensión humana.

## Conclusión

La investigación no recomienda perseguir al proyecto con más modelos. Recomienda
hacer más difícil que FARMAKSIA se equivoque silenciosamente:

```text
menos dependencias prematuras
+ contratos tipados
+ representación reversible
+ provenance
+ evidencia de exposición
+ verificación independiente
= una capa generativa defendible
```

La lista sí sirve, pero como mapa de patrones. El núcleo propio de FARMAKSIA
debe seguir siendo pequeño, local, auditable y capaz de sobrevivir aunque todos
los adaptadores externos sean reemplazados.

## Fuentes primarias complementarias

- [RFC 6902 — JSON Patch](https://www.rfc-editor.org/rfc/rfc6902)
- [WAI standards and guidelines](https://www.w3.org/WAI/standards-guidelines/)
- [Provenance semirings](https://doi.org/10.1145/1265530.1265535)
- [MMR original, CMU](https://www.cs.cmu.edu/afs/cs/Web/People/jgc/publication/MMR_DiversityBased_Reranking_SIGIR_1998.pdf)
- [Sequential Facility Location](https://proceedings.mlr.press/v97/elhamifar19a/elhamifar19a.pdf)
- [Unbiased Learning to Rank](https://www.cs.cornell.edu/~tj/publications/joachims_etal_17a.pdf)
- [Google: disentangling relevance and bias](https://research.google/pubs/towards-disentangling-relevance-and-bias-in-unbiased-learning-to-rank/)
- [Horvitz: Mixed-Initiative Interaction](https://www.microsoft.com/en-us/research/publication/mixed-initiative-interaction/)
- [Ability-Based Design](https://www.eecs.harvard.edu/~kgajos/papers/2011/wobbrock11abd.shtml)
- [Structure-Mapping Theory](https://doi.org/10.1207/s15516709cog0702_3)
- [OpenAdapt Grounding](https://github.com/OpenAdaptAI/openadapt-grounding)
- [OpenAdapt ML status](https://github.com/OpenAdaptAI/openadapt-ml)
- [OpenAdapt Retrieval status](https://github.com/OpenAdaptAI/openadapt-retrieval)
