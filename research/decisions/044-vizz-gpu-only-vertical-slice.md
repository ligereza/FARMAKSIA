# Decisión 044 — VIZZ implementa el primer vertical slice GPU-only

Fecha: 2026-08-24

## Resultado

La decisión 043 deja de ser solamente arquitectura: el experimento
`031-vizz-gpu-only-deep-tracker` implementa una ruta local y aislada con:

- Face Landmarker de MediaPipe Tasks Vision con `delegate: "GPU"`.
- Encoder ONNX diminuto con `executionProviders: ["webgpu"]`.
- Adaptador `low-power` y compuerta `gpu_unavailable` antes de solicitar cámara.
- 12 puntos de calibración de pantalla completa, muestras solo en memoria y
  limpieza al detener.
- Assets locales versionados, licencias y hashes en `provenance.json`.

El modelo ONNX es un smoke model determinista construido con `MatMul`, `Add` y
`Relu`. No fue entrenado con datos humanos y no puede presentarse como
predictor de gaze. El marcador visible es una señal geométrica de iris para
diagnóstico; no es una coordenada calibrada.

## Evidencia

La auditoría `run_contract_test.py` pasa con `onnx_execution_provider=webgpu`,
`mediapipe_delegate=GPU` y `cpu_or_wasm_fallback=False`. La suite de FARMAXIA
termina en `SUITE_VALID`, incluida la procedencia 031. La comprobación HTTP
local confirmó que página, runtimes y modelos se sirven sin CDN.

No se ejecutó un navegador WebGPU desde el terminal, no se abrió una cámara y
no se produjeron datos humanos. Por ello todavía no hay evidencia de FPS,
temperatura, latencia, estabilidad entre calibraciones ni precisión.

## Objetivo siguiente

Construir un head de gaze pequeño entrenable por usuario sobre embeddings GPU,
con un protocolo de calibración VIZZ-Cal v2 y un conjunto de datos explícito,
consentido y local. El primer kill test será demostrar que el navegador no
acepta la sesión si el head o cualquier operador cae a CPU/WASM. No se
incorporarán GazeCapture u otro corpus hasta auditar licencia, procedencia,
sesgo y necesidad experimental.
