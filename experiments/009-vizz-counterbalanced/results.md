# Resultados 009 — piloto VIZZ contrabalanceado

Fecha: 2026-08-23

## Verificación del diseño

Se generó un piloto local con tres conjuntos de estímulos distintos y tres
rotaciones de asignación. `verify_pilot.py` produjo:

```text
BALANCED_PILOT_VALID
sets=3 signatures=3
```

La verificación confirmó:

- tres firmas distintas, con los mismos ids de ramas;
- ausencia de `correct_action` en el HTML entregado al navegador;
- ausencia de llamadas de red;
- un único script inline con sintaxis válida en Node;
- registro de `condition`, `set_id`, `order_index` y firma del conjunto;
- controles básicos de teclado, foco y semántica accesible.

El analizador sin archivo exportado produjo `NO_HUMAN_DATA`. No se fabricaron
respuestas.

El agregador multi-sesión también produce `NO_HUMAN_DATA` sin exportaciones y
queda configurado para exigir códigos explícitos, no duplicados, antes de
emitir métricas descriptivas.

## Decisión

La versión 0.2 reemplaza el diseño inválido para inferencia causal del
experimento 003 como candidato para futuras sesiones. Todavía no demuestra que
VIZZ mejore decisiones: solo elimina una confusión de exposición que habría
invalidado esa conclusión.

## Residuo

El balance entre participantes debe verificarse en una muestra real; una sola
sesión no estima el efecto de condición. También siguen pendientes lector de
pantalla, zoom, contraste medido, consentimiento/gestión de datos y cualquier
análisis estadístico que se haga sobre observaciones humanas.
