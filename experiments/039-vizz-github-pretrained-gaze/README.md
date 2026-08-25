# VIZZ 039 — puente a modelo preentrenado de GitHub

Este incremento integra como señal GPU independiente el modelo ONNX
`mobileone_s0_gaze.onnx` de
[`yakhyo/gaze-estimation`](https://github.com/yakhyo/gaze-estimation). El peso
se descarga desde su release de GitHub y queda fuera de git, con SHA-256 fijado
en `experiments/033-vizz-python-headless-runtime/download_models.py`.

La señal devuelve yaw/pitch en grados y se registra en la traza. No reemplaza
la calibración VIZZ ni se transforma silenciosamente en coordenadas de
pantalla: el mapper actual sigue usando el perfil calibrado binocularmente.
Esto evita usar un modelo nuevo como si ya estuviera calibrado para este
monitor.

## Verificaciones

```powershell
.\.venv\Scripts\python.exe experiments/039-vizz-github-pretrained-gaze/run_experiment.py
.\.venv\Scripts\python.exe experiments/039-vizz-github-pretrained-gaze/run_contract_test.py
```

El smoke test CUDA del modelo completo está en el experimento 034 y no abre la
cámara ni guarda frames.
