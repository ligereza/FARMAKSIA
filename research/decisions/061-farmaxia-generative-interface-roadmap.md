# ADR 061 — futuro de FARMAKSIA como compilador de representación

Fecha: 2026-08-25  
Estado: propuesta de dirección; la implementación debe pasar los experimentos
de representación antes de convertirse en runtime estable.

## Decisión estratégica

FARMAKSIA no competirá con los frameworks que generan componentes. Su apuesta
será una capa intermedia que decide **cómo debe aparecer la información** antes
de entregarla a un renderer.

```text
app / agente / fuente
        ↓
modelo semántico
        ↓
FARMAKSIA RepresentationPlan
        ↓
renderer confiable y catálogo de componentes
        ↓
experiencia visual, temporal, espacial o multimodal
```

La unidad principal será `RepresentationPlan`, no `Button`, `Card` ni
`Dashboard`.

## Qué se toma de cada referencia

| Referencia | Se adopta | No se adopta como núcleo |
|---|---|---|
| [A2UI](https://github.com/a2ui-project/a2ui) | contrato declarativo, IDs estables, catálogo aprobado, separación agente/renderer, actualizaciones incrementales | su catálogo de componentes como teoría completa de experiencia |
| [OpenUI](https://github.com/thesysdev/openui) | lenguaje de composición, streaming y biblioteca que limita la generación | generación directa de una UI sin un plan semántico y sensorial previo |
| [MCP Apps](https://github.com/modelcontextprotocol/ext-apps) | adapter para mostrar representaciones en contexto, vistas aisladas y comunicación host↔vista | dependencia del chat como superficie principal de FARMAKSIA |
| [W3C Personalization](https://www.w3.org/WAI/WCAG2/supplemental/objectives/o8-personalization/) | semántica de contenido, simplificación, preferencias familiares, control y reversión | una adaptación automática que oculte cambios o elimine capacidades |
| [Design Tokens](https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/) | vocabulario portable de decisiones de color, tipo, espacio, tema y referencias | tokens tratados como decoración sin relación con significado o ritmo |
| [Microsoft HAX](https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/) | explicar capacidad, actuar según contexto, permitir descartar/corregir y adaptar con cautela | personalización opaca, irreversible o guiada por permanencia |
| [Calm Technology](https://calmtech.com/papers/designing-calm-technology) | centro/periferia, señales ambientales y tránsito controlado de atención | una interfaz plana que esconda información crítica en la periferia |

## Futuro de los tres compuestos

### VIZZ — el renderer sensorial

VIZZ será el sistema que organiza el campo de presentación:

- dirige la atención sin exigir cámara;
- decide foco, periferia, anclas y recorrido;
- adapta densidad, escala, color, contraste, movimiento y profundidad;
- incorpora geometría de monitores;
- usa teclado, mouse, IMU o cámara sólo como capacidades disponibles y
  explícitas.

VIZZ no será un píxel predictor. Será la capa que convierte un plan abstracto
en una experiencia perceptual.

### X-ANA-X — el traductor pedagógico

X-ANA-X será el agente que cambia el espacio de representación cuando el
problema no se entiende:

```text
desconocido → fuente conocida → mapeo → visualización → predicción → verificación
```

La salida no será sólo una explicación textual. Podrá ser una secuencia visual,
un mapa de relaciones, una comparación, una simulación o una vista dual
fuente/objetivo.

### CODE-INE — el compilador de construcción

CODE-INE será la capa para quien necesita crear la interfaz:

```text
intención → esquema → plan visual → código → preview → oracle → iteración
```

Su diferencia frente a vibecoding será conservar el vínculo entre intención,
representación, código y comportamiento verificable.

## Roadmap Now / Next / Later

### Now — probar la unidad correcta

Objetivo: demostrar que FARMAKSIA puede cambiar la representación sin cambiar
la información subyacente.

1. Implementar el esquema mínimo de `RepresentationPlan`.
2. Definir un catálogo pequeño de componentes seguros y tokens semánticos.
3. Crear el experimento 022-A con una misma información en cinco
   representaciones: panel, guía, mapa, analogía y flujo de construcción.
4. Crear un renderer local HTML/SVG/Canvas sin cámara, red ni agente externo.
5. Medir cobertura semántica, pérdida de contexto, reversibilidad, latencia,
   cantidad de elementos y cambios de atención solicitados.
6. Crear el onboarding VIZZ para un operador nuevo usando foco de ventana,
   teclado, mouse y confirmaciones explícitas.

**Salida:** una demostración visible donde el contenido es constante y la
experiencia cambia por el `RepresentationPlan`.

### Next — convertir los compuestos en operaciones

Objetivo: hacer que un agente pueda proponer planes, no sólo texto o código.

1. Añadir un adaptador compatible conceptualmente con A2UI/OpenUI, sin adoptar
   aún sus dependencias completas.
2. Implementar X-ANA-X como operación `map_relation`, con fuente, objetivo,
   predicción y ruptura.
3. Implementar CODE-INE como flujo `intent → spec → preview → code → test`.
4. Añadir perfiles de intensidad y ritmo: `calm`, `guided`, `explore`,
   `build`, con nombres de parámetros y no diagnósticos humanos.
5. Implementar explicación, preview, aceptación, pausa, restauración y undo
   para cada cambio generativo.
6. Crear un renderer de centro/periferia que conserve contexto crítico y
   permita revelar progresivamente el detalle.
7. Comparar notificación inmediata, agrupada y periférica en un fixture
   reproducible.

**Salida:** un agente que puede decir “propongo mostrar esto como un mapa
porque necesito hacer visible esta relación” y luego ser aceptado o corregido.

### Later — convertirlo en una capa interoperable

Objetivo: hacer que FARMAKSIA pueda sentarse entre distintas fuentes y
superficies.

1. Adapter A2UI para renderers web y móviles.
2. Adapter MCP Apps para exponer planes en agentes compatibles.
3. Export/import basado en Design Tokens para temas y perfiles sensoriales.
4. VIZZ multimonitor con geometría física y capacidades opcionales de cabeza,
   IMU y ojos.
5. Renderers especializados: código, aprendizaje, monitorización, lectura,
   exploración y visualización de datos.
6. Biblioteca de compuestos combinables, por ejemplo `X-ANA-X → CODE-INE`:
   primero comprender, luego construir.
7. Evaluación con usuarios y tareas reales sólo después de que el contrato
   local sea auditable y reversible.

**Salida:** FARMAKSIA como una capa que puede transformar la presentación de
una herramienta, agente o flujo de trabajo sin obligar a reescribir su fuente.

## Prioridad

| Iniciativa | Valor | Esfuerzo | Prioridad | Dependencia |
|---|---:|---:|---|---|
| `RepresentationPlan` + catálogo | alto | medio | Must | ninguna |
| 022-A cinco representaciones | alto | bajo | Must | plan mínimo |
| Onboarding VIZZ sin cámara | alto | medio | Must | renderer local |
| X-ANA-X relacional verificable | alto | medio | Should | modelo semántico |
| CODE-INE preview/code/oracle | alto | alto | Should | catálogo + plan |
| Adaptador A2UI/OpenUI | medio | medio | Could | contrato estable |
| Adaptador MCP Apps | medio | medio | Later | renderer y seguridad |
| Eye tracking/IMU multimonitor | medio | alto | Later | VIZZ sin cámara validado |
| Modelo neuronal personalizado | bajo ahora | alto | Won't yet | datos y baseline |

## Criterios de éxito

FARMAKSIA avanzará si logra demostrar, con la misma información de entrada:

- mejor orientación de un operador nuevo;
- mejor transferencia de una relación enseñada por analogía;
- mejor trazabilidad entre intención, código y resultado;
- menor pérdida de contexto al reducir densidad;
- más control percibido sobre cambios generativos;
- reversión limpia y conservación del estado local;
- latencia y transiciones suficientemente estables para no producir saltos;
- mejora frente a una representación estática limpia, no frente a una UI
  deliberadamente mala.

No se optimizará tiempo de permanencia, número de clicks ni intensidad de
estimulación como objetivos principales. La métrica central será la calidad de
la relación entre información, representación, comprensión y acción.

## Riesgos y kill tests

- Si el agente genera componentes bonitos pero no puede declarar qué relación
  hacen visible, FARMAKSIA no está funcionando.
- Si la interfaz cambia sin preview, razón o undo, se bloquea la adaptación.
- Si simplificar destruye contexto crítico, se conserva la vista completa.
- Si los compuestos sólo producen estilos distintos pero no cambian una
  operación de comprensión o construcción, son temas visuales, no FARMAKSIA.
- Si el sistema aprende a maximizar atención o permanencia en lugar de agencia,
  comprensión y control, se rechaza la política.
- Si una dependencia externa introduce ejecución arbitraria, red obligatoria,
  telemetría opaca o pérdida de privacidad, se mantiene el renderer local.
- Si VIZZ requiere cámara para su función base, el roadmap retrocede a
  `NO_CAMERA`.

## Horizonte del proyecto

La visión de FARMAKSIA es convertirse en un **compilador de experiencias de
información**:

```text
no sólo generar la interfaz
sino generar la forma adecuada de percibir, aprender y construir con ella
```

El proyecto no termina cuando pueda producir una pantalla. Termina cuando
pueda justificar por qué eligió una representación, mostrar sus alternativas,
permitir que la persona la modifique y conservar una ruta verificable entre
significado y experiencia.
