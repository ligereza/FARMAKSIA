# VIZZ 033 — calibración visible y contenido normal modificado en background

Este incremento convierte el contrato 032 en una ruta Python ejecutable en
Windows:

```text
GPU sessions -> camera -> CALIBRATION_UI -> local profile -> headless camera
                                                        │
                                                        └─ click-through focus layer
```

El único momento con interfaz es `--calibrate`. Se muestra una pantalla
completa con 12 puntos; no hay vista previa de cámara. Al sellar el perfil se
cierra Tk y el proceso pasa al runtime de fondo. El runtime no importa Tkinter,
no crea paneles ni botones y no dibuja un marcador VIZZ: modifica el contenido
normal con una capa nativa transparente, click-through, que atenúa suavemente
lo que queda fuera de la zona de mirada.

## Instalación y ejecución

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r experiments/033-vizz-python-headless-runtime/requirements.txt
.\.venv\Scripts\python.exe experiments/033-vizz-python-headless-runtime/download_models.py
.\.venv\Scripts\python.exe experiments/033-vizz-python-headless-runtime/run_vizz.py --calibrate
```

La calibración se almacena en `.vizz-calibration.json` y no contiene vídeo.
Para iniciar después sin mostrar la calibración:

```powershell
.\.venv\Scripts\pythonw.exe experiments/033-vizz-python-headless-runtime/run_vizz.py
```

Para detener el proceso headless se usa `Ctrl+C` si se inició con `python`, o
se cierra su proceso si se inició con `pythonw`. Los fallos se registran en
`.vizz-runtime.log`; no se abre una interfaz de error VIZZ.

## Evidencia y límites

- ONNX Runtime 1.29.0 se configura con `CUDAExecutionProvider` y
  `session.disable_cpu_ep_fallback=1`; si la sesión CUDA no se crea, no se
  abre la cámara ni se crea el overlay.
- Los modelos se descargan fuera de git desde el release MIT de
  [screen-eye-tracking](https://github.com/PINTO0309/screen-eye-tracking), que
  documenta la composición RetinaFace + modelo gaze ONNX + proyección de
  pantalla.
- Solo se persisten vectores de calibración, geometría y hash de modelo; nunca
  frames o vídeo crudo.
- La capa es una modificación visual experimental. No demuestra precisión,
  reducción de fatiga, seguridad médica ni inferencias sobre atención,
  intoxicación, ansiedad o neurotransmisores.
- La calidad cae si no se detectan dos ojos, si la discrepancia binocular supera
  45 grados o si el rostro no supera el umbral. En esos casos el overlay se
  oculta: no inventa una coordenada.
