# FARMAKSIA

Laboratorio independiente de investigación computacional, matemática y
artística. El repositorio conserva hipótesis, antecedentes, fixtures,
experimentos, kill tests, procedencia y decisiones de adopción.

Los nombres CODE-INE, X-ANA-X, KETAMINE y VIZZ son hipótesis de trabajo, no
compromisos de producto. Pueden fusionarse, redefinirse o eliminarse.

## Marco conceptual: una capa generativa de representación

FARMAXIA no está construyendo solamente una UI, un hub ni un mouse ocular.
La hipótesis central es una **capa generativa de representación sensorial**:
un sistema que decide no sólo qué información mostrar, sino con qué ritmo,
intensidad, estructura, color, movimiento, escala y relación espacial debe
aparecer para que pueda percibirse, comprenderse y utilizarse.

La dirección de crecimiento es agnóstica a dominios: el núcleo no intentará
convertirse en una aplicación universal, sino en una capa que conecta dos o
más superficies mediante un estado semántico, una representación reversible y
un verificador independiente. El primer producto puede adaptarse a una
institución con aplicaciones distintas sin reemplazarlas: observa una fuente,
conserva su procedencia, propone cómo recorrerla en otra superficie y sólo
declara éxito cuando el resultado real puede comprobarse.

En este sentido, FARMAXIA investiga el diseño de **drogas computacionales**:
composiciones de interfaz capaces de cambiar una experiencia de interacción
sin afirmar que reproduzcan sensaciones farmacológicas ni diagnosticar el
estado neuroquímico de una persona. La reducción de daño es un criterio de
diseño: la capa puede informar, desacelerar, ordenar o reducir estímulos
cuando eso mejora la experiencia del usuario y del entorno, sin convertir la
interfaz en una autorización para realizar actividades peligrosas bajo
intoxicación.

Las tres hipótesis forman una gramática funcional, no tres productos aislados:

```text
VIZZ     → orientar la percepción y el recorrido visual
X-ANA-X  → enseñar mediante analogías, relaciones y transformaciones semánticas
CODE-INE → construir, modificar y verificar interfaces mediante código
```

### VIZZ: orientación sensorial

VIZZ puede guiar a un operador nuevo sin exigir que la cámara esté encendida.
La interfaz puede atraer la atención, reducir ruido, conservar anclas,
mostrar una secuencia y confirmar cada paso mediante mouse, teclado o foco de
ventana. La cámara, cuando exista, es una capacidad opcional para estudiar la
respuesta visual; no es requisito para que la representación sea inteligente.

### X-ANA-X: comprensión y enseñanza

X-ANA-X transforma lo desconocido en una estructura recorrible: código en
diagrama, error en causalidad, sistema en mapa o concepto en una analogía
manipulable. Un agente puede enseñar así, pero debe conservar la relación entre
fuente y objetivo, producir una predicción y señalar dónde se rompe la
analogía. No basta con que una explicación resulte tranquilizadora.

### CODE-INE: construcción

CODE-INE corresponde al usuario que no sólo opera interfaces, sino que también
necesita construirlas. Su cadena es:

```text
intención → estructura → representación → código → ejecución → prueba → corrección
```

El objetivo es que la persona conserve visible la relación entre lo que quiso
crear, el código generado y el comportamiento observado, evitando que la
velocidad de generación sustituya la comprensión.

### Composición generativa

Las capas pueden encadenarse:

```text
VIZZ orienta al operador
        ↓
X-ANA-X explica lo que no comprende
        ↓
CODE-INE permite construir o modificar
        ↓
VIZZ presenta el resultado de forma comprensible
```

El modelo generativo se investigará como una función de objetivo, tarea,
fricción, incertidumbre, contexto sensorial, geometría de pantalla y
compuesto activo. La intensidad visual, la velocidad de transición, la
densidad informativa, el contraste, la saturación y el movimiento son
parámetros de representación; no son afirmaciones sobre neurotransmisores.

## Estado actual

| Hipótesis | Estado |
|---|---|
| CODE-INE | descriptor provisional con oracle ejecutable 029, compilador de experiencia 060, compromiso progresivo 061 y espacio de representaciones 062/063/064; interoperable con VIZZ; operador independiente eliminado |
| X-ANA-X | archivado como hipótesis independiente; protocolo de analogía conservado |
| KETAMINE | en cuarentena; sin prototipo activo ni teoría forzada |
| VIZZ | flujo 032/033 y geometría 052/053: runtime CUDA experimental con compuerta privacy-first; no toda función requiere cámara; precisión y eficacia desconocidas |

No se implementan operadores como API ni se fija arquitectura mientras sus
kill tests sigan abiertos.

## Ejecutar la suite

Desde la raíz del repositorio:

```text
python research/tools/run_suite.py
```

La suite usa Python estándar, valida la procedencia de todos los experimentos,
regenera y verifica el piloto VIZZ y confirma explícitamente `NO_HUMAN_DATA`
cuando no existe un archivo humano.

El laboratorio opera **sin datos humanos** en esta fase: los fixtures son
sintéticos o declarativos y cualquier captura personal queda fuera del corpus
hasta contar con un protocolo y consentimiento explícitos.

## Leer el laboratorio

- [Protocolo del loop](RESEARCH_LOOP.md)
- [Auditoría consolidada](research/decisions/009-laboratory-audit.md)
- [Kill test amplio de CODE-INE](experiments/007-codeine-general-boundary/results.md)
- [Transición de sesión CODE-INE](experiments/016-codeine-session-state/results.md)
- [Frontera de X-ANA-X](experiments/008-xanax-boundary/results.md)
- [Cadena de analogía X-ANA-X](experiments/017-xanax-analogy-chain/results.md)
- [Control X-ANA-X frente a reformulación](experiments/018-xanax-reformulation-control/results.md)
- [Auditoría final y archivo X-ANA-X](experiments/019-xanax-provenance-archive-audit/results.md)
- [Kill test metodológico de VIZZ](research/decisions/015-vizz-carryover-kill.md)
- [Piloto VIZZ contrabalanceado](experiments/009-vizz-counterbalanced/results.md)
- [Kill test poligonal de KETAMINE](experiments/011-nonrectangular-boundary/results.md)
- [Kill test de curvas y capas](experiments/012-curves-layers-boundary/results.md)
- [Prototipo VIZZ de adaptación perceptual](experiments/013-vizz-perceptual-adaptation/results.md)
- [Consulta VIZZ de entrada en repetición](experiments/014-vizz-decision-query/results.md)
- [Contrato VIZZ de sesión](experiments/015-vizz-session-contract/results.md)
- [Puente VIZZ → CODE-INE](experiments/020-vizz-codeine-event-bridge/results.md)
- [Compuerta del adaptador manual VIZZ](experiments/021-manual-adapter-gate/results.md)
- [Puente largo VIZZ → CODE-INE](experiments/022-vizz-codeine-long-bridge/results.md)
- [Frontera de observabilidad VIZZ → CODE-INE](experiments/023-vizz-codeine-observability-boundary/results.md)
- [Frontera de latencia y cobertura VIZZ](experiments/024-vizz-latency-coverage-boundary/results.md)
- [Invariancia de condición de display VIZZ](experiments/025-vizz-display-condition-invariance/results.md)
- [Señal de objetivo CODE-INE](experiments/026-codeine-objective-signal/results.md)
- [Oráculo de objetivo CODE-INE](experiments/027-codeine-objective-oracle/results.md)
- [Oracle ejecutable y mutación CODE-INE](experiments/029-codeine-executable-oracle/results.md)
- [Compuerta de calidad gaze-contingent VIZZ](experiments/028-vizz-gaze-quality-gate/results.md)
- [Adaptador WebGazer local opt-in VIZZ](experiments/030-vizz-webgazer-opt-in/results.md)
- [Contrato de flujo VIZZ visible/headless](experiments/032-vizz-python-flow-split/README.md)
- [Runtime Python CUDA y modificador de contenido VIZZ](experiments/033-vizz-python-headless-runtime/README.md)
- [Auditor offline de calidad naturalista VIZZ](experiments/054-vizz-naturalistic-quality-audit/README.md)
- [Renderer de representación generativa FARMAKSIA](experiments/056-farmaxia-representation-renderer/README.md)
- [Runtime overlay real sin camara](experiments/057-farmaxia-overlay-runtime/README.md)
- [Runtime GPU de composicion retenida FARMAKSIA](experiments/058-farmaxia-gpu-composition-runtime/README.md)
- [Compuerta de privacidad y capacidades sin cámara VIZZ](research/decisions/060-vizz-privacy-capability-gate.md)
- [Arquetipos open source para la capa adaptativa FARMAKSIA](research/decisions/062-farmaxia-open-source-archetypes.md)
- [Auditoría consolidada de estado](research/decisions/032-laboratory-state-audit.md)
- [Arquitectura X-ANA-X para tutoriales transferibles](research/decisions/065-xanax-tutorial-transfer-architecture.md)
- [Contrato X-ANA-X de tutorial y puente entre aplicaciones](experiments/059-xanax-tutorial-transfer-contract/README.md)
- [Compilador de experiencia CODE-INE](experiments/060-codeine-experience-compiler/README.md)
- [Compromiso progresivo CODE-INE](experiments/061-codeine-progressive-commitment/README.md)
- [Renderer de espacio de representaciones FARMAKSIA](experiments/062-farmaxia-representation-space-renderer/README.md)
- [Contrato de invariantes semánticos FARMAKSIA](experiments/063-farmaxia-semantic-invariant-contract/README.md)
- [Selección de subset de ramas FARMAKSIA](experiments/064-farmaxia-branch-subset-selection/README.md)
- [Evidencia entre aplicaciones GitLab–Mattermost](experiments/065-farmaxia-cross-application-evidence/README.md)
- [Replay temporal de evidencia FARMAKSIA](experiments/066-farmaxia-temporal-evidence-replay/README.md)
- [Watermarks y eventos tardíos FARMAKSIA](experiments/067-farmaxia-watermark-late-event-replay/README.md)
- [Sobre CloudEvents sin infraestructura](experiments/068-farmaxia-cloudevents-envelope/README.md)
- [Decisión de latencia y cobertura VIZZ](research/decisions/034-vizz-latency-coverage-boundary.md)
- [Decisión de condición de display VIZZ](research/decisions/035-vizz-display-condition-invariance.md)
- [Lógica de diseño para interfaz generativa sensorial](research/literature/022-farmaxia-generative-interface-design-logic.md)
- [Decisión CODE-INE como compilador de experiencia](research/decisions/066-codeine-experience-compiler.md)
- [Decisión CODE-INE de compromiso progresivo](research/decisions/067-codeine-progressive-commitment.md)
- [Decisión de renderer RepresentationSpace](research/decisions/068-representation-space-renderer.md)
- [Decisión de preservación semántica relativa a consultas](research/decisions/069-semantic-invariant-contract.md)
- [Decisión de selección marginal de ramas](research/decisions/070-branch-subset-selection.md)
- [Auditoría profunda de referencias open source y científicas](research/literature/023-open-source-reference-audit.md)
- [Compuerta de adopción de referencias externas](research/decisions/071-open-source-reference-gate.md)
- [Decisión de replay temporal de evidencia](research/decisions/072-temporal-evidence-replay.md)
- [Decisión de watermarks y eventos tardíos](research/decisions/073-watermark-late-events.md)
- [Atajo de adopción de infraestructura consolidada](research/decisions/074-consolidated-foundations-shortcut.md)
- [Handoff: crecimiento entre aplicaciones y desafío institucional](research/handoffs/001-adaptive-representation-growth.md)
- [Futuro de FARMAKSIA como compilador de representación](research/decisions/061-farmaxia-generative-interface-roadmap.md)
- [Literatura de observabilidad VIZZ](research/literature/010-vizz-observability-boundary.md)
- [Literatura de condiciones de display VIZZ](research/literature/011-vizz-display-conditions.md)
- [Literatura de señal objetiva CODE-INE](research/literature/012-codeine-objective-signal.md)
- [Literatura de oráculos verificables CODE-INE](research/literature/013-codeine-verifiable-objective.md)
- [Literatura de oracle ejecutable y mutation testing CODE-INE](research/literature/015-codeine-executable-oracle-mutation.md)
- [Decisión de oracle ejecutable CODE-INE](research/decisions/039-codeine-executable-oracle.md)
- [Auditoría de completitud de la fundación](research/decisions/040-laboratory-completion-audit.md)
- [Literatura de calidad de mirada y herramientas VIZZ](research/literature/014-vizz-gaze-quality-tools.md)
- [Decisión de compuerta gaze-contingent VIZZ](research/decisions/038-vizz-gaze-quality-gate.md)
- [Literatura del runtime WebGazer VIZZ](research/literature/016-vizz-webgazer-runtime.md)
- [Decisión de adopción experimental WebGazer VIZZ](research/decisions/041-vizz-webgazer-opt-in.md)
- [Modelo óptico reducido VIZZ: pantalla, luz, foco y retina](experiments/044-vizz-reduced-eye-camera/README.md)
- [Cámara óptica VIZZ 045: objeto, foco y sensor](experiments/045-vizz-single-eye-camera/README.md)
- [Investigación de calibración y herramientas open source VIZZ](research/literature/017-vizz-calibration-open-source.md)
- [Investigación de runtime Python GPU VIZZ](research/literature/018-vizz-python-gpu-runtime.md)
- [Decisión de flujo VIZZ calibración/runtime](research/decisions/045-vizz-flow-split.md)
- [Contrato de ingreso de corpus](research/corpus-intake.md)
- [Piloto humano VIZZ](experiments/003-vizz-decision/pilot_protocol.md)
- [Compuerta de adopción de herramientas](research/decisions/011-tool-adoption-gate.md)

## Regla de honestidad

La automatización puede demostrar estructura, costo, preservación,
procedencia y falsación lógica. No puede demostrar percepción humana, valor
artístico ni autoridad de decisión.
