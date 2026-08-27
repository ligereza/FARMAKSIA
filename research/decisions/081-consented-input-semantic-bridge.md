# Decisión 081 — input como motor, intención como hipótesis

## Decisión

El input humano se incorpora como una secuencia local de observaciones, no como
una orden autónoma ni como una etiqueta de intención. El primer vocabulario es:

```text
keyboard_activity
focus_context_changed
pointer_motion
idle_observation
```

Un evento sólo puede convertirse en `select`, `modify` o `commit` cuando un
adaptador nativo observa el delta de estado y su postcondición.

## Evidencia

El experimento 079 ejecutó un observer real durante 2 segundos a 5 Hz, resolvió
la aplicación allowlisted y el tipo UIA del foco (`firefox:Group`) y mantuvo
fuera de la salida las teclas, texto, títulos y píxeles. Sus kill tests rechazan
captura de contenido, inyección e inferencia de intención sin resultado.

## Arquitectura

```text
input observado → contexto allowlisted → delta nativo → transición tipada
```

VIZZ puede aportar contexto de atención en una etapa posterior, pero no debe
ser la fuente de verdad para la intención. CODE-INE puede registrar la
transición; X-ANA-X puede buscar una operación análoga cuando la precondición,
el tipo de cambio y la postcondición sean compatibles.

## Límite

Un hook global cuenta actividad, no significado. La siguiente prueba debe
trabajar con Excel o Blender abiertos por el usuario y correlacionar una acción
explícitamente elegida con un delta nativo, preservando el contenido privado.
