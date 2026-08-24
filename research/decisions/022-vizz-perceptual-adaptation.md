# Decisión 022 — VIZZ gana una frontera de exposición perceptual

Fecha: 2026-08-24

## Evidencia

El experimento 013 usa una traza declarada de diez eventos y cuatro
representaciones:

- texto: conserva acción exacta y secuencia;
- timeline: conserva secuencia y señales de ganancia/error, pero comprime la
  acción;
- foco local: conserva cinco eventos y detalle local dentro de `38m ± 16m`,
  pero pierde contexto global;
- campo agregado: conserva cinco intervalos de actividad, ganancia y errores,
  pero no identidad ni orden de eventos.

El perfil de luminancia, el contraste y la ventana de foco modifican la
exposición visual del display, no la traza ni las métricas de consulta. No hay
participantes, eye tracking ni medida de confort.

## Decisión

VIZZ puede formularse provisionalmente como un contrato entre consulta,
representación y residuo perceptual:

`consulta → exposición visual → información disponible → decisión posible`

El foco no es una mejora gratuita: aumenta detalle local a cambio de contexto.
La agregación puede hacer visible una transición de estado sin permitir
reconstruir la acción que la produjo. Esto es una diferencia computacional
concreta, no todavía una ventaja humana.

## Kill test

La hipótesis de exposición adaptativa queda falsada si:

- un modo que declara pérdida responde consultas exactas que no debería poder
  responder;
- una condición de luminancia/contraste cambia los datos o la consulta;
- el foco local conserva la secuencia global fuera de su ventana;
- el campo agregado permite recuperar identidad y orden de acciones.

La verificación automática pasa en esta traza.

## Próximo paso

Añadir una sola tarea de decisión reproducible —detectar la entrada en
repetición después de la última mejora— y medir qué representaciones exponen
esa transición con menor información irrelevante. La fase humana y el eye
tracking quedan posteriores a esa prueba computacional.
