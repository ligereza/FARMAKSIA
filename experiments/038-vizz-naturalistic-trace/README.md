# VIZZ 038 — traza naturalista de uso

Este incremento añade un registro opt-in para sesiones de trabajo. A una tasa
configurable guarda timestamps monotónicos, gaze estimado, features legacy,
eye-centric, pose, calidad y posición OS del mouse. No guarda vídeo, píxeles,
contenido de pantalla ni usa el mouse como ground truth.

## Ejecución

Con un perfil ya sellado:

```powershell
.\.venv\Scripts\python.exe experiments/033-vizz-python-headless-runtime/run_vizz.py `
  --trace .\.vizz-trace-work.jsonl `
  --trace-hz 20
```

El trace sólo se crea si se solicita explícitamente `--trace`. Se puede detener
con `Ctrl+C`; el archivo termina con un footer y queda ignorado por git. El
runtime continúa sin panel de análisis, para no cambiar la conducta observada.

La posición del mouse sirve como covariable temporal y señal de interacción. No
es etiqueta ocular: el cursor puede adelantarse o seguir a la mirada y puede
quedar quieto mientras la mirada cambia. El análisis posterior debe comparar
gaze/mouse con desfases, clics y contenido presentado, nunca convertir el
cursor en ground truth.

## Límites

La traza no conoce el contenido que estaba leyendo el usuario y no demuestra
atención, comprensión ni precisión clínica. Una sesión naturalista mide
robustez y deriva; una validación con targets conocidos sigue siendo necesaria
para medir error de pantalla.
