# Resultados VIZZ 033

## Evidencia obtenida

- El entorno aislado instala Python 3.13, OpenCV 5.0.0, ONNX Runtime GPU
  1.29.0 y las DLL CUDA/cuDNN correspondientes.
- Las sesiones RetinaFace y gaze reales del proyecto open source adoptado
  cargaron con `CUDAExecutionProvider`; la prueba de sesión registró
  `session.disable_cpu_ep_fallback=1` y ejecutó inferencia de forma sintética,
  sin cámara ni datos humanos.
- El flujo ejecutable tiene una única ventana de calibración y un modificador
  nativo click-through sin controles después del sellado.
- La ventana Win32 se probó en un smoke test de creación, actualización de
  bitmap de 1x1 y destrucción; la firma Win64 de `LPARAM` quedó corregida para
  `DefWindowProcW`.

## Desconocido

No se ha ejecutado todavía una sesión humana con cámara ni se ha medido
precisión, FPS, latencia, temperatura, estabilidad con lentes, asimetría entre
ojos o efecto perceptual. La primera sesión manual debe registrar solo métricas
de calidad y puede abortarse sin guardar el perfil.

## Kill tests

- Modelo ausente, CUDA ausente o DLL incompatible: terminar antes de abrir la
  cámara.
- Fallback CPU habilitado: rechazar la sesión.
- Menos de 12 puntos válidos: no sellar perfil.
- Error binocular mayor de 45 grados: ocultar capa y no producir coordenada.
- Perfil con `raw_video` distinto de `false`: rechazar.
- Runtime headless con toolkit visible: contrato inválido.
