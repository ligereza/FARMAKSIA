# Resultados VIZZ 031

## Evidencia reproducible de esta entrega

- El adaptador no abre la cámara: la compuerta `navigator.gpu.requestAdapter({powerPreference: "low-power"})` y las dos sesiones de modelo se ejecutan antes de `getUserMedia`.
- ONNX Runtime recibe exclusivamente `executionProviders: ["webgpu"]`.
- Face Landmarker recibe exclusivamente `delegate: "GPU"`.
- El contrato estático verifica consentimiento opt-in, recursos locales, CSP requerida, limpieza de tracks y ausencia de persistencia/red externa en `app.js`.
- La suite del laboratorio sigue siendo la fuente de validación de contratos y procedencia; no inicia dispositivos ni genera datos humanos.

## Desconocido

No se ha ejecutado una prueba manual de navegador en esta sesión porque el entorno de terminal no expone un navegador con WebGPU. Quedan sin medir: compatibilidad concreta del equipo del investigador, temperatura, FPS real, latencia, estabilidad del delegado GPU y precisión de gaze.

## Kill tests

- Sin `navigator.gpu`: detener con `gpu_unavailable` antes de pedir cámara.
- Sin adaptador: detener con `gpu_unavailable`.
- Fallo del modelo ONNX o Face Landmarker GPU: detener; no degradar a CPU/WASM.
- Rostro no detectable: no producir coordenadas de gaze ni inferencia humana.
- “Detener”: cerrar tracks, eliminar `srcObject` y descartar muestras de calibración.
