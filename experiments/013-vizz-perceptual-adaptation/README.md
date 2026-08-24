# Experimento 013 — VIZZ: adaptación perceptual de una traza

Fecha: 2026-08-24

## Pregunta

¿Qué cambia en lo que puede observarse o decidirse cuando una misma sesión
informática se representa como texto, timeline, foco local o campo agregado?

## Experiencia original

Una sesión de desarrollo puede acumular actividad después de la última mejora
significativa. El prototipo separa actividad, ganancia, errores, detalle y
secuencia para no confundir “hay movimiento” con “el objetivo mejora”.

## Entrada

`trace.json` es una traza sintética, pequeña y declarada. No contiene datos
humanos ni una grabación de una sesión ajena. Tiene diez eventos ordenados,
incluyendo implementación, error, corrección, validación y mantenimiento.

## Representaciones

- `text`: conserva detalle y secuencia completa.
- `timeline`: conserva orden, fase, ganancia y errores, pero reduce detalle.
- `focus`: conserva detalle local alrededor de una ventana de foco configurable
  y pierde contexto global.
- `field`: agrega actividad por intervalos temporales y hace visible densidad,
  ganancia y errores, pero no permite reconstruir acciones individuales.

La interfaz `vizz.html` permite cambiar representación, ventana de foco y
perfil de luminancia. El perfil nocturno es una condición de display, no una
afirmación de seguridad ni una medición de melatonina.

## Medición computacional

El runner calcula cobertura de eventos, fidelidad de secuencia, disponibilidad
de detalle, señales de estado y consultas posibles. Esto mide qué información
queda expuesta por cada representación; no demuestra que una persona la
comprenda mejor.

## Kill tests

1. Si `field` permite reconstruir la acción exacta, la pérdida declarada es
   falsa.
2. Si `focus` conserva la secuencia global aunque solo muestre una ventana,
   la pérdida de contexto es falsa.
3. Si `timeline` conserva el texto completo de cada acción, no está realizando
   la compresión declarada.
4. Si el cambio de luminancia modifica los datos o la consulta, la adaptación
   visual contaminó la representación computacional.

## Límite

El experimento demuestra diferencias de exposición y de consulta en una traza
controlada. No demuestra confort visual, reducción de fatiga ni mejor decisión
humana. Eso requiere una fase posterior con protocolo perceptual y, si procede,
medición ocular consentida.
