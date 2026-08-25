# Decisión 066 — CODE-INE como compilador de experiencia

Fecha: 2026-08-25

## Decisión

CODE-INE abre un frente propio: no será sólo un generador de código ni un
lector de frustración. Será un **compilador de experiencia de construcción**.
Su entrada es una intención declarada; su salida son cuatro artefactos
separables:

1. un mapa semántico contrastivo;
2. una representación intermedia de la tarea;
3. un plan de representación sensorial reversible;
4. una prueba externa que determine si la construcción conserva la intención.

```text
intención
   ↓
perfil de entrada + presupuesto de complejidad
   ↓
relaciones: equivalente / análogo / diferente / desconocido
   ↓
residuo explícito
   ↓
IR declarativa (estados, eventos, postcondiciones)
   ↓
oracle independiente
   ↓
plan de representación: foco, capas, ritmo, movimiento, pausa, control
```

La sensación no es un objetivo farmacológico ni una variable psicológica
oculta. Es la forma en que el sistema hace perceptible una relación: puede
revelar por capas, mantener una ancla, bajar el movimiento, pausar ante una
señal declarada de atasco o mostrar el detalle técnico. La persona debe poder
previsualizar, aceptar, revertir y pedir la representación completa.

La composición entre hipótesis queda delimitada así:

```text
X-ANA-X  produce el mapa de relaciones y sus residuos
CODE-INE compila el mapa en una estructura construible y verificable
VIZZ     representa el estado con foco, capas, ritmo y pausa
```

Cada capa puede funcionar sin la siguiente. VIZZ no debe ejecutar una
intención; X-ANA-X no debe llamar equivalente a lo que sólo es análogo; y
CODE-INE no debe aceptar como correcto un resultado que no tiene oracle.

## Por qué esta ruta

Las tres listas convergen en una idea más fértil que “hacer una interfaz”:

- **perfil de entrada adaptativo:** la persona elige si entra desde lo guiado,
  lo técnico, lo rápido o lo quieto;
- **analogía contrastiva:** X-ANA-X puede transferir estructura, pero debe
  mostrar qué no se transfiere;
- **presupuesto de complejidad:** la representación puede limitar el número de
  conceptos simultáneos sin ocultar el sistema completo;
- **prueba de transferencia:** CODE-INE no acepta que una explicación se
  convierta en una construcción hasta que un oracle externo la pueda comprobar;
- **compilador de experiencia:** el mismo estado puede expresarse como mapa,
  código, trazo, pausa o resumen sin cambiar la semántica de origen.

El primer fixture usa una política de estados de un juego arcade como dominio
familiar y un ciclo de recuperación de trabajo como dominio objetivo. No
pretende enseñar Pac-Man ni invertir un juego real: prueba que la unidad
transferida puede ser una relación abstracta —meta activa, cambio de estado,
fallo visible, recuperación acotada— y no una lista de botones.

## Research informático

La arquitectura adopta principios, no dependencias todavía:

- [A2UI](https://github.com/google/A2UI) separa el mensaje declarativo del
  renderer y restringe al agente a un catálogo de componentes confiables. Para
  CODE-INE, la consecuencia es separar la IR de cualquier ejecución real;
- el [protocolo A2UI](https://github.com/a2ui-project/a2ui/blob/main/specification/v1_0/docs/a2ui_protocol.md)
  exige que los identificadores estructurales y los catálogos sean resolubles,
  lo que inspira validación de referencias antes de renderizar;
- [Tree-sitter](https://github.com/tree-sitter/tree-sitter) mantiene un árbol
  sintáctico incremental y tolerante a errores. Es un candidato futuro para
  que CODE-INE conserve estructura mientras cambia código, pero no se descarga
  aún ni forma parte del runtime;
- el oracle independiente y las mutaciones continúan la línea ya probada en
  `experiments/029-codeine-executable-oracle`: una puntuación declarada no
  puede reemplazar una verificación externa.

## Research de interacción y accesibilidad

- [W3C WAI: adaptación y personalización](https://www.w3.org/WAI/WCAG2/supplemental/objectives/o8-personalization/)
  recomienda permitir opciones familiares, simplificación y control sobre
  cuándo cambia el contenido. Esto se implementa como perfil declarado y
  controles reversibles, no como diagnóstico automático;
- [WAI-Adapt](https://www.w3.org/WAI/adapt/) respalda ocultar información
  extraneous para comprender la tarea principal, pero no autoriza borrar el
  contexto necesario. Por eso el plan conserva anclas y ofrece `show_full`;
- la adaptación sólo se acepta como representación si no convierte el color,
  el movimiento o el tempo en el único canal de significado. Los tokens del
  experimento combinan etiqueta, forma y relación semántica;
- `declared_friction` es una señal de interacción explícita. No se llama
  “ansiedad”, “TDAH”, intoxicación ni emoción: el sistema no observa el cuerpo
  ni presume el estado del usuario.

## Contrato de datos

```text
Intent
  statement
  entry_profile
  familiar_domain / target_domain
  declared_preferences
  complexity_budget

ContrastiveMap
  source, target
  relation: equivalent | analogous | different | unknown
  preserves
  residue

BuildIR
  states
  events
  observable
  postcondition
  execution_policy

RepresentationPlan
  focus
  disclosure_layers
  tempo_policy
  motion_policy
  intensity_policy
  friction_policy
  controls
  reversible

Evidence
  compiled_trace
  independent_oracle_trace
  status
```

No se permite que `unknown` se convierta silenciosamente en `equivalent`.
Una analogía sin residuo queda bloqueada. Un estado sin postcondición no puede
cruzar a ejecución. Un plan sin `preview`, `accept` o `revert` no se presenta
como adaptación segura.

## Experimento implementado

El vertical slice está en
`experiments/060-codeine-experience-compiler/`. Es local, determinista y sin
dependencias externas. Compila una máquina declarativa, genera un esquema de
código inspeccionable —no ejecutable—, corre una traza sintética contra un
oracle independiente y deriva un plan sensorial acotado.

Resultado aceptable:

```text
COMPILED_VERIFIED_WITH_RESIDUE
```

El sufijo importa: la construcción es verificable, pero el mapa conserva
diferencias y desconocidos. La incertidumbre queda representada, no escondida.

## Kill tests y límites

- relación no equivalente sin residuo → `BLOCKED`;
- transición mutada → desacuerdo con oracle;
- ausencia de reversión → `BLOCKED`;
- destello periódico → `BLOCKED`;
- evento no explicado → `BLOCKED`/`UNAVAILABLE`;
- nunca se lanza una aplicación, se ejecuta código generado, se usa cámara,
  red o datos humanos.

Esto no prueba comprensión humana, reducción de ansiedad ni mejora de
productividad. La siguiente fase, si el contrato sobrevive, será construir un
renderer local de la IR y comparar dos representaciones de la misma tarea sin
modificar el contenido fuente. Después se puede estudiar un adaptador real,
por ejemplo documentación oficial de Blender/Maya, manteniendo permisos,
versiones, precondiciones y verificador separado.
