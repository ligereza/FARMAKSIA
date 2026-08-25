# Research 022 — lógica de diseño para una interfaz generativa sensorial

Fecha: 2026-08-25

## Pregunta

¿Qué principios científicos, patrones de interacción y proyectos abiertos
pueden convertir FARMAKSIA en una capa generativa que decida cómo se muestra
la información, en vez de limitarse a generar componentes de una UI?

## Tesis

La unidad de FARMAKSIA no debe ser el botón, la tarjeta ni el dashboard. Debe
ser el **plan de representación**: una decisión explícita sobre qué relación
semántica debe percibirse, qué atención merece, con qué ritmo debe aparecer y
qué transformación visual o interactiva la vuelve comprensible.

```text
fuente de información
        ↓
estructura semántica
        ↓
objetivo, tarea y contexto
        ↓
compuesto FARMAKSIA
        ↓
plan de representación
        ↓
render visual, temporal, espacial o multimodal
```

FARMAKSIA investiga el diseño de **drogas computacionales** como una metáfora
de diseño de experiencias: intensidad, ritmo, foco, claridad, continuidad y
transformación. No son afirmaciones farmacológicas ni intentos de inferir la
química cerebral de una persona.

## Hallazgo principal: Generative UI todavía es insuficiente

Los proyectos recientes de Generative UI resuelven una parte real del
problema: permiten que un agente describa una interfaz y que un cliente la
renderice con componentes confiables.

| Proyecto o estándar | Aporte confirmado | Límite para FARMAKSIA |
|---|---|---|
| [Google A2UI](https://github.com/a2ui-project/a2ui) | Formato declarativo para que un agente describa interfaces actualizables; el cliente renderiza un catálogo de componentes propios y evita ejecutar código arbitrario | Describe componentes y datos, pero no define una teoría de ritmo, atención, color, intensidad o aprendizaje |
| [MCP Apps](https://github.com/modelcontextprotocol/ext-apps) | Permite que una herramienta declare una vista `ui://`, que el host la renderice en un entorno aislado y que exista comunicación bidireccional | Lleva la interfaz al contexto del agente, pero no decide cómo debe sentirse o dosificarse la información |
| [OpenUI](https://github.com/thesysdev/openui) | Lenguaje compacto y orientado a streaming para generar UI estructurada desde una biblioteca de componentes | Su unidad principal sigue siendo el componente; sus cifras de tokens/latencia son afirmaciones del proyecto, no evidencia FARMAKSIA |
| [W3C Personalization Semantics](https://www.w3.org/TR/2020/WD-personalization-semantics-1.0-20200127/) | Permite asociar significado a controles y contenido para que la presentación pueda adaptarse a preferencias y necesidades | Aporta semántica de contenido, no una política sensorial completa |
| [Design Tokens 2025.10](https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/) | Vocabulario interoperable para expresar decisiones de color, tipografía, espaciado, referencias y temas | Estandariza valores y relaciones de diseño, pero no decide cuándo, por qué o a qué velocidad cambiar la representación |

La oportunidad de FARMAKSIA está entre el modelo semántico y el renderer:

```text
A2UI / OpenUI / MCP Apps:       qué componentes puede dibujar el cliente
FARMAKSIA:                      por qué, cuándo y cómo debe cambiar la forma
```

La adopción recomendada es conceptual y gradual: tomar el principio
declarativo, el catálogo confiable, el streaming y los tokens semánticos, pero
no convertir ninguna de esas herramientas en la teoría de FARMAKSIA.

## Evidencia de diseño e interacción

### 1. La atención tiene centro y periferia

La propuesta de *Calm Technology* de Weiser y Brown no es eliminar
información, sino diseñar para que una señal pueda vivir en la periferia y
entrar al centro cuando importe. La tecnología debe informar sin exigir que
todo compita por el foco al mismo tiempo
([Designing Calm Technology](https://calmtech.com/papers/designing-calm-technology)).

Esto se conecta directamente con VIZZ:

- centro: acción o relación que requiere comprensión inmediata;
- parafóvea: contexto que ayuda a anticipar la siguiente acción;
- periferia: estado, orientación y cambios que no deben desaparecer;
- transición: el momento en que una señal gana suficiente importancia para
  ocupar el centro.

VIZZ no debe convertir la periferia en un basurero visual ni borrar contexto.
Debe administrar el tránsito entre centro y periferia.

### 2. La simplificación debe ser reversible y controlable

La guía de accesibilidad cognitiva de W3C recomienda soportar personalización,
simplificación y alternativas familiares, junto con control del usuario sobre
cuándo el contenido se mueve o cambia
([adaptación y personalización](https://www.w3.org/WAI/WCAG2/supplemental/objectives/o8-personalization/),
[simplificación](https://www.w3.org/WAI/WCAG2/supplemental/patterns/o8p03-complexity/)).

La implicación no es diseñar una versión “infantil”. Es permitir que la misma
información adopte distintas formas:

```text
completa ↔ resumida ↔ guiada ↔ visual ↔ técnica
```

La persona debe poder regresar a la representación completa. Toda adaptación
debe tener explicación, control y reversión.

### 3. El aprendizaje mejora cuando se guía la atención

La literatura de aprendizaje multimedia estudia señales, segmentación,
señalización y codificación de relaciones. Un metaanálisis encontró que las
señales visuales pueden reducir búsquedas innecesarias y carga cognitiva, y
favorecer retención y transferencia
([meta-análisis de señales y carga cognitiva](https://pmc.ncbi.nlm.nih.gov/articles/PMC5576760/)).

El color también guía atención de forma dependiente de la complejidad y del
color concreto; no existe una regla universal del tipo “azul calma” o “rojo
alerta” que pueda aplicarse sin contexto
([color y atención en displays complejos](https://pubmed.ncbi.nlm.nih.gov/31422277/)).

Por tanto, la lógica didáctica de X-ANA-X debe hacer visible la relación que
quiere enseñar:

```text
fuente → relación → transformación → predicción → verificación
```

Un elemento visual es didáctico cuando reduce la distancia entre dos
conceptos, no simplemente cuando hace la pantalla más atractiva.

### 4. La revelación progresiva es una forma de aprendizaje

Un estudio reciente sobre interfaces por capas examinó la revelación
progresiva para aprender una interfaz compleja. Su hipótesis práctica es
mostrar primero las funciones que sirven para la tarea actual y liberar
gradualmente las demás, manteniendo una tensión entre descubribilidad local y
conciencia del sistema completo
([Designing for Learnability](https://doi.org/10.1177/10648046241273291)).

Esto ofrece a VIZZ una lógica para operadores nuevos:

```text
ver lo esencial → ejecutar → comprender la consecuencia → ampliar el mapa
```

La interfaz no debe esconder capacidades de manera irreversible. Debe
construir un camino de aprendizaje.

### 5. El tiempo es un parámetro visual

Las interrupciones no son sólo un problema de cantidad de información. Son
un cambio forzado de tarea. Un metaanálisis de 68 estudios encontró que los
efectos dependen de urgencia, complejidad, modalidad y carga de trabajo
([interruption management](https://doi.org/10.1177/0018720813476298)).

FARMAKSIA debe poder cambiar:

- velocidad de aparición;
- duración de una señal;
- agrupación de notificaciones;
- anticipación antes de interrumpir;
- permanencia de un contexto;
- tiempo disponible para confirmar;
- velocidad de scroll o reproducción.

La pauta de W3C de pausar, detener u ocultar contenido móvil establece una
base técnica para que la animación no sea una imposición irreversible
([Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html)).

### 6. La adaptación necesita iniciativa compartida

La personalización automática puede ser útil, pero si cambia la interfaz sin
explicación se vuelve impredecible. Las guías de Microsoft para interacción
humano-IA recomiendan que el sistema explique sus capacidades, actúe según el
contexto, permita descartar y corregir, actualice con cautela y ofrezca
controles globales
([HAX Toolkit](https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/)).

La personalización de FARMAKSIA debe ser de **iniciativa mixta**:

```text
el sistema propone → la persona previsualiza → acepta, modifica o revierte
```

La persona puede decir “más simple”, “más técnico”, “muéstrame todo” o
“enséñamelo con una analogía”. No se debe construir un adaptador invisible que
aprenda preferencias sin hacerlas comprensibles.

## Gramática visual propuesta

La lógica de diseño debe operar sobre parámetros semánticos, no sobre colores
decorativos elegidos al azar.

| Dimensión | Pregunta de diseño | Operadores FARMAKSIA |
|---|---|---|
| Jerarquía | ¿Qué debe entenderse primero? | escala, posición, contraste, aislamiento |
| Relación | ¿Qué elementos deben entenderse juntos? | proximidad, líneas, agrupación, color compartido |
| Ritmo | ¿Cuándo debe aparecer cada parte? | revelación, segmentación, pausa, agrupación |
| Intensidad | ¿Cuánta energía visual requiere? | luminancia, cromaticidad, movimiento, densidad |
| Contexto | ¿Qué no debe perderse aunque no esté en foco? | periferia, estado persistente, mini-mapa, ancla |
| Aprendizaje | ¿Qué relación debe poder transferirse? | analogía, comparación, transformación, predicción |
| Construcción | ¿Cómo se conecta la intención con el resultado? | intención, estructura, código, preview, oracle |
| Control | ¿Quién decide el cambio? | propuesta, previsualización, aceptación, undo, perfil |

### Color

El color debe tener un contrato semántico: acción, estado, relación,
advertencia, selección, incertidumbre o procedencia. La saturación puede
regular atención, pero el significado no debe depender exclusivamente del
color. Cada token debe tener contraste, texto o forma complementaria.

### Forma y espacio

La posición puede expresar una relación: causa antes que consecuencia, fuente
al lado del objetivo, dependencia detrás del componente que la consume,
historia arriba y estado actual abajo. Esto es más potente que decorar tarjetas
con colores distintos.

### Movimiento

El movimiento debe explicar una transformación: de dónde salió un dato, qué
relación se activó o qué cambió. El movimiento ornamental compite con la
comprensión. Toda animación debe poder detenerse, reducirse o sustituirse por
un estado estático.

### Densidad

La densidad no es simplemente ocultar cosas. Es decidir qué nivel de detalle
se necesita ahora y qué nivel puede aparecer cuando se solicite:

```text
señal → resumen → estructura → detalle → fuente/origen
```

### Ritmo

La interfaz debe tener acelerador y freno. Un usuario puede querer una lectura
rápida, una guía pausada, una exploración abierta o una construcción intensa.
La velocidad de presentación es parte del diseño, no una propiedad fija del
contenido.

## Los tres compuestos como políticas de representación

### VIZZ — política de orientación

**Objetivo:** que una persona nueva sepa dónde mirar, qué hacer y qué cambió.

Operadores:

- foco progresivo;
- anclas espaciales persistentes;
- reducción reversible de ruido;
- recorrido de atención sin cámara;
- confirmación mediante mouse, teclado o foco;
- geometría de múltiples pantallas cuando esté disponible.

VIZZ es la capa sensorial. Puede usar cámara, IMU, mouse, teclado, geometría
de monitores o ninguna de esas fuentes según la capacidad autorizada.

### X-ANA-X — política de traducción

**Objetivo:** que una persona pueda pasar de no entender a manipular una
estructura nueva.

Operadores:

- selección de un dominio fuente;
- alineamiento de entidades y relaciones;
- vista fuente/objetivo;
- animación de correspondencias;
- predicción explícita;
- verificación y declaración de ruptura.

Un agente X-ANA-X no debe generar una interfaz sólo porque sea visualmente
atractiva. Debe escoger una representación porque hace visible una relación.

### CODE-INE — política de construcción

**Objetivo:** que una persona pueda convertir intención en una interfaz
funcional sin perder el vínculo con el código y el resultado.

Operadores:

- intención declarada;
- esquema semántico;
- composición de componentes;
- preview interactivo;
- código inspeccionable;
- prueba u oracle;
- corrección reversible.

CODE-INE no es sólo generación rápida. Es una política de continuidad entre
idea, representación, implementación y verificación.

## Contrato de representación propuesto

La unidad que un agente debe producir no es directamente HTML o React. Es un
plan declarativo que un renderer seguro puede convertir en una o varias
representaciones.

```text
RepresentationRequest {
  semantic_model,
  task,
  user_role,
  declared_preferences,
  available_capabilities,
  desired_compound,
  constraints
}

RepresentationPlan {
  semantic_priority,
  disclosure_layers,
  spatial_anchors,
  visual_tokens,
  motion_policy,
  tempo_policy,
  peripheral_context,
  explanation,
  confidence,
  provenance,
  user_controls,
  reversible_actions
}
```

El modelo puede proponer `RepresentationPlan`; el cliente debe validar el
esquema, limitar los tokens y renderizar sólo componentes aprobados. Esta
separación combina la intuición de A2UI/OpenUI con la política sensorial
propia de FARMAKSIA.

## Ejemplos de composición

### Operador nuevo

```text
VIZZ: resalta el primer control
X-ANA-X: explica su función con una analogía visible
VIZZ: muestra el siguiente paso y conserva el anterior como ancla
CODE-INE: registra la intención de la acción y la confirma
```

### Persona explorando una explicación de un agente

```text
X-ANA-X: divide la explicación en fuente, mapeo y predicción
VIZZ: muestra las correspondencias con color, espacio y movimiento
el usuario: solicita más detalle o vuelve al resumen
CODE-INE: convierte la comprensión verificada en una modificación ejecutable
```

### Interfaz que compite con el scrolling

FARMAKSIA no necesita ganar con más estímulo. Puede cambiar la lógica de
presentación:

- reemplazar flujo infinito por unidades con principio y cierre;
- mostrar progreso semántico, no sólo una barra de tiempo;
- agrupar contenido por relaciones;
- permitir recapitulación y salida clara;
- reservar movimiento y color para cambios significativos;
- ofrecer una elección explícita entre explorar, resumir y profundizar.

La meta no es maximizar permanencia. Es aumentar comprensión, orientación,
agencia y capacidad de continuar o detenerse.

## Hipótesis de FARMAKSIA

1. Un plan que separa significado, ritmo y estilo puede producir interfaces más
   fáciles de aprender que una lista estática de componentes.
2. La revelación progresiva con contexto periférico puede reducir sobrecarga
   sin volver invisible la capacidad del sistema.
3. Las analogías visuales verificables pueden enseñar mejor que una explicación
   textual equivalente cuando la dificultad principal es relacional.
4. Una interfaz que permite cambiar intensidad, densidad y ritmo puede servir a
   más estados de interacción sin diagnosticar al usuario.
5. La generación declarativa de un plan de representación puede ser más
   auditable y portable que la generación directa de código de interfaz.

## Experimentos siguientes

### 022-A — misma información, cinco representaciones

El renderer ejecutable está en
`experiments/056-farmaxia-representation-renderer/`. Usa un fixture local y
renderiza la misma escena como panel plano, vista guiada, mapa de relaciones,
explicación por analogía y flujo de construcción. El contrato mide cobertura
semántica, invariancia de entidades/relaciones, reversibilidad declarada y
privacidad. No usa cámara ni datos humanos. La comprensión humana sigue siendo
`UNKNOWN` hasta una evaluación posterior.

### 022-B — contrato `RepresentationPlan`

Implementar un esquema pequeño y un renderer local. El agente sólo puede
escoger tokens, capas, relaciones y componentes de un catálogo. El kill test
rechaza código ejecutable o propiedades visuales no declaradas.

### 022-C — operador nuevo sin cámara

Comparar interfaz completa, interfaz simplificada y guía progresiva. La
respuesta se registra con acciones explícitas, no con una inferencia de mirada.

### 022-D — analogía verificable

Comparar explicación directa frente a explicación X-ANA-X. Aceptar una mejora
solamente si aumenta transferencia o detección de errores, no sólo sensación de
claridad.

### 022-E — ritmo y periferia

Comparar notificación inmediata, agrupada y periférica. Medir interrupciones,
recuperación de contexto y acciones omitidas en un fixture reproducible.

## Kill tests

- Si una adaptación cambia sin que el usuario pueda entender por qué, se
  bloquea.
- Si simplificar elimina contexto necesario, se rechaza la simplificación.
- Si el color mejora estética pero no facilita una decisión o relación, no se
  considera evidencia de avance.
- Si X-ANA-X produce una analogía sin predicción verificable, devuelve
  `unavailable`.
- Si CODE-INE genera código cuyo comportamiento no puede inspeccionarse o
  probarse, no se acepta como construcción asistida.
- Si VIZZ sólo funciona con cámara, la arquitectura no cumple el contrato
  `NO_CAMERA`.
- Si una política generativa borra el input, mueve el foco inesperadamente o
  pierde el estado local, se revierte al plan anterior.
- Si una interfaz adaptativa mejora permanencia pero reduce comprensión,
  agencia o capacidad de salida, se considera fallo de diseño.

## Límites

La capa puede reducir complejidad visual, ordenar estímulos y adaptar una
representación. No debe presentarse como tratamiento para ansiedad, déficit de
atención, intoxicación, fatiga, miopía, astigmatismo o presbicia. Tampoco debe
usar cámara, pupila o logs para diagnosticar estados humanos. Es posible
estudiar perfiles declarados y señales de interacción sin convertirlos en
explicaciones neuroquímicas.

## Decisión de adopción

FARMAKSIA adoptará como referencias:

1. semántica declarativa y catálogo confiable de A2UI;
2. composición incremental y streaming de OpenUI;
3. vistas en contexto y sandbox de MCP Apps;
4. tokens interoperables como vocabulario de estilo;
5. personalización, simplificación, control y reversibilidad de W3C;
6. centro/periferia de Calm Technology;
7. revelación progresiva, señalización y gestión de interrupciones de la
   literatura de HCI.

No se adopta todavía ninguna de esas dependencias como runtime principal. El
primer prototipo será local, pequeño y declarativo, para probar la lógica de
representación antes de incorporar una plataforma generativa externa.

## Fuentes principales

- [Designing Calm Technology — Weiser y Brown](https://calmtech.com/papers/designing-calm-technology)
- [W3C: Support Adaptation and Personalization](https://www.w3.org/WAI/WCAG2/supplemental/objectives/o8-personalization/)
- [W3C: Support Simplification](https://www.w3.org/WAI/WCAG2/supplemental/patterns/o8p03-complexity/)
- [W3C: Personalization Semantics](https://www.w3.org/TR/2020/WD-personalization-semantics-1.0-20200127/)
- [W3C Design Tokens Format 2025.10](https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/)
- [Designing for Learnability: Layered Interfaces](https://doi.org/10.1177/10648046241273291)
- [The role of cues in multimedia learning](https://pmc.ncbi.nlm.nih.gov/articles/PMC5576760/)
- [The attentional guidance of individual colours](https://pubmed.ncbi.nlm.nih.gov/31422277/)
- [Supporting Interruption Management](https://doi.org/10.1177/0018720813476298)
- [W3C: Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html)
- [Microsoft HAX Toolkit](https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/)
- [Google People + AI Guidebook](https://pair.withgoogle.com/guidebook-v2/chapters)
- [Google A2UI](https://github.com/a2ui-project/a2ui)
- [MCP Apps](https://github.com/modelcontextprotocol/ext-apps)
- [OpenUI](https://github.com/thesysdev/openui)
