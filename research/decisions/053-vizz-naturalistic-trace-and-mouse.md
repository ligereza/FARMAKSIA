# ADR-053 — VIZZ: sesiones naturalistas y mouse como covariable

## Estado

Aceptada como protocolo experimental; la traza es opt-in y no modifica el
mapper productivo.

## Decisión

VIZZ usará dos tipos de evidencia:

1. sesiones con targets conocidos para medir error de pantalla, deriva y
   generalización agrupada;
2. sesiones naturalistas/caóticas para medir robustez ante distancia, pose,
   atención dividida, cambios de contenido y movimientos reales.

La posición del mouse se almacenará con timestamp monotónico como covariable de
interacción. Puede ayudar a estudiar desfase, anticipación, clics y relación
ojo-mano, pero no se usará para etiquetar gaze: la literatura describe patrones
en que los ojos preceden al cursor, lo siguen o alternan entre cursor y objeto.

La interfaz de análisis no se superpondrá durante la sesión naturalista por
defecto. Mostrar números, predicciones o errores puede cambiar la conducta que
se pretende medir. En su lugar, el runtime escribirá una traza resumida sin
vídeo ni contenido de pantalla y el análisis se mostrará después.

## Contrato de traza

Cada fila contiene, cuando están disponibles:

```text
t_monotonic
mouse_screen
gaze_screen
gaze_valid
legacy_features
eye_centric
eye_centric_distance_px
eye_centric_roll_rad
pose
quality
disagreement_deg
pretrained_gaze_deg
pretrained_gaze_valid
pretrained_gaze_unknown_reason
```

El encabezado declara `mouse_is_ground_truth=false`, `raw_video=false` y
`screen_content=false`. Una muestra sin gaze conserva la posición del mouse para
no confundir ausencia ocular con ausencia de interacción.

## Recomendación práctica

La prueba controlada de cabeza quieta sigue siendo necesaria como referencia
instrumental, pero no debe ser el único criterio. Después se deben recoger
varias sesiones naturalistas con el mismo perfil, guardar trazas separadas y
analizar por sesión completa. No mezclar las filas consecutivas como si fueran
observaciones independientes.

## Kill tests

- Si la traza contiene frames, píxeles o contenido de pantalla, se rechaza.
- Si el análisis convierte mouse en target ocular, se rechaza el resultado.
- Si la superposición cambia la conducta o el rendimiento, se desactiva durante
  la recolección y se conserva sólo el análisis posterior.
- Si una sesión naturalista no tiene timestamps alineables, queda como
  cobertura cualitativa y no como validación de precisión.
