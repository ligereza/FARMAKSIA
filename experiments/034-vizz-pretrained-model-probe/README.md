# VIZZ 034 — probe local de modelos preentrenados

Este experimento comprueba la infraestructura local antes de cambiar la
representación de VIZZ. Usa solamente los modelos ONNX que ya están en
`.vizz-models`, genera tensores sintéticos y no abre la cámara, no muestra una
previsualización y no guarda frames.

## Ejecución

Desde `C:\IA\FARMAXIA`:

```powershell
.\.venv\Scripts\python.exe experiments/034-vizz-pretrained-model-probe/run_probe.py
```

El resultado se guarda en `.vizz-pretrained-probe.json`, ignorado por git. Se
puede cambiar la ruta con `--output`. El probe solicita exclusivamente
`CUDAExecutionProvider` y desactiva el fallback CPU. Si la sesión CUDA no se
activa o un modelo no puede ejecutar su tensor de prueba, termina como
`PROBE_BLOCKED`.

## Qué mide

- GPU, driver y memoria reportados por `nvidia-smi`;
- proveedores disponibles en ONNX Runtime;
- firma de entradas/salidas y hash de cada modelo instalado;
- inferencia sintética, finitud de las salidas y latencia aproximada;
- catálogo de candidatos investigados que aún no están instalados.

La salida de gaze todavía no es una coordenada de pantalla. El paso siguiente,
si este probe es reproducible, es adaptar un modelo eye-centric que entregue
vector de mirada, landmarks, escala interocular y pose; la conversión a
monitor requiere después una geometría cámara-monitor y una calibración
personal.

## Límites y kill tests

Un smoke test CUDA no demuestra precisión, estabilidad ante movimiento de
cabeza ni exactitud en pantalla. No se hace afirmación humana ni clínica. No se
descargan automáticamente pesos de terceros en este experimento. Los modelos
ptgaze/ETH-XGaze, MobileGaze, MediaPipe Iris, 6DRepNet y UniGaze quedan en el
catálogo hasta revisar dependencias, pesos, licencia y compatibilidad Windows.
