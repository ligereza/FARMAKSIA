# Experimento 009 — piloto VIZZ contrabalanceado

## Pregunta

¿Puede prepararse un instrumento humano que compare condiciones de
representación sin confundir el efecto de la condición con recordar el mismo
estímulo?

## Diseño

Hay tres conjuntos de ramas (`set-A`, `set-B`, `set-C`) con la misma estructura
de tarea y regla analítica, pero valores y evidencia distintos. Cada sesión
asigna cada conjunto a una condición distinta mediante tres rotaciones:

| Rotación | tabla | estática | VIZZ |
|---|---|---|---|
| 0 | A | B | C |
| 1 | B | C | A |
| 2 | C | A | B |

El orden de condiciones también rota por la semilla. Cada participante ve cada
condición y cada conjunto exactamente una vez. La asignación y el `set_id` se
exportan para que el análisis pueda separar condición, conjunto y orden.

## Invariantes

- cada conjunto conserva cuatro ramas y la misma regla declarada;
- las tres condiciones de un conjunto reciben exactamente sus mismos valores y
  evidencia;
- el navegador no recibe la respuesta analítica;
- no hay llamadas de red;
- la representación no elige por la persona.

## Kill tests

- Si una sesión repite un `set_id` o una condición, el verificador falla.
- Si una condición altera valores o evidencia dentro de un conjunto, falla la
  paridad.
- Si el piloto incluye la respuesta analítica o llamadas de red, falla la
  integridad.
- Si datos humanos posteriores no muestran mejora frente a la vista estática
  controlando conjunto y orden, VIZZ no sobrevive como operador independiente.

Este experimento prepara un instrumento; no contiene ni fabrica observaciones
humanas.

`aggregate_pilot.py` acepta varias exportaciones, exige códigos de participante
explícitos y únicos, comprueba el balance de asignación y emite solo métricas
descriptivas. Sin archivos exportados informa `NO_HUMAN_DATA`.
