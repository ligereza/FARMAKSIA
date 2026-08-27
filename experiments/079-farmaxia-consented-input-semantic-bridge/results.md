# Resultados — experimento 079

## Evidencia local

La prueba conecta el hook de actividad de teclado ya adoptado por VIZZ con
`pywinauto/UIA` para observar el contexto de la ventana activa. El resultado
local se expresa como conteos de eventos (`keyboard_activity`,
`focus_context_changed`, `pointer_motion`, `idle_observation`) y no contiene
teclas, texto, títulos ni píxeles.

En una ejecución local de 2 segundos a 5 Hz, con puntero habilitado, se
observaron 10 muestras y el contexto allowlisted `firefox:Group`. No hubo
actividad de teclado durante ese intervalo. Esto es evidencia de que el
observador real resolvió aplicación/clase UIA sin emitir contenido, no una
medición de intención ni de productividad.

## Relación con el kernel

La cadena ahora puede representarse así:

```text
input observado → contexto UIA → delta de estado nativo → transición tipada
```

El observer no transforma automáticamente `keyboard_activity` en `modify`.
Eso sería una inferencia no identificada. La clasificación semántica requiere
observar la postcondición en Excel o Blender.

## Límites

- Esta ejecución verifica el observador real, no la comprensión de intención.
- Un hook global cuenta actividad de teclado y debe usarse sólo con opt-in.
- El tipo UIA de la ventana no identifica por sí solo el documento, objeto o
  celda que recibió el input.
- La siguiente prueba debe correlacionar un evento con un delta nativo sin
  persistir contenido privado.
