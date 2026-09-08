# Research 028 — diálogo orientado a tareas, reparación y handoff

**Fecha de corte:** 2026-08-31  
**Pregunta:** ¿Cómo puede una interfaz dialogar con una persona que no sabe
qué hacer, reparar una interpretación equivocada y transferir el caso a un
humano sin obligarla a empezar de nuevo?

## Corrección de enfoque

La investigación anterior se quedó en el nivel de “detectar el atasco y
mostrar una ayuda”. Eso no cubría el ejemplo del tótem, donde la persona dice o
señala una duda y el guardia responde.

La función correcta es un **diálogo orientado a tareas** (*task-oriented
dialogue*), no un chatbot general:

```text
estado de tarea
→ duda o atasco
→ propuesta contextual
→ respuesta del usuario
→ confirmación / reparación
→ siguiente estado o handoff
```

El diálogo no tiene que ser sólo voz. Puede combinar texto breve, botones,
ilustración, teclado, audio opcional o una persona asistente. Lo esencial es que
cada turno modifique o confirme un estado de tarea verificable.

## Cómo funciona el diálogo en sistemas reales

### 1. Iniciativa mixta

En un diálogo de iniciativa única, sólo el usuario o sólo el sistema dirige el
flujo. En la **iniciativa mixta**, ambos pueden aportar información: el usuario
puede preguntar algo inesperado y el sistema puede pedir una aclaración o
mostrar información pertinente cuando detecta una omisión.

El trabajo TITAN estudia precisamente diálogos orientados a tareas con
iniciativa mixta: el sistema puede preguntar activamente para resolver una
ambigüedad o proporcionar información cuando detecta una petición implícita.
Sus autores advierten que los modelos todavía tienen dificultades para generar
alternativas útiles, por lo que no debe suponerse que un LLM resolverá el
problema por sí solo.
[TITAN, IJCAI 2023](https://www.ijcai.org/proceedings/2023/583)

Para el tótem esto significa:

```text
usuario: “¿Cuál tarjeta uso?”
sistema: “Para esta operación aparecen débito y crédito. ¿Cuál tienes?”
usuario: “No sé la diferencia.”
sistema: “Débito descuenta de tu cuenta; crédito usa tu línea. Puedes elegir
una, volver o pedir asistencia.”
```

La respuesta se ancla en el paso actual. No abre una conversación infinita.

### 2. Grounding y reparación

En interacción humano-máquina, el sistema debe crear un “terreno común”:
demostrar qué entendió, qué falta y qué consecuencia tendrá la elección. Si la
interpretación es incierta, repara con una pregunta mínima.

Una reparación buena tiene esta forma:

```text
entendí: [elección concreta]
falta:   [un dato o decisión]
consecuencia: [qué ocurrirá después]
opciones: [A] [B] [volver] [ayuda humana]
```

No pregunta “¿sigues ahí?”, porque eso no reduce la incertidumbre de la tarea.
Pregunta lo mínimo que separa dos caminos posibles.

### 3. Fallback por etapas y handoff

Rasa, un proyecto abierto de diálogo, implementa patrones separados para
corrección, aclaración, cancelación, interrupción, error y handoff humano. Su
fallback de dos etapas puede primero pedir confirmación o reformulación y sólo
después transferir el caso a una persona.
[Rasa, conversation patterns](https://rasa.com/docs/reference/primitives/patterns/)
[Rasa, fallback y handoff](https://legacy-docs-oss.rasa.com/docs/rasa/fallback-handoff/)

El patrón importante no es instalar Rasa automáticamente, sino conservar tres
reglas:

1. **reparar antes de reiniciar**;
2. **escalar cuando la incertidumbre persiste**;
3. **transferir el contexto completo**.

El paquete de handoff debería contener etapa actual, respuestas válidas,
errores, último estado confirmado y pregunta pendiente. El usuario no debería
tener que repetir toda la historia frente a la fila.

## Cómo medir si el diálogo ayudó

El diálogo no se evalúa por hablar mucho ni por sonar natural. PARADISE propuso
separar éxito de tarea y costo del diálogo, incluyendo duración, número de
turnos y otros costos conversacionales, para comparar estrategias distintas.
[PARADISE, Walker et al.](https://arxiv.org/abs/cmp-lg/9704004)

Para un tótem, las métricas son:

```text
éxito de tarea
− errores
− abandono
− turnos innecesarios
− tiempo total
− handoffs evitables
+ recuperación sin repetir datos
+ confianza calibrada en la decisión
```

Un diálogo más corto no es mejor si termina en una elección incorrecta. Un
diálogo más largo puede ser mejor si evita un error costoso y entrega el caso
completo a la persona adecuada.

## La duda como estado conversacional

La detección de atasco activa el diálogo, pero no decide su contenido. El
contenido sale del estado de la tarea:

```text
NORMAL
  ↓ falta de progreso sostenida
DIFFICULTY_PROBABLE
  ↓ selección de “explicar” o respuesta ambigua
CLARIFY
  ↓ comprensión suficiente
GUIDED_STEP
  ↓ sigue sin resolverse
HANDOFF
  ↓ aceptación o intervención humana
RESUMED / ABANDONED
```

Una respuesta puede ser “no sé”, “explícame”, “quiero volver” o una elección
parcial. Todas son entradas válidas del diálogo. La interfaz no debe interpretar
“no sé” como consentimiento para elegir por la persona.

## Qué cambia en un sistema crítico

En un kiosco se puede detener la transacción. En un entorno bélico el mundo no
se detiene, pero una interfaz sí puede separar niveles de acción:

```text
informar → recomendar → confirmar → comprometer
```

El diálogo sirve para aclarar estado, intención, límites y alternativas antes
del compromiso. No debe convertirse en una autoridad que ejecute una orden
ambigua. Para acciones de bajo costo puede bastar una recomendación visible;
para acciones irreversibles se necesita confirmación explícita, autoridad
vigente, estado conocido y una vía de interrupción cuando exista.

La formación del operador debe practicar conversaciones de fallo:

```text
agente: “No puedo confirmar este estado.”
operador: “Continúa.”
agente: “Falta una condición; puedo mostrar evidencia, mantener espera o
escalar.”
```

El objetivo es que el operador aprenda a no convertir una respuesta ambigua en
una orden segura por mera presión temporal.

## Diálogo e incentivos

El diálogo no debe tener puntos por cantidad de acciones, rapidez o cantidad de
casos cerrados. Eso crea un atajo: responder “sí” o comprometer antes para
mejorar la métrica.

La evaluación debe premiar la decisión calibrada:

```text
si evidencia suficiente y estado claro → avanzar
si evidencia insuficiente y costo alto → pausar/escalar
si interpretación incorrecta → reparar
si resultado confirmado → cerrar
```

El análisis reciente de programas de puntos para unidades de drones muestra por
qué una métrica operativa puede convertirse en objetivo sustitutivo: el sistema
premia lo que es fácil de contar, aunque no capture todo el resultado ni sus
costos.
[Análisis sobre Army of Drones](https://link.springer.com/article/10.1057/s41311-026-00753-w)

Para FARMAXIA, la “moneda” correcta no es una coin visible durante la acción.
Es un informe posterior de calibración: qué decidió, con qué evidencia, qué
alternativas rechazó, si pidió ayuda y si el resultado verificado coincidió con
la intención.

## Diseño propuesto para FARMAXIA

### X-ANA-X: diálogo de analogía

Cuando el usuario no entiende una etapa, X-ANA-X puede preguntar:

```text
“¿Quieres una explicación breve, un ejemplo conocido o comparar dos opciones?”
```

Después entrega una analogía con cuatro piezas:

```text
equivalencia → diferencia → límite de la analogía → siguiente elección
```

Nunca debe ocultar la diferencia ni avanzar automáticamente sólo porque la
persona aceptó la explicación.

### VIZZ: diálogo espacial y atencional

VIZZ puede llevar la explicación al punto que genera el atasco: ampliar el
control, iluminar la etapa, mostrar una relación o reducir el ruido visual. No
necesita afirmar que conoce la intención ocular; la mirada es sólo una señal
auxiliar y el usuario siempre puede pedir ayuda por teclado, mouse o botón.

### CODE-INE: contrato conversacional

CODE-INE debe registrar cada turno como evento tipado:

```text
dialogue_started
stage_context_shown
interpretation_proposed
clarification_requested
user_confirmed / user_corrected
help_exposed / help_accepted
handoff_requested / handoff_completed
commit_requested / commit_confirmed
outcome_verified
```

El diálogo debe poder reproducirse sin el modelo generativo: estado, pregunta,
respuesta, decisión y resultado. Así se puede auditar si el agente realmente
ayudó o sólo produjo una explicación convincente.

## Primer experimento sin cámara ni sistema externo

Construir una transacción sintética de cuatro pasos con un pequeño diálogo
contextual. Comparar:

1. interfaz sin diálogo;
2. ayuda contextual con opciones cerradas;
3. diálogo de iniciativa mixta con reparación y handoff preservando progreso;
4. chatbot libre como control negativo.

Inyectar cuatro casos:

- usuario lento pero progresando;
- usuario rápido que se congela;
- elección ambigua;
- error que el usuario corrige.

El verificador conoce la intención objetivo y el estado real. Se mide éxito,
errores, turnos, tiempo, abandono, handoff y recuperación. El chatbot libre
será útil como comparación: si habla más pero no mejora el resultado, la
hipótesis queda refutada.

## Kill tests

- Si el diálogo pregunta sin reducir el conjunto de opciones, es ruido.
- Si responde algo correcto pero no cambia el estado de la tarea, es un
  chatbot decorativo.
- Si el usuario debe repetir datos después del handoff, falla la continuidad.
- Si una respuesta ambigua provoca un compromiso automático, falla la seguridad.
- Si la versión más rápida produce más errores que la versión guiada, la métrica
  de velocidad no puede gobernar la selección.
- Si un sistema gana más puntos por comprometer que por pausar correctamente,
  el incentivo está mal diseñado.

## Decisión

El diálogo sí forma parte del producto, pero como **protocolo de continuidad y
reparación**, no como una ventana conversacional genérica. Su motor es el estado
de la tarea y su prueba es el resultado verificado.

El siguiente objetivo es implementar el diálogo mínimo en el simulador de
kiosco: propuesta contextual, aclaración de una sola ambigüedad, corrección,
handoff con contexto y cierre verificado. Después se puede llevar el mismo
contrato a una interfaz compleja o a una simulación de supervisión, sin conectar
armas ni sistemas reales.

