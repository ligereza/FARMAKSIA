# Resultados — experimento 014

La traza sintética tiene diez eventos. El oráculo declara `e06` como última
mejora significativa (`gain=0.40`) y `e07–e10` como tramo posterior, con
ganancia total `0.14` y un error.

| Exposición | Consulta global | Señal proxy | Qué queda oculto |
|---|---:|---:|---|
| texto | sí | sí | nada dentro de la traza |
| timeline | sí | sí | acción exacta |
| foco 38m ± 16m | sí | sí | contexto anterior a la ventana |
| campo agregado | no | sí | identidad y orden |

La sensibilidad del foco es el resultado principal: con ventanas de 4 u 8
minutos la consulta global queda no disponible; con 16 minutos vuelve a estar
disponible porque incluye el ancla `e06` y todo el tramo posterior. El campo
puede señalar baja ganancia y errores, pero no demuestra que la señal ocurra
después de la última mejora.

Esto es una frontera de información, no una medición de percepción humana. No
se recogieron datos humanos, movimientos oculares, confort visual ni efectos
de luminancia, contraste, noche o corrección óptica.
