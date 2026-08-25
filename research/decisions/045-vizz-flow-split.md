# ADR-045 — VIZZ: calibración visible, runtime headless y contenido normal

Estado: aceptado como frontera de implementación; el tracker y el modificador visual aún están en desarrollo.

## Decisión

VIZZ se divide en dos superficies con responsabilidades incompatibles:

```text
calibration_ui (temporal y visible)
        │ profile local sellado
        ▼
headless_runtime (sin ventana propia, CUDA-only)
        │ señal de gaze
        ▼
content_modifier (capa transparente sobre la aplicación normal)
```

La interfaz visible existe únicamente para autorizar cámara, mostrar los puntos
de calibración y sellar el perfil. Después de `PROFILE_SEALED`, VIZZ no muestra
panel, botones ni dashboard: el proceso de fondo transforma la presentación del
contenido normal mediante una capa click-through. Esta capa podrá modificar
foco, contraste o tinte, pero no reemplaza la interfaz de la aplicación que el
usuario está usando.

## Razones

- El fallo de WebGPU en Firefox/Edge se observó como `gpu_unavailable` y el
  diagnóstico del navegador mostró renderizado software/WARP, aunque la máquina
  sí tiene una RTX 4070. El navegador no es una compuerta suficiente para este
  objetivo.
- ONNX Runtime documenta la solicitud explícita de `CUDAExecutionProvider`,
  por lo que el runtime Python puede fallar cerrado sin degradar silenciosamente
  a CPU.
- El delegado GPU de MediaPipe Python no es una base soportada para Windows;
  por eso no se presenta el port de MediaPipe como solución GPU terminada.

## Contratos y kill tests

- No se inicia el runtime sin un perfil sellado.
- No se sella un perfil con menos de 12 muestras, sin características o sin hash
  de modelo.
- No se solicita la cámara hasta que la sesión CUDA se crea correctamente.
- El perfil persiste geometría, vectores y hash, nunca vídeo crudo.
- `stop` elimina el estado volátil del flujo.
- Si falta `CUDAExecutionProvider`, el código devuelve `cuda_unavailable` y no
  crea la capa de contenido.

## Lo que aún no se afirma

Este ADR no afirma precisión ocular, reducción térmica, efecto clínico,
detección de intoxicación ni inferencia de atención, ansiedad o
neurotransmisores. El siguiente incremento debe instalar el entorno aislado,
probar el proveedor CUDA con un modelo ONNX verificable y luego implementar el
modificador click-through con su propio kill test de visibilidad.
