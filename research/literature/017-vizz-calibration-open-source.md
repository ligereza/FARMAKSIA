# Investigación 017 — calibración VIZZ y alternativas open source

Fecha: 2026-08-24

## Pregunta

¿Qué herramienta y protocolo pueden mejorar la estabilidad observada en VIZZ
sin convertir una webcam en un instrumento clínico ni abrir una ruta de
captura remota?

## Fuentes primarias revisadas

- [WebGazer.js](https://github.com/brownhci/WebGazer) y su
  [API de nivel superior](https://github.com/brownhci/WebGazer/wiki/Top-Level-API).
- [RealEye Webcam EyeTracker Light Open](https://github.com/RealEye-io/webcam-eyetracker-light-open).
- [EyeGestures](https://github.com/NativeSensors/EyeGestures).
- [OpenFace](https://github.com/TadasBaltrusaitis/OpenFace).
- [Pupil Core](https://github.com/pupil-labs/pupil).
- [MediaPipe Iris](https://mediapipe.readthedocs.io/en/latest/solutions/iris.html).
- Papoutsaki et al., [WebGazer: Scalable Webcam Eye Tracking Using User
  Interactions](https://jeffhuang.com/papers/WebGazer_IJCAI16.pdf).
- [Assessing two methods of webcam-based eye-tracking for child language
  research](https://www.cambridge.org/core/journals/journal-of-child-language/article/assessing-two-methods-of-webcam-based-eye-tracking-for-child-language-research/F28BD05F1D529D3ADE04F2E28A5EE4CB).

## Comparación operativa

| Opción | Ventaja para VIZZ | Límite o riesgo | Decisión |
|---|---|---|---|
| WebGazer 3.5.3 | Referencia histórica: navegador local, consentimiento, `recordScreenPosition()` y regresión | Muestras de clic sensibles al momento, pose y calidad de webcam; GPL-3.0-or-later y mantenimiento oficial terminado | Retirado; conservar solo como antecedente, no como baseline activo |
| RealEye Light Open | 17 puntos, landmarks, blendshapes, crops de ambos ojos, compensación de pose, diagnósticos y regresión ridge | AGPLv3 o licencia comercial; modelos/WASM se cargan desde CDN por defecto; la cifra de aproximadamente 120 CSS px es una afirmación del propio repositorio, no una validación independiente registrada aquí | Mejor referencia de arquitectura; no adoptar aún como dependencia |
| EyeGestures | Código abierto GPL, navegador/Python, eventos de fijación, parpadeo y calibración; útil para estados de calidad | La ruta web documentada usa dependencias CDN y el repositorio no aporta un benchmark publicado comparable | Extraer ideas de eventos y fallback, no incorporar todavía |
| OpenFace | Gaze, landmarks, pose y acción facial en un stack de escritorio | No es un runtime browser-first ni una solución directa de coordenadas CSS | Posible comparador offline, no runtime VIZZ |
| Pupil Core | Plataforma open source con hardware y software de referencia para medición ocular | Requiere headset, instalación nativa y otra superficie de integración | Referencia de validación si VIZZ necesita precisión real |

MediaPipe Iris entrega landmarks faciales y de iris en tiempo real, pero declara
explícitamente que no infiere por sí solo el lugar de la pantalla que mira la
persona. Por ello es un buen extractor de características y calidad, no un
reemplazo automático de la calibración gaze-to-screen.

## Evidencia sobre la calibración

El hallazgo de las dos sesiones VIZZ era compatible con el mecanismo de
WebGazer: cada clic asociaba la posición de pantalla con la muestra ocular
disponible en ese instante. Cambiar el orden cambia la fase de calentamiento,
la postura, el tiempo de fijación y las muestras realmente capturadas; no
prueba que exista un orden universalmente mejor.

La literatura revisada aporta tres consecuencias prácticas:

1. Más muestras y mayor frecuencia de webcam se asociaron con mejores scores
   de calibración en un estudio de WebGazer.
2. La distancia al objetivo disminuyó después de aproximadamente 200 ms de
   fijación y se estabilizó cerca de 500 ms en la tarea analizada; conviene
   descartar el inicio de una fijación y capturar una ventana, no un solo clic.
3. El error vertical puede ser mayor que el horizontal; una validación solo en
   el centro o solo por sensación de “marcador estable” es insuficiente.

## Conclusión

La próxima mejora no es simplemente cambiar el orden ni aumentar puntos sin
control. Es un protocolo de calibración con cobertura espacial, muestras
repetidas, control de calidad ocular y validación separada. El runtime debe
rechazar frames con rostro perdido u ojo cerrado, y congelar la adaptación si
la calidad cae; no debe inventar una coordenada estable a partir de una señal
ocluida.

No se generaron datos humanos ni se inició una webcam durante esta revisión.
