# Resultados VIZZ 034

Resultado local: `PROBE_VALID`.

- GPU: NVIDIA GeForce RTX 4070 Laptop GPU, driver 610.62, 8.188 MiB, 49 °C
  al inicio de la ejecución ampliada.
- ONNX Runtime: 1.29.0; CUDA y TensorRT disponibles.
- RetinaFace: 752 asignaciones de operadores perfiladas en
  `CUDAExecutionProvider`; latencia mediana sintética aproximada de 10.739 ms.
- Gaze binocular: 1.020 asignaciones de operadores perfiladas en
  `CUDAExecutionProvider`; latencia mediana sintética aproximada de 16.630 ms.
- MobileOne S0 de MobileGaze: peso ONNX de 4.974.521 bytes, entrada
  `1x3x448x448`, 360 asignaciones de operadores en CUDA, dos salidas
  `yaw/pitch` de 90 bins y latencia mediana sintética de 8.945 ms. El tensor
  negro produjo yaw 11.792° y pitch 7.164°; esto es sólo una comprobación de
  decodificación, no una medida de precisión.
- Las salidas fueron finitas y compatibles con las firmas esperadas.
- El runtime registró también `CPUExecutionProvider` en la lista de proveedores
  registrados, pero la sesión solicitó únicamente CUDA, configuró
  `session.disable_cpu_ep_fallback=1` y el perfil no observó operadores en CPU.

Este experimento no abre la cámara, no recoge datos humanos y no guarda frames.
Los resultados computacionales se escriben en `.vizz-pretrained-probe.json` y
no se versionan porque contienen información específica de la instalación
local, como latencia y memoria. Esto prueba la infraestructura de los
baselines, no su precisión de pantalla ni la invariancia ante movimiento de
cabeza. ETH-XGaze/ptgaze y los frontends de iris/pose siguen sin instalarse.
