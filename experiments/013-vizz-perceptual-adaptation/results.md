# Resultados 013 — VIZZ: adaptación perceptual de una traza

Fecha: 2026-08-24

El runner compara cuatro exposiciones de los mismos diez eventos. La métrica
es disponibilidad computacional de consulta, no rendimiento humano.

| Representación | Cobertura de eventos | Acción exacta | Secuencia global | Señal de estado | Pérdida principal |
|---|---:|---|---|---|---|
| Texto | 10/10 | sí | sí | sí | densidad y carga de detalle |
| Timeline | 10/10 | no | sí | sí | texto exacto de la acción |
| Foco local | 5/10 con ventana 38m ± 16m | sí, local | no | sí, local | contexto global |
| Campo agregado | 5 intervalos agregados | no | no | sí, agregado | identidad y orden de acciones |

## Decisión

VIZZ puede describirse de forma concreta como una elección de representación
según la consulta: detalle completo, secuencia, estado agregado o contexto
local. La transformación de foco no es gratis: reduce contexto mientras
preserva detalle local. El campo hace visible densidad y ganancia, pero no
permite reconstruir qué acción produjo el valor.

## Qué se gana

- Una misma traza puede exponer señales distintas sin modificar los datos.
- La ventana local concentra detalle alrededor de un foco declarado.
- La agregación expone actividad, ganancia y errores como estado temporal.
- Luminancia y contraste se pueden variar como condiciones de display sin
  contaminar la traza.

## Qué se pierde

- El texto conserva demasiado detalle para una lectura rápida.
- El timeline elimina la acción exacta.
- El foco elimina contexto fuera de la ventana.
- El campo elimina identidad y secuencia de eventos.

## Kill test

El prototipo falla si una representación lossy responde una consulta que su
contrato declara perdida, o si el perfil de luminancia/contraste cambia la
traza o sus métricas. La verificación automática pasa ambas condiciones.

## Límite

No hay participantes, eye tracking, pupillometría ni medida de confort. El
resultado demuestra un contrato de exposición y residuo, no que una persona
prefiera o comprenda mejor una condición.
