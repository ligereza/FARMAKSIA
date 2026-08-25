# Investigación 018 — runtime Python GPU y modificación gaze-contingent

## Pregunta

¿Qué composición open source permite abandonar el navegador cuando el equipo
no expone WebGPU, conservar inferencia en la RTX y separar la calibración de la
modificación visual del contenido?

## Herramientas revisadas

- [ONNX Runtime CUDA Execution Provider](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html): permite crear sesiones Python con `CUDAExecutionProvider`; su configuración de sesión también puede desactivar la asignación/fallback de nodos a CPU.
- [screen-eye-tracking](https://github.com/PINTO0309/screen-eye-tracking): proyecto MIT de escritorio que combina RetinaFace, un modelo gaze ONNX, cámara OpenCV, calibración y proyección a pantalla. Se adopta su composición y sus modelos publicados, no su interfaz Electron ni su fallback CPU/TensorRT.
- [Open Model Zoo gaze-estimation](https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/intel/gaze-estimation-adas-0002/README.md): referencia de la tarea de estimar vector 3D desde ojos y pose; se conserva como comparador conceptual, no como backend del runtime CUDA.
- [MediaPipe Python GPU en Windows](https://github.com/google-ai-edge/mediapipe/issues/5126): issue que documenta el límite de usar el delegado GPU de MediaPipe Python en Windows; por eso no se fuerza esa ruta.

## Decisión de adopción

VIZZ 033 usa un detector de rostro con landmarks oculares y un modelo gaze
ONNX en sesiones ORT CUDA. Las señales de ambos ojos se convierten en un
vector pequeño y la calibración aprende un mapa local a coordenadas normalizadas
de pantalla. Tras sellar el mapa, `FocusOverlay` usa una ventana Win32
layered/click-through sin controles para dejar el contenido normal debajo y
atenuar lo que queda fuera del foco.

## Límites científicos e informáticos

Los modelos publicados tienen métricas propias de sus proyectos y no validan
este equipo, cámara, lentes, iluminación ni pantalla. Una calibración de webcam
no equivale a un eye tracker clínico. La asimetría observada al cerrar un ojo
se trata como señal de baja calidad y puede ocultar el overlay; no se interpreta
como neurotransmisor, ansiedad, intoxicación o atención. La primera ejecución
humana debe medir error frente a puntos conocidos, latencia, FPS, temperatura,
apagado y estabilidad, sin registrar vídeo crudo.
