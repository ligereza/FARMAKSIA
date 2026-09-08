# Research 027 — detectar atasco en kioscos y alinear incentivos

**Fecha de corte:** 2026-08-31  
**Pregunta:** ¿Cómo ayuda un sistema a una persona que empezó rápido y luego
se quedó detenida, sin interrumpirla con un “¿sigues ahí?”; y cómo se evita que
un sistema de recompensas premie la acción rápida equivocada?

## Veredicto

Sí: la interfaz debe hacer algo. Pero no debe adivinar “ansiedad” desde una
sola pausa ni expulsar al usuario por superar un tiempo promedio. Debe estimar
un **estado de atasco de tarea** con varias señales, intervenir primero de forma
silenciosa y contextual, y ofrecer ayuda humana o guiada antes del abandono.

En el segundo problema, la duda correcta no es un fracaso. El objetivo debe
premiar la **decisión calibrada**: continuar cuando la evidencia basta, pausar o
pedir ayuda cuando el costo de equivocarse es alto, y detectar/corregir un error
antes de comprometer el resultado.

## Qué hacen sistemas sencillos en la práctica

### 1. No usan sólo un temporizador

Un kiosco puede observar una secuencia de interacción sin usar cámara:

```text
etapa actual
→ tiempo hasta primera acción
→ tiempo entre acciones
→ errores de formato / toques repetidos
→ retrocesos y cambios de elección
→ confirmación o ausencia de confirmación
→ ayuda abierta / handoff / abandono
```

La señal relevante no es “lleva 20 segundos quieto”, sino “su patrón dejó de
progresar para esta etapa”. Alguien puede leer lentamente y estar avanzando;
otra persona puede tocar rápido y quedar bloqueada en el pago.

Un estudio de 2026 sobre ayuda *just-in-time* en kioscos formula precisamente
la confusión como un estado interno que se forma antes de pedir ayuda. En un
piloto con nueve participantes, la variabilidad de la expresión facial resultó
prometedora, mientras que las respuestas EEG fueron heterogéneas; los autores
proponen detectar dificultades sostenidas, no intervenir ante cada instante de
incertidumbre.
[Li et al., Procedia CIRP, 2026](https://doi.org/10.1016/j.procir.2026.05.195)

Esto respalda una regla importante para VIZZ: **no hace falta encender la
cámara para que la interfaz ayude**. La interacción nativa ya ofrece señales
útiles y menos invasivas.

### 2. La presión de la fila cambia el problema

En una investigación cualitativa de 2026 con adultos mayores usando kioscos,
la presión de la fila, la falta de confirmación y la ambigüedad del pago
incrementaron la duda, la búsqueda de ayuda y el abandono. El estudio encontró
que una ayuda visible dentro del flujo, mensajes de confirmación confiables,
texto legible y un camino predecible de recuperación podían convertir un atasco
en finalización.
[Cheng et al., SAGE Open, 2026](https://doi.org/10.1177/21582440261445622)

La consecuencia no es “forzar a la persona a terminar rápido”. Es ofrecer dos
salidas dignas:

```text
seguir con guía contextual
o
conservar el progreso y pedir asistencia
```

La ayuda humana no es una falla del kiosco; es parte del diseño del servicio.

### 3. La interfaz ayuda antes de preguntar

W3C recomienda feedback claro de éxito o error, instrucciones breves de
corrección y confirmación cuando una acción no puede deshacerse. También señala
que los diálogos son más intrusivos y deben reservarse para cambios que el
usuario podría no percibir.
[W3C, User Notification](https://www.w3.org/WAI/tutorials/forms/notifications/)
[W3C, confirmación de acciones irreversibles](https://www.w3.org/WAI/WCAG22/Techniques/general/G168)

Por eso el primer nivel de asistencia debe ser una modificación local y no una
ventana emergente:

```text
“Paso 2 de 4 · elige cómo pagar”
“Tu selección aún no se ha confirmado”
“Puedes revisar antes de continuar”
```

Si el sistema detecta errores, debe iluminar el campo o decisión concreta, no
declarar vagamente que el usuario “no entiende”.

### 4. La adaptación puede ser por usuario y por control

OptiDwell, una investigación de IBM para interacción mediante mirada, ajusta
el tiempo de permanencia según experiencia previa del usuario y el control
concreto. Su principio general es útil aunque FARMAXIA no adopte dwell-click:
un tiempo fijo para todos y para todas las etapas puede ser menos cómodo que
una política que aprende del historial local.
[OptiDwell, IBM Research](https://research.ibm.com/publications/optidwell-intelligent-adjustment-of-dwell-click-time)

La adaptación debe ser conservadora: cambia el nivel de ayuda, no el significado
del control ni la autoridad para ejecutar una acción.

## Cómo calcular la duda sin inventarla

La duda es una variable latente. Podemos estimar una probabilidad operacional
`p_stuck`, no leer una emoción ni diagnosticar a la persona.

Para cada etapa `s`, construir una línea base robusta con tareas comparables:

```text
z_gap   = (tiempo_entre_acciones − mediana_s) / (MAD_s + ε)
z_error = errores_recientes normalizados
z_back  = retrocesos y cambios de elección
z_rep   = intentos repetidos sin cambio de estado
```

Una puntuación inicial puede ser:

```text
H_t = w1·z_gap + w2·z_error + w3·z_back + w4·z_rep
p_stuck(t) = actualización_secuencial(H_t, estado_de_la_etapa)
```

No se deben fijar los `w` a priori como verdad universal. Se calibran con
trazas etiquetadas por resultado: completó, pidió ayuda, abandonó, corrigió o
cometió un error. La unidad de análisis es la sesión/tarea, no cada evento como
si fuera independiente.

El caso que planteas —inicio veloz y luego detención— es un **cambio de régimen**:
la velocidad inicial no debe “perdonar” el atasco posterior. El detector debe
comparar el progreso actual con la etapa vigente, no con la media global del
usuario.

## Política de ayuda en tres niveles

| Estado estimado | Intervención | Efecto esperado |
|---|---|---|
| progreso normal | sólo feedback de estado | no interrumpir |
| dificultad probable | guía junto al control, ejemplo, resaltado y revisar | reducir carga sin tomar control |
| atasco persistente | modo asistido, conservar datos, llamar a persona o cambiar de canal | evitar vergüenza, fila bloqueada y abandono |

La transición debe tener histéresis: entrar a ayuda requiere evidencia sostenida
y salir requiere progreso. Así se evita el parpadeo entre “ayuda/no ayuda”.

El disparador no debe decir “¿sigues ahí?”. Debe decir algo útil y específico:

```text
“Tu solicitud está guardada hasta este paso.”
“Falta elegir una opción para continuar.”
“Puedes revisar la selección o pedir ayuda.”
```

## El problema de las coins en contextos críticos

Un análisis reciente del programa ucraniano Army of Drones describe un sistema
de puntos para unidades basado en resultados verificados, canjeables por
equipamiento. El mismo análisis advierte una tensión: cuando el sistema hace
visible y premiable el conteo de determinados resultados, puede desplazar la
atención hacia aquello que suma puntos y concentrar datos sensibles.
[Giametta, International Politics, 2026](https://link.springer.com/article/10.1057/s41311-026-00753-w)

La lección no es que toda recompensa sea mala. Es que en sistemas de alto costo
el indicador no debe convertirse en el objetivo. El operador que duda
correctamente puede estar protegiendo el resultado; el que actúa rápido puede
estar acumulando una métrica equivocada.

### Métrica correcta

En vez de premiar clicks, velocidad o acciones aisladas, usar una utilidad
multicriterio:

```text
U = resultado_verificado
    − error_no_detectado
    − costo_de_falsa_alarma
    − costo_de_demora
    + pausa_correcta
    + escalada_correcta
    + evidencia_reproducible
```

La “pausa correcta” no vale siempre lo mismo: vale más cuando el costo de una
acción equivocada es alto y la evidencia es débil. La demora innecesaria sí debe
medirse, pero después de la corrección y la seguridad, no antes.

El objetivo de entrenamiento sería maximizar **calibración**:

```text
calibración = confianza declarada ≈ desempeño real en ese estado
```

No se recompensa dudar por dudar. Se recompensa reconocer cuándo continuar y
cuándo no comprometerse todavía.

## Cómo se traduce a FARMAXIA

### VIZZ

Detecta atasco desde el flujo de interacción y modifica saliencia local,
progreso, contraste o densidad. La cámara puede quedar apagada. La mirada, si
se usa, sólo añade contexto y no decide por sí sola que alguien está confundido.

### X-ANA-X

Cuando una persona se bloquea, ofrece una analogía de la etapa actual con un
procedimiento conocido, mostrando equivalencia y diferencia. No reemplaza la
decisión ni ejecuta la siguiente acción automáticamente.

### CODE-INE

Registra `stage_started`, `progress`, `error`, `backtrack`, `help_exposed`,
`help_accepted`, `handoff`, `commit`, `pause`, `escalate` y `outcome_verified`.
Así se puede distinguir “no sabía qué hacer” de “el sistema no confirmó lo que
hice”.

## Experimento mínimo, sin cámaras ni drones

Construir un kiosco sintético de cuatro pasos con tres condiciones:

1. interfaz plana con timeout fijo;
2. ayuda contextual basada en etapa y cambio de régimen;
3. ayuda contextual más handoff conservando el progreso.

Generar usuarios sintéticos y luego probar personas con cuatro trazas:

- normal;
- rápido y luego bloqueado;
- lento pero progresando;
- errores y retrocesos.

El verificador conoce el estado correcto, pero la interfaz no lo revela. Medir
finalización, errores, intervenciones innecesarias, abandono, tiempo total,
solicitud de ayuda y recuperación. Para el módulo de incentivos, introducir una
“atajo” que da más puntos pero produce peor resultado; el sistema debe rechazar
esa métrica como objetivo válido.

## Kill tests

- Si el sistema interrumpe a usuarios lentos que sí progresan, falla.
- Si sólo detecta quietud y no reconoce errores/retrocesos, falla.
- Si ofrece ayuda pero borra el progreso, falla.
- Si la velocidad mejora a costa de más errores irreversibles, falla.
- Si un operador gana más por actuar rápido que por detectar una condición
  incierta, el esquema de incentivos falla.
- Si la interfaz cambia el color o sonido y eso aumenta confianza sin aumentar
  corrección, la adaptación es persuasión, no asistencia.

## Decisión

La función que debemos construir no es un detector de presencia. Es un
**asistente de continuidad**: reconoce que la tarea dejó de avanzar, reduce la
carga en el punto concreto, conserva el trabajo, ofrece ayuda humana y registra
el resultado.

El siguiente prototipo debe implementar primero la secuencia de eventos y la
política de ayuda con datos sintéticos. La cámara y el eye tracking quedan como
señales opcionales posteriores. En sistemas críticos, “dudar bien” debe ser una
salida válida y medible; “equivocarse rápido” nunca debe ser el comportamiento
óptimo por diseño.

