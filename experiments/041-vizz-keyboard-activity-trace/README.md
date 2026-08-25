# VIZZ 041 — actividad de teclado sin contenido

Este experimento añade una señal temporal opt-in para las sesiones naturalistas:
cuenta pulsaciones de teclado por intervalo de muestreo, pero no conserva el
código de tecla, caracteres, palabras, texto, ventana activa ni contenido de
pantalla.

La señal no es ground truth ocular. Sólo permite comparar intervalos de escritura
con gaze, mouse, pose y calidad del tracker. El hook es una integración nativa de
Windows y se inicia únicamente con `--keyboard-trace` junto con `--trace`.

```powershell
.\.venv\Scripts\python.exe experiments/041-vizz-keyboard-activity-trace/run_experiment.py
.\.venv\Scripts\python.exe experiments/041-vizz-keyboard-activity-trace/run_contract_test.py
```

Para la próxima sesión de trabajo:

```powershell
.\.venv\Scripts\python.exe experiments/033-vizz-python-headless-runtime/run_vizz.py --trace .\.vizz-trace-keyboard.jsonl --trace-hz 20 --keyboard-trace
```

No usar `--calibrate` si el perfil vigente ya está aprobado. Detén el runtime
con `Ctrl+C` al terminar.
