# Decisión 062 — Arquetipos open source para la capa adaptativa FARMAXIA

**Fecha:** 2026-08-25  
**Estado:** propuesta de arquitectura, sin dependencias descargadas  
**Alcance:** VIZZ, X-ANA-X y CODE-INE

## Decisión

FARMAXIA no se desarrollará como una aplicación delimitada ni como un hub con
componentes propios. Se desarrollará como un runtime local de representación
que observa el contexto permitido de otras aplicaciones y dibuja una capa
adaptativa sobre ellas.

La unidad de diseño no será un botón, tarjeta o panel. Será un evento semántico
convertido en un `RepresentationPlan` y luego en primitivas visuales seguras:

```text
aplicación existente
        ↓
adaptador de contexto
        ↓
evento semántico
        ↓
VIZZ / X-ANA-X / CODE-INE
        ↓
RepresentationPlan
        ↓
overlay GPU transparente
```

La superposición no debe sustituir el contenido original, interceptar entradas
por defecto ni ejecutar código recibido desde un agente. La ausencia de una
intervención también es un resultado válido.

## Tres referencias directas

### 1. ShaderGlass y procmod/overlay: el cuerpo del overlay

[ShaderGlass](https://github.com/mausimus/ShaderGlass) demuestra la idea de
aplicar una transformación gráfica sobre el escritorio o una ventana capturada,
con modos de transparencia, clonación, escalado y passthrough. No se adoptará
como núcleo porque su problema principal son los shaders de imagen, no la
semántica de una aplicación.

[procmod/overlay](https://github.com/procmod/overlay) es una referencia más
pequeña para una ventana Windows transparente, always-on-top, click-through y
renderizada con Direct3D 11. Su patrón de ventana y composición es directamente
útil para el primer prototipo nativo.

**Lo que tomamos:** ventana transparente, coordenadas relativas a la ventana,
alpha blending, passthrough, seguimiento de posición y render GPU.

**Lo que no tomamos:** HUD permanente, captura indiscriminada, interacción
oculta o dependencia de una aplicación concreta.

### 2. Excalidraw y tldraw: el lenguaje visual de X-ANA-X

[Excalidraw](https://github.com/excalidraw/excalidraw) aporta un formato abierto
de elementos, flechas, etiquetas, vínculos, undo/redo y un canvas local-first.
[tldraw](https://github.com/tldraw/tldraw) aporta primitivas extensibles, formas
personalizadas, bindings, hooks y un editor controlable por API.

No queremos convertir FARMAXIA en un whiteboard. Queremos extraer su gramática
de relaciones: nodo, ancla, flecha, agrupación, foco, transición y reversión.
La licencia de tldraw exige revisar las condiciones de producción; por eso se
considera referencia, no dependencia inicial.

**Lo que tomamos:** representación de relaciones y escenas, no su interfaz de
whiteboard.

Ejemplo X-ANA-X:

```text
operación Blender desconocida
        ↕ equivalencia aproximada
operación Maya conocida
        ↓ diferencia / límite / ejemplo
acción verificable sobre Blender
```

La analogía debe conservar el objeto original, declarar dónde no hay
equivalencia y poder desaparecer sin dejar una segunda aplicación abierta.

### 3. Rich + Tree-sitter: el cuerpo de CODE-INE

[Rich](https://github.com/Textualize/rich) demuestra que una biblioteca puede
convertir logs, tracebacks, tablas, Markdown, progreso, estilos y sintaxis en
una salida visual legible. [Tree-sitter](https://github.com/tree-sitter/tree-sitter)
aporta un árbol sintáctico incremental, rápido y tolerante a errores para
identificar estructuras mientras se edita.

Rich no es el producto CODE-INE y Tree-sitter no explica por sí solo el código.
Juntos ofrecen el patrón correcto: eventos de ejecución + anclas semánticas del
código + representación visual incremental.

Ejemplo CODE-INE:

```text
log de error
   ↓
archivo / función / nodo causal
   ↓
evento: primer fallo, retry, repetición, solución
   ↓
traza visual temporal sobre editor y terminal
```

Una repetición del mismo error no produciría cinco alertas aisladas: mostraría
un ciclo. Una solución confirmada mostraría la salida del ciclo. La intensidad
visual debe ayudar a recuperar legibilidad, no aumentar artificialmente la
frustración.

## Contrato común

Los adaptadores producirán eventos locales y tipados, por ejemplo:

```json
{
  "event": "code.error",
  "source": "terminal",
  "anchor": {"window_id": "...", "file": "main.py", "line": 42},
  "causes": ["NameError"],
  "attempt": 3,
  "confidence": 0.91,
  "privacy": {"screen_pixels": "ephemeral", "network": false}
}
```

El compound correspondiente no dibujará libremente. Generará un plan limitado
por un catálogo local de primitivas:

- `anchor`: fija una relación a una ventana, línea, control o región;
- `path`: conecta causa, explicación y acción;
- `focus`: modifica prioridad perceptiva;
- `explain`: añade texto, analogía o diferencia;
- `pulse`: representa un evento temporal acotado;
- `group`: reduce complejidad agrupando elementos;
- `reversible`: permite retirar la capa completa.

La fuente factual y la capa de representación estarán separadas. El renderer
no podrá inventar una acción de aplicación ni ejecutar código arbitrario.

## Tres prototipos directos

### Prototipo A — Overlay real

Ventana transparente sobre una aplicación existente, sin panel propio:

1. detectar ventana activa, monitor, DPI y rectángulo;
2. dibujar una marca, foco o conexión sobre esa ventana;
3. pasar teclado y mouse a la aplicación original;
4. mover/redimensionar el overlay junto a la ventana;
5. apagarlo completamente con una tecla de emergencia.

Primera prueba: trabajar en un editor o navegador y mostrar sólo un foco suave
sobre el área activa. No habrá cámara ni eye tracking en esta prueba.

### Prototipo B — X-ANA-X Maya → Blender

Un adaptador de aprendizaje recibe una operación conocida en Maya y la conecta
con una operación de Blender. El overlay dibuja la relación junto a la zona
real de Blender, muestra la diferencia y guía una acción concreta.

Resultado verificable: la persona puede cerrar la explicación y repetir la
operación en Blender sin que X-ANA-X permanezca visible.

### Prototipo C — CODE-INE en terminal/editor

Un adaptador local recibe logs de un proceso de prueba, Tree-sitter ubica las
estructuras del código y el overlay relaciona error, retry y solución. Rich se
puede usar inicialmente como renderer de terminal; el overlay nativo será la
capa transversal.

Resultado verificable: cada evento visual puede rastrearse a una línea de log o
de código y puede apagarse sin modificar el proyecto observado.

## Qué adoptaremos y qué sólo estudiaremos

| Proyecto | Decisión |
|---|---|
| procmod/overlay | estudiar e implementar el patrón de overlay nativo |
| ShaderGlass | estudiar composición, shaders y passthrough |
| Excalidraw | estudiar formato de relaciones y reversión |
| tldraw | estudiar bindings y canvas API; no dependencia inicial |
| Rich | dependencia candidata para CODE-INE terminal |
| Tree-sitter | dependencia candidata para anclas semánticas de código |
| A2UI | estudiar contrato agente-renderer, no catálogo de widgets |
| OBS Studio | estudiar captura/composición; no incorporar su tamaño/licencia al núcleo |
| Continue | referencia histórica de agente de código; no dependencia, su repositorio está archivado |

[A2UI](https://github.com/a2ui-project/a2ui) es útil como inspiración para
mensajes declarativos entre agente y renderer, pero FARMAXIA necesita primitivas
de atención, relación y ritmo, no una galería de componentes.

## Por qué puede ser difícil de copiar

La diferenciación no estará en una ventana transparente ni en un efecto de
color aislado. Estará en la combinación de:

- contrato semántico común entre aplicaciones;
- adaptadores para cada contexto;
- lenguaje de representación temporal y espacial;
- perfiles de analogías de X-ANA-X;
- trazabilidad de CODE-INE desde log hasta visualización;
- adaptación perceptiva de VIZZ;
- pruebas de no intervención, reversión y privacidad.

Eso no hace que el proyecto sea incopiable; sí lo convierte en un sistema de
conocimiento y comportamiento difícil de reproducir mirando sólo la interfaz.

## Decisión de implementación

No descargaremos repositorios completos ni ejecutables todavía. Primero
implementaremos en FARMAXIA un contrato propio compatible conceptualmente con
estos patrones. Después incorporaremos sólo dependencias reputadas, fijadas a
una versión, con licencia revisada y sin binarios opacos.

El siguiente bloque de código debe ser un `overlay_runtime` pequeño, no otra
interfaz demo. Sobre él construiremos un evento de X-ANA-X y uno de CODE-INE,
para demostrar que la misma capa puede explicar una aplicación y también
representar un proceso de programación.

## Kill tests

- Si el overlay necesita modificar la aplicación original, falla.
- Si no puede apagarse de inmediato, falla.
- Si no puede señalar la fuente del evento, falla.
- Si genera una interfaz permanente propia, deja de ser FARMAXIA.
- Si una analogía oculta las diferencias entre Maya y Blender, X-ANA-X falla.
- Si una animación hace más difícil encontrar el error, CODE-INE falla.
- Si la cámara o la red son requisitos del primer prototipo, el diseño falla.
