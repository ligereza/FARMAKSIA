# Decisión 002 — frontera provisional X-ANA-X / KETAMINE

Fecha: 2026-08-23

## Evidencia

Sobre el mismo SVG:

- la tabla geométrica conservó la consulta espacial mediante atributos
  explícitos;
- el grafo conservó la respuesta como relación derivada, pero perdió la
  capacidad de recalcular consultas geométricas generales;
- la estructura temporal diferenciada mantuvo la consulta espacial y habilitó
  `active_at(t)` con respuestas distintas;
- el control temporal constante añadió un campo, pero no habilitó ninguna
  distinción nueva.

## Decisión

La separación sobrevive provisionalmente:

- **KETAMINE candidato:** transformación de representación que preserva una
  consulta/capacidad declarada bajo invariantes explícitos.
- **X-ANA-X candidato:** transformación que modifica variables, observables,
  estados o el conjunto de preguntas posibles.

El criterio no es “más campos” frente a “menos campos”. Es la aparición de una
estructura semántica nueva que no estaba implícita en la representación
anterior.

## Riesgo abierto

La estructura temporal diferenciada fue inventada para el experimento; no fue
descubierta en el SVG. Por tanto demuestra una diferencia operacional posible,
pero no demuestra que un sistema pueda descubrir correctamente cuándo una nueva
dimensión está justificada.

## Próximo kill test

Usar eventos temporales reales, no intervalos asignados manualmente, y comparar:

1. conversión a una representación de eventos que conserva la misma consulta;
2. cambio de tarea desde intersección espacial hacia orden temporal;
3. una codificación temporal redundante.

Si las tres operaciones no pueden separarse por invariantes, consultas y
residuo, fusionar X-ANA-X con KETAMINE.
