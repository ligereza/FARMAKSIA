# Decisión 031 — el contrato compartido puede expresar la transición CODE-INE

Fecha: 2026-08-24

## Evidencia

El experimento 022 pasó una secuencia VIZZ sintética de ocho eventos por el
adaptador manual en dry-run. CODE-INE recuperó `c04` como última mejora y
`c07` como entrada en repetición. El dry-run no escribió archivos; el puente
rechazó la eliminación de `action_class` y el adaptador bloqueó la ausencia de
consentimiento.

## Decisión

La interoperabilidad VIZZ → CODE-INE queda demostrada como propiedad del
contrato de eventos, no como evidencia de un estado humano. No se duplicará la
captura y no se habilitarán sensores para obtener esta transición.

La secuencia sigue siendo sintética: no sabemos si una persona puede emitir
esas clases sin interrumpir su tarea ni si la etiqueta “repetición” corresponde
a su experiencia.

## Próximo objetivo

Mantener el adaptador en preparación y, si el usuario inicia deliberadamente
una sesión, validar primero una secuencia corta con consentimiento explícito.
Hasta entonces, continuar con auditorías y controles sintéticos sin crear datos
humanos.
