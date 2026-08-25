# VIZZ 040 — auditoría de traza naturalista

Este experimento añade dos límites operativos:

1. El runtime ejecuta un tensor cero del modelo MobileOne S0 durante el
   arranque. Si CUDA no puede ejecutar realmente el modelo, el proceso falla
   antes de abrir la cámara.
2. La traza conserva el gaze binocular, el gaze preentrenado y su diferencia
   angular bruta. Esa diferencia solo audita concordancia entre modelos; no es
   error de pantalla ni se usa como verdad ocular.

El auditor verifica timestamps, mouse, flags de privacidad, conteo de muestras
y ausencia de coordenadas de pantalla derivadas del segundo modelo.

```powershell
.\.venv\Scripts\python.exe experiments/040-vizz-naturalistic-trace-audit/run_experiment.py
.\.venv\Scripts\python.exe experiments/040-vizz-naturalistic-trace-audit/run_contract_test.py
```
