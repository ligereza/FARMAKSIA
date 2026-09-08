# Resultados — Experimento 085

## Evidencia computacional

La escena se construyó y renderizó con Blender **4.5.4 LTS** en Cycles.
El control se verificó dentro de Blender mediante el objeto separado
`VIZZ_CONTROLLER`:

| Estado | Cámara Y | Distancia focal |
|---|---:|---:|
| referencia/pantalla | −0,60 m | 0,60 m |
| lejos/pantalla | −1,00 m | 1,00 m |
| referencia/cerca | −0,60 m | 0,38 m |

Se generaron tres renders de 1920×1080. El cambio de distancia modifica el
tamaño angular aparente del monitor; el cambio de `focus_offset_m` modifica el
plano de profundidad de campo sin cambiar la geometría.

El primer intento produjo tres imágenes casi iguales porque el timeline
restauraba los valores keyframe. El fallo se corrigió eliminando esos keyframes,
separando el controlador de la cámara y forzando la actualización del ID en
modo batch. El segundo intento pasó la comprobación numérica y mostró cambios
visuales en los tres renders.

## Lo que demuestra

- Cycles puede representar una cámara perspectiva con apertura y foco físico.
- La distancia del observador y el plano focal son variables separables.
- Una escena 3-D controlada es mejor punto de partida que una imagen ampliada
  con IA para estudiar el efecto visual.

## Lo que todavía no demuestra

- No demuestra que una pantalla real pueda producir profundidad binocular.
- No demuestra una mejora de agudeza, comodidad o fatiga ocular.
- No demuestra que el usuario prefiera un cambio de escala o desenfoque.
- El render ejecutado en esta máquina no confirmó uso de GPU; Cycles pudo usar
  CPU en modo batch.

## Próximo experimento útil

Usar el `.blend` como banco de pruebas y exportar una secuencia corta donde la
distancia cambie suavemente, manteniendo el foco en la pantalla. Después crear
una segunda secuencia con `focus_offset_m` variando de 0 a −0,22 m. Sólo cuando
ambas secuencias sean comprensibles se conectará la distancia relativa de VIZZ.

