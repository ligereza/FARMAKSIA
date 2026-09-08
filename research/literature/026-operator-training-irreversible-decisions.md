# Research 026 — aprender a decidir cuando no existe Ctrl+Z

**Fecha de corte:** 2026-08-31  
**Pregunta:** ¿Cómo aprende una persona sin experiencia a supervisar un sistema
crítico y cómo se reduce la duda cuando una acción física no puede deshacerse?

## Alcance

La investigación se limita a formación, factores humanos, simulación,
confianza calibrada, comunicación, verificación y diseño seguro de interfaces.
No cubre tácticas, selección de objetivos, empleo de armas, espionaje operativo
ni instrucciones para operar sistemas reales. Para FARMAXIA, el dominio se
representa con un simulador local no conectado a vehículos.

## Respuesta corta

Un operador competente no supera la duda aprendiendo a actuar siempre más rápido.
Aprende a distinguir cinco estados:

```text
normal → incierto → degradado → comprometido → recuperado
```

En cada estado sabe:

1. qué está observando;
2. qué parte es interpretación del sistema;
3. qué puede hacer la persona y qué no;
4. qué evidencia falta;
5. cuál es el estado seguro o la escalada disponible.

Cuando no existe deshacer, el sistema desplaza el “undo” hacia antes de la
acción:

```text
observar → interpretar → comprobar → confirmar → comprometer
                                    ↘ pausar / abortar / escalar
```

Después del compromiso queda registro y aprendizaje, pero no se finge que una
revisión posterior puede revertir el daño.

## Qué aprende realmente un operador nuevo

### 1. Modelo mental del sistema

Primero aprende estados y transiciones, no combinaciones de botones. Debe poder
explicar qué significa cada indicador, qué entradas usa el sistema, qué demora
existe, qué fallos son conocidos y qué comportamiento no debe aceptar.

La directiva pública DoDD 3000.09 exige que la formación y los procedimientos
permitan comprender capacidades y limitaciones bajo condiciones realistas; sus
criterios también mencionan interfaces comprensibles, feedback transparente del
estado y procedimientos claros para activar y desactivar funciones.
[DoDD 3000.09, 2023](https://media.defense.gov/2023/jan/25/2003149928/-1/-1/0/dod-directive-3000.09-autonomy-in-weapon-systems.pdf)

El principio transferible es válido incluso fuera del ámbito militar:
**conocer la limitación del sistema es una habilidad de operación, no una nota
al pie del manual**.

### 2. Reconocimiento de normalidad y anomalía

Si la persona sólo practica el camino perfecto, aprende a confiar en la
apariencia de la interfaz. La formación efectiva introduce retardos, datos
faltantes, mensajes ambiguos, cambios de modo y comportamientos inesperados en
un entorno controlado.

En una investigación con equipos humano-autonomía que operaban una aeronave
remotamente pilotada simulada, se inyectaron fallos de automatización y de
autonomía. Los equipos fueron más resilientes ante fallos explícitos de la
interfaz que ante fallos del agente autónomo cuyo comportamiento anormal era más
difícil de reconocer; los autores relacionan esa dificultad con ambigüedad,
sobreconfianza y menor seguridad del equipo en su propio diagnóstico.
[Demir et al., 2019](https://doi.org/10.1177/1071181319631020)

Por tanto, la práctica debe enseñar “esto no cuadra” antes de enseñar “qué
botón presiono”.

### 3. Comunicación y confianza calibrada

La confianza útil no es confianza máxima. Es que la confianza de la persona se
parezca a la capacidad real del sistema en ese contexto.

Un estudio de entrenamiento en equipos humano-autonomía comparó coordinación,
calibración de confianza y control en misiones simuladas con fallos. La
formación de coordinación mejoró ciertos patrones de intercambio y la
superación de fallos; la formación que mostraba las limitaciones del agente
hizo más estable la confianza frente a fallos, aunque no mejoró por sí sola
todos los resultados de rendimiento.
[Johnson et al., Human Factors](https://pubmed.ncbi.nlm.nih.gov/34595958/)

La conclusión es importante para X-ANA-X: explicar las limitaciones sí modifica
el modelo mental, pero una explicación bonita no basta. La persona también debe
practicar alternativas, persistencia, petición de información y recuperación.

### 4. Decisión bajo presión

El entrenamiento no debería medir sólo tiempo de respuesta. Debe medir si el
operador detecta una condición anómala, escoge una acción proporcional, conserva
la conciencia del estado y puede justificar la decisión después.

El entrenamiento de Crew Resource Management de la FAA usa comunicación,
liderazgo, resolución de problemas y toma de decisiones como capacidades
relacionadas, no como botones aislados.
[FAA, Crew Resource Management](https://www.faa.gov/training_testing/training/aqp/library)

Esto también explica por qué los checklists no son una señal de incompetencia:
son una memoria externa para impedir que la presión comprima demasiadas
decisiones en una sola intuición.

## Cómo se reemplaza Ctrl+Z en un mundo físico

No existe una operación universal de deshacer. Hay cinco sustitutos parciales:

| Antes de la acción | Durante | Después |
|---|---|---|
| simulación y ensayo | límites de autoridad | registro inmutable |
| precondiciones | confirmación explícita | revisión posterior |
| doble comprobación | pausa/abort | análisis de causa |
| estado seguro | interbloqueos | actualización de entrenamiento |
| escalada humana | monitorización | cambio controlado y revalidado |

La diferencia es temporal: **la prevención protege el mundo; el log sólo
protege el aprendizaje**.

DoDD 3000.09 exige verificación y validación, pruebas realistas, evaluación de
comportamientos emergentes y procedimientos para activar/desactivar funciones;
además pide que cambios de software o de estados vuelvan a probarse cuando
puedan afectar características críticas.
[DoDD 3000.09, secciones de V&V y HMI](https://media.defense.gov/2023/jan/25/2003149928/-1/-1/0/dod-directive-3000.09-autonomy-in-weapon-systems.pdf)

No lo interpretamos como permiso ni como receta de armas. Lo tomamos como una
regla de ingeniería: una interfaz que cambia la capacidad de decisión debe
tener límites, pruebas, reversión cuando sea posible y una vía clara de
interrupción.

## Arquitectura formativa para FARMAXIA

El entrenamiento del prototipo debe tener seis fases, cada una con una salida
observable:

```text
1. mapa       → explica estados y roles
2. rutina     → completa una tarea sin sorpresa
3. perturbada → detecta una anomalía conocida
4. ambigua    → separa observación de inferencia
5. recuperación→ elige pausa, alternativa o escalada
6. debrief    → reconstruye evidencia y decisión
```

### Aplicación a los tres frentes

- **VIZZ:** hace visible qué cambió y dirige la atención sin ocultar el contexto.
  Una señal de saliencia nunca debe sustituir el dato ni impedir la pausa.
- **X-ANA-X:** enseña un procedimiento desconocido mediante una estructura
  conocida, pero debe mostrar también dónde la analogía se rompe. La analogía
  ayuda a formar un modelo mental; no autoriza la acción.
- **CODE-INE:** convierte estados, precondiciones, permisos, confirmaciones,
  abortos y resultados en contratos auditables. El código visual no debe
  simular reversibilidad donde no existe.

## Modelo matemático mínimo

Sea `z` el estado del sistema, `o` lo que observa el operador, `a` una acción y
`C(a,z)` el costo de equivocarse. La formación debe minimizar el riesgo esperado
y la carga de decisión:

```text
L = E[C(a,z)] + λ · tiempo + μ · carga + ν · sobreconfianza
```

Antes de una acción no reversible, una política de seguridad puede exigir:

```text
permitir(a) = estado_válido
              ∧ evidencia_suficiente
              ∧ autoridad_vigente
              ∧ modo_conocido
              ∧ confirmación_explícita
```

Si falla una condición, el resultado no debe ser una pantalla vacía. Debe ser
una salida accionable y segura: **PAUSAR**, **SOLICITAR VERIFICACIÓN**,
**CAMBIAR A ESTADO SEGURO** o **ESCALAR**.

La duda no se elimina; se convierte en una decisión visible con costo y ruta de
resolución.

## Qué debe mostrar la interfaz durante el entrenamiento

Cada evento debe tener al menos:

```text
estado actual
fuente y hora
edad de la evidencia
confianza y supuestos
modo de operación
acción disponible
precondición
vía de pausa/aborto
resultado esperado y verificador
```

La pantalla inicial puede ser simple. La profundidad aparece bajo demanda:
primero el estado, luego la razón, después el historial. Así se evita tanto el
HUD saturado como el chatbot que responde sin demostrar de dónde salió la
respuesta.

## Prueba que debemos construir

En vez de entrenar con armas o vehículos, crear un simulador local con eventos
de sensores y documentos sintéticos. En cada ronda:

1. el sistema muestra un estado normal;
2. aparece una anomalía explícita, ambigua o contradictoria;
3. el operador elige continuar, pausar, pedir verificación o volver al estado
   seguro;
4. un verificador oculto comprueba si identificó correctamente la situación;
5. el debrief reconstruye qué observó y qué inferencia hizo.

Comparar entrenamiento sin fallos, con fallos visibles y con fallos ambiguos.
Medir:

- detección correcta antes del compromiso;
- falsos positivos y omisiones;
- elección de pausa/escalada proporcional;
- tiempo hasta decisión correcta;
- recuperación después de una falsa alarma;
- coincidencia entre confianza declarada y desempeño real;
- capacidad de explicar la evidencia;
- carga subjetiva y estabilidad de la interfaz.

## Kill tests

- Si el usuario actúa más rápido pero aumenta los compromisos erróneos, el
  entrenamiento fracasa.
- Si la interfaz muestra una advertencia pero no cambia la decisión frente a
  evidencia contradictoria, la advertencia es decorativa.
- Si la persona confía más después de ver sólo demostraciones perfectas, el
  entrenamiento está calibrando sobreconfianza.
- Si la adaptación visual cambia el significado de un evento o no permite
  recuperar la vista estable, VIZZ debe desactivarse.
- Si una explicación generada no puede reconstruirse desde evidencia registrada,
  X-ANA-X/CODE-INE deben marcarla como no verificable.

## Decisión

La vía válida para FARMAXIA es **entrenamiento de juicio y recuperación**, no
entrenamiento de puntería ni de velocidad de control. El siguiente objetivo es
implementar el simulador sintético y su verificador con tres estados mínimos:
`OBSERVED`, `INFERRED`, `ACTIONABLE`, más `PAUSE/ESCALATE` como salidas de
seguridad.

La probabilidad de que este enfoque produzca un prototipo útil es alta porque
se puede probar localmente, medir y revertir. La probabilidad de que una
interfaz por sí sola convierta a alguien sin experiencia en operador apto para
un sistema real es baja: la competencia exige práctica supervisada, doctrina,
certificación, equipo y responsabilidades institucionales que el software no
puede sustituir.

