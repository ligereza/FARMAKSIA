# Decisión 043 — VIZZ exige inferencia GPU para el tracker profundo

Fecha: 2026-08-24

## Motivo

El objetivo operativo de VIZZ no es solo reducir latencia: también es evitar
mantener un pipeline de visión pesado sobre CPU durante una sesión. Una GPU no
garantiza por sí sola menor temperatura —la cámara, el navegador y la copia de
frames siguen consumiendo CPU y el dispositivo puede calentarse—, pero permite
que la inferencia principal no se ejecute silenciosamente en CPU.

## Decisión

El futuro tracker profundo de VIZZ será **GPU-only para inferencia de machine
learning**. No se añadirá `wasm`, `webgl` ni otro proveedor CPU como fallback
automático. Si el navegador no expone WebGPU, si el adapter no puede crearse o
si la sesión no puede ejecutarse con el proveedor GPU, el estado será
`gpu_unavailable` y no se solicitará ni procesará la cámara.

La CPU seguirá pudiendo ocuparse de trabajo no neuronal e inevitable: permisos,
decodificación de vídeo del navegador, eventos, DOM, temporizadores y lectura
de métricas. El contrato GPU se refiere a la inferencia del detector facial,
extractor ocular y modelo gaze.

## Arquitectura propuesta

1. **Entrada:** cámara local a resolución controlada y frecuencia limitada,
   usando `requestVideoFrameCallback`/frame skipping para no inferir a 60 FPS
   innecesariamente.
2. **Detector/landmarks:** MediaPipe Tasks Vision Face Landmarker con
   `delegate: "GPU"`, modelo `.task` local y blendshapes/transformación facial
   activados para calidad y pose. No usar la ruta legacy de WebGazer como prueba
   de que toda la inferencia está en GPU.
3. **Modelo gaze:** red pequeña exportada a ONNX y ejecutada con
   `onnxruntime-web/webgpu`, usando solo `executionProviders: ["webgpu"]`.
   La sesión debe fallar cerrada si no puede asignarse al proveedor GPU.
4. **Características:** crops de ojos y landmarks normalizados, con máscara
   de visibilidad por ojo y pose de cabeza. Se prefiere una CNN depthwise o un
   MobileNetV3-Small recortado antes que una red grande de imagen completa.
5. **Adaptación personal:** backbone congelado y una cabeza pequeña de
   regresión/clasificación ajustada con la calibración VIZZ-Cal v2. No se
   entrena una red completa en el navegador.
6. **Memoria GPU:** entradas y salidas deben permanecer en buffers GPU cuando
   la API lo permita; evitar convertir cada frame a grandes arrays JS y copiarlo
   de vuelta innecesariamente.

## Presupuesto inicial de ingeniería

Son objetivos de diseño, no resultados medidos todavía:

- modelo gaze de menos de 5 MB y menos de 2 millones de parámetros;
- inferencia gaze a 15–20 FPS, con detector facial compartido y frame skipping;
- resolución de crop ocular pequeña y fija;
- proveedor GPU explícito, perfil de tiempo por etapa y contador de frames
  rechazados;
- selección de `powerPreference: "low-power"` cuando el navegador lo respete,
  sin fingir que eso garantiza una temperatura determinada.

## Compuertas y kill tests

- `navigator.gpu` ausente: `gpu_unavailable`, sin permiso de cámara.
- Adapter o device no creado: `gpu_unavailable`, sin inferencia.
- Sesión ONNX no creada con `webgpu`: kill test.
- Cualquier fallback a WASM/CPU detectado en la sesión o en el perfil: kill
  test; no se muestra un marcador gaze.
- Modelo, WASM, task y runtime deben ser locales y tener versión, licencia y
  hash registrados; no CDN.
- Ojo cerrado, landmarks inválidos o rostro perdido: frame rechazado, no
  coordenada inventada.
- Temperatura, uso de CPU/GPU y consumo se medirán en una auditoría separada;
  este contrato no afirma una mejora térmica hasta medirla.

## Herramientas investigadas

- [ONNX Runtime Web](https://onnxruntime.ai/docs/tutorials/web/) ofrece WASM
  para CPU y WebGPU para GPU; VIZZ usará únicamente el segundo en este frente.
- [MediaPipe Face Landmarker web sample](https://github.com/google-ai-edge/mediapipe-samples-web/blob/main/src/workers/face-landmarker.worker.ts)
  muestra el uso de `delegate: "GPU"` y de un modelo local.
- [GazeCapture/iTracker](https://gazecapture.csail.mit.edu/) demuestra que un
  modelo convolucional puede ejecutarse en tiempo real en un dispositivo móvil,
  pero su dataset y licencia deben auditarse antes de incorporarlos al corpus.

No se instalaron modelos ni se inició una webcam en esta decisión.
