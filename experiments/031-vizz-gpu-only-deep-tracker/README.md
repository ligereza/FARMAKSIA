# VIZZ 031 — deep tracker GPU-only

Primer vertical slice del diseño de seguimiento de VIZZ con dos comprobaciones de backend:

1. MediaPipe Tasks Vision `FaceLandmarker` con `delegate: "GPU"`.
2. Un encoder ONNX pequeño con `executionProviders: ["webgpu"]`.

No existe fallback CPU/WASM. Si el navegador no expone WebGPU, el adaptador no está disponible o cualquiera de los modelos GPU no inicializa, la aplicación se detiene antes de pedir `getUserMedia`. Se solicita la cámara únicamente después de que ambas rutas hayan inicializado.

## Qué prueba y qué no prueba

Al ejecutarlo desde un servidor local, la página captura 12 muestras de calibración en memoria y muestra un embedding del encoder. El modelo ONNX incluido es un smoke model determinista: prueba la conexión y la ejecución GPU, pero no tiene pesos entrenados con datos humanos y no es un predictor de gaze. El marcador amarillo es solo una vista de la señal geométrica de iris, no una predicción calibrada.

La inferencia ML está forzada a GPU. El navegador todavía puede usar CPU para cámara, DOM, decodificación y copias; `low-power` es una sugerencia al adaptador, no una garantía térmica. La temperatura debe medirse en un experimento posterior.

## Uso manual

Desde la raíz del repositorio:

```powershell
python -m http.server 8000
```

Abrir `http://localhost:8000/experiments/031-vizz-gpu-only-deep-tracker/` en un navegador con WebGPU habilitado. Chrome/Edge suelen ofrecer la ruta más directa; si el navegador devuelve `gpu_unavailable`, no se habilita un backend alternativo.

1. Marcar “Autorizo cámara local”.
2. Pulsar “Iniciar”.
3. Mirar cada punto y hacer clic cuando aparezca una señal facial válida.
4. “Detener” cierra la cámara y descarta las muestras.

## Fuente y licencias

- `@mediapipe/tasks-vision` 1.0.1, Apache-2.0, bundle local en `vendor/tasks-vision/`.
- `onnxruntime-web` 1.29.0, MIT, bundle local en `vendor/ort.webgpu.min.js`.
- Face Landmarker task oficial de Google AI Edge, URL y hash en `provenance.json`.

La política de ejecución y los límites están en `runtime_policy.json`. La auditoría estática se ejecuta con `python run_contract_test.py`.
