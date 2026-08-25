# ADR-055 — VIZZ como interfaz adaptativa al campo visual

## Estado

Aceptada como dirección de investigación y arquitectura de prueba. No es una
afirmación clínica ni autoriza todavía una transformación visual permanente.

## Contexto

La investigación de VIZZ pasó por calibraciones de webcam, modelos de pose,
geometría de pantalla, experimentos ópticos y búsqueda de modelos preentrenados.
El patrón común de los proyectos externos es que ningún componente resuelve
por sí solo la cadena completa:

```text
ojos/cabeza → gaze → geometría del monitor → tarea → transformación visual
```

Además, la evidencia científica apoya una periferia menos detallada pero no
una periferia ciega: el campo periférico conserva contexto, movimiento y
señales para decidir la siguiente mirada. Los displays contingentes a la
mirada son sensibles a latencia, error espacial y tipo de tarea.

## Decisión

VIZZ se define provisionalmente como una **interfaz 2D adaptativa al campo
visual, consciente de pose y contingente a la mirada**. Su función no será
mover el cursor ni afirmar que corrige la vista. Su función será explorar una
política reversible de asignación de presupuesto visual:

```text
detalle máximo cerca de la mirada confiable
estructura y señales útiles en parafóvea/periferia
menos textura, densidad o movimiento sólo en contenido de baja prioridad
fallback estático si la señal no es confiable
```

La unidad de control será una región con incertidumbre y no un píxel. El
tracker deberá conservar pose, distancia/escala, timestamps, estado de
fijación, monitor candidato y motivo de `UNKNOWN`.

## Componentes que se adoptan como referencia

- MediaPipe Face Landmarker GPU o el frontend GPU existente: landmarks y
  señales oculares.
- OpenTrack: ideas de filtrado, recenter, deadzone y curvas de pose; no es
  fuente de ground truth de mirada.
- Pupil: contrato de eventos, timestamps, plugins y separación entre modelo de
  ojo y consumidores; no se incorpora hardware no disponible.
- OptiKey/WebGazer: patrones de interacción, calibración y fallback; no se
  copian sus supuestos de mouse ocular.
- OpenXR/VRS: referencia conceptual para niveles de calidad por región; no se
  adopta como dependencia de escritorio hasta probar el compositor real.

No se descarga un nuevo modelo ni se acepta un corpus externo en esta etapa.
La selección futura requiere repositorio, licencia, procedencia de pesos,
proveedor GPU, latencia y prueba fuera de dominio verificables.

## Contrato de runtime

```text
track(frame) -> {
  eye_centers,
  eye_landmarks,
  interocular_scale,
  head_pose,
  gaze_ray_or_region,
  monitor_hypotheses,
  confidence,
  covariance,
  fixation_state,
  timestamps,
  unknown_reason
}
```

```text
visual_policy(GazeState, TaskState, DisplayState) ->
  reversible_layer | STATIC_FALLBACK
```

La política debe rechazar o congelar cuando falte un ojo, la pose esté fuera
de dominio, la cámara o el layout de monitores cambie, la covarianza sea alta
o la latencia provoque artefactos. El proceso no debe caer silenciosamente a
CPU si el contrato exige GPU.

## Hipótesis preregistrables

1. Una política adaptativa reduce tiempo de búsqueda o regresiones respecto de
   una interfaz estática limpia, sin aumentar errores.
2. Usar pose y geometría reduce desplazamientos artificiales cuando la cabeza
   se traslada o rota manteniendo el objetivo visual.
3. Una política que preserva señales periféricas supera a un blur uniforme en
   alertas y orientación.
4. Las políticas específicas para lectura, escritura y monitorización superan
   una política universal.

## Secuencia de validación

1. **Geometría sin cambio visual:** validar rayos, planos, monitor activo,
   distancia angular e `UNKNOWN` con escenas sintéticas y layout documentado.
2. **Playback:** comparar estático completo, estático limpio, adaptativo
   protegido y adaptativo sin protección; medir latencia y artefactos.
3. **Overlay pasivo:** registrar gaze, teclado, mouse y ventana activa sin
   alterar contenido; usar mouse/teclado sólo como contexto.
4. **A/B por tarea:** lectura, código, navegación y monitorización, agrupando
   por sesión/tarea y no por frames.

## Criterios de descarte

- Artefactos perceptibles, saltos, mareo o pérdida de legibilidad.
- Deterioro de búsqueda o detección de alertas periféricas.
- Mejora sólo en ajuste interno, no en sesiones o tareas no vistas.
- Dependencia de una coordenada fija después de mover cabeza, cámara, DPI o
  monitor.
- Degradación por tarea que no pueda resolverse con una política separada.
- Necesidad de exactitud ocular o médica que una webcam no pueda sostener.

## Desconocidos

No sabemos todavía qué tamaño de región será perceptualmente estable para este
usuario, qué latencia extremo a extremo permite la webcam concreta, si la
salida GPU es suficientemente estable durante trabajo real, ni si la política
adaptativa mejorará alguna tarea frente a un baseline estático bien diseñado.
Esas preguntas requieren un playback controlado y después una comparación A/B;
no otra calibración ciega.

## Fuentes

- [Revisión de visión periférica](https://www.annualreviews.org/content/journals/10.1146/annurev-vision-082114-035733)
- [Revisión de displays multirresolución contingentes a la mirada](https://journals.sagepub.com/doi/10.1518/hfes.45.2.307.27235)
- [Medición de latencia](https://pmc.ncbi.nlm.nih.gov/articles/PMC4077667/)
- [Proyecto Pupil](https://github.com/pupil-labs/pupil)
- [MediaPipe Face Landmarker GPU](https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/modules/face_landmark/README.md)
- [OpenTrack](https://github.com/opentrack/opentrack)
- [OptiKey](https://github.com/Optikey/Optikey/)
- [OpenXR eye gaze](https://registry.khronos.org/OpenXR/specs/1.0/man/html/XR_EXT_eye_gaze_interaction.html)
