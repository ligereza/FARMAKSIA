# Resultados VIZZ 034

Resultado local: `PROBE_VALID`.

- GPU: NVIDIA GeForce RTX 4070 Laptop GPU, driver 610.62, 8.188 MiB, 49 °C
  al inicio del probe.
- ONNX Runtime: 1.29.0; CUDA y TensorRT disponibles.
- RetinaFace: 752 asignaciones de operadores perfiladas en
  `CUDAExecutionProvider`; latencia mediana sintética aproximada de 6.644 ms.
- Gaze binocular: 1.020 asignaciones de operadores perfiladas en
  `CUDAExecutionProvider`; latencia mediana sintética aproximada de 9.279 ms.
- Las salidas fueron finitas y compatibles con las firmas esperadas.
- El runtime registró también `CPUExecutionProvider` en la lista de proveedores
  registrados, pero la sesión solicitó únicamente CUDA, configuró
  `session.disable_cpu_ep_fallback=1` y el perfil no observó operadores en CPU.

Este experimento no abre la cámara, no recoge datos humanos y no guarda frames.
Los resultados computacionales se escriben en `.vizz-pretrained-probe.json` y
no se versionan porque contienen información específica de la instalación
local, como latencia y memoria. Esto prueba la infraestructura del baseline
actual, no su precisión de pantalla ni la invariancia ante movimiento de
cabeza. Los candidatos externos siguen sin instalarse.
