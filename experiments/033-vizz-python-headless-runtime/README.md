# VIZZ 033 — calibración visible y contenido normal modificado en background

Este incremento convierte el contrato 032 en una ruta Python ejecutable en
Windows:

```text
GPU sessions -> camera -> CALIBRATION_UI -> local profile -> headless camera
                                                        │
                                                        └─ click-through focus layer
```

El único momento con interfaz es `--calibrate`. Primero aparece una pantalla
completa con el botón `Iniciar calibración`; los 12 puntos no empiezan hasta
que el usuario hace clic. En una calibración nueva, el flujo recorre dos
condiciones, primero con lentes y luego sin lentes, y sella sus 24 puntos en un
único perfil. Si ya existe un perfil `0.3` de una sola condición, no es
necesario repetir esa sesión: se puede capturar sólo la condición faltante y
fusionar sus observaciones con un refit conjunto. Para cada
punto, el cursor solo arma la captura: se descarta el periodo de estabilización
y luego se recoge una ventana fija de muestras válidas. La ventana se acepta
únicamente si tiene suficientes muestras, pose disponible y baja dispersión
robusta; el mouse nunca se guarda como verdad de la mirada. El texto de estado desaparece durante
la captura para no contaminar la etiqueta visual. No hay vista previa de
cámara. Al sellar el perfil se cierra Tk y el proceso pasa al runtime de fondo.
El runtime no importa Tkinter,
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

El descargador también fija el peso ONNX MobileOne S0 de
[`yakhyo/gaze-estimation`](https://github.com/yakhyo/gaze-estimation) para el
runtime y el probe 034. Se ejecuta en CUDA como señal independiente de gaze;
no reemplaza el mapper calibrado binocularmente ni se convierte por sí solo en
coordenadas de pantalla.

La calibración se almacena en `.vizz-calibration.json` y no contiene vídeo.
Para iniciar después sin mostrar la calibración:

```powershell
.\.venv\Scripts\pythonw.exe experiments/033-vizz-python-headless-runtime/run_vizz.py
```

Para añadir la condición sin lentes a una calibración anterior hecha con
lentes, conservando ambas en un único perfil:

```powershell
.\.venv\Scripts\python.exe experiments/033-vizz-python-headless-runtime/run_vizz.py --calibrate --condition without_glasses --merge-existing .\.vizz-calibration.json --existing-condition with_glasses
```

La fusión no promedia coeficientes de dos modelos. Pone en común las
observaciones por punto, asigna explícitamente la condición del perfil legado y
vuelve a ajustar una sola transformación regularizada. Esto es auditable y
permite añadir futuras sesiones sin depender de un selector de perfil.

Para ejecutar la validación controlada de pose sin modificar el perfil:

```powershell
.\.venv\Scripts\python.exe experiments/033-vizz-python-headless-runtime/run_validation.py --profile .\.vizz-calibration.json --output .\.vizz-validation.json
```

La validación realiza tres repeticiones por punto y condición, registra seis
proxies geométricos de pose y guarda únicamente vectores/metadatos en
`.vizz-validation.json`. No inicia el overlay ni sobrescribe la calibración.

Para analizar una validación ya capturada sin volver a usar la cámara:

```powershell
.\.venv\Scripts\python.exe experiments/033-vizz-python-headless-runtime/analyze_validation.py --calibration .\.vizz-calibration.json --validation .\.vizz-validation-smoke.json --output .\.vizz-validation-analysis.json
```

El auditor usa grupos por target y selección interna de Ridge; nunca divide
frames consecutivos. `M0` se puede comparar entre calibración y validación.
`M1` (pose) y `M2` (pose + condición) solo se ejecutan dentro de la sesión de
validación como diagnóstico si la calibración no persistió pose. En ese caso,
su comparación entre sesiones queda explícitamente como
`UNKNOWN_NOT_IDENTIFIABLE`; el auditor no modifica el perfil.

Para detener el proceso headless se usa `Ctrl+C` si se inició con `python`, o
se cierra su proceso si se inició con `pythonw`. Los fallos se registran en
`.vizz-runtime.log`; no se abre una interfaz de error VIZZ.

## Evidencia y límites

- El perfil actual es `farmaxia:vizz-calibration-profile:0.4` y declara el
  protocolo `static-stable-window-v3-multicondition`. Exige las condiciones
  `with_glasses` y `without_glasses` en un único perfil; no hay que alternar
  perfiles durante el runtime.
- Las calibraciones nuevas persisten seis proxies de pose por punto y marcan
  `pose_complete=true` solo cuando los 24 puntos tienen pose válida. Un perfil
  legado fusionado puede quedar incompleto; el auditor lo detecta y no permite
  usarlo para afirmar una comparación pose-aware entre sesiones.
- Esta versión implementa la primera corrección de la arquitectura híbrida:
  puntos estáticos con ventanas temporales estables. La trayectoria móvil y la
  cabeza neuronal personalizada permanecen como fases posteriores; no se
  entrenan con los 24 promedios de esta calibración.
- Los valores iniciales de estabilización (300 ms), captura (900 ms), mínimo
  (12 muestras) y MAD máximo (0.08 por característica normalizada) son
  hiperparámetros de ingeniería. Deben validarse con sesiones independientes y
  no se presentan como constantes fisiológicas.

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
- Desde el incremento 036, cada muestra y cada resumen de ventana conserva,
  además, `eye_centric`, `eye_centric_distance_px`, `eye_centric_roll_rad` y su
  razón de `UNKNOWN`. Esos campos se guardan para comparar la nueva
  representación con las seis features legacy; el mapper productivo continúa
  leyendo sólo `sample.features` hasta que exista una validación held-out
  favorable.
- Desde el incremento 053, el proveedor CUDA también entrega, cuando la señal
  es válida, `binocular_ray_proxy`: dos orígenes y dos direcciones explícitas,
  una por ojo, en `camera_proxy_normalized_v1`. Los orígenes conservan la
  separación interocular en unidades relativas de imagen y las direcciones
  provienen de los ángulos individuales del tracker. Esto evita perder la
  binocularidad al promediar `binocular_gaze_deg`.
- Este campo no es todavía una medición métrica del mundo: no contiene
  intrínsecos calibrados, profundidad ocular ni una pose 3-D resuelta. Por eso
  el contrato marca `VALID_RELATIVE_PROXY` y el futuro mapper físico debe
  seguir devolviendo `UNKNOWN` si exige metros, orientación de monitor o
  compensación de cabeza. La traza opcional y las capturas de calibración lo
  conservan como metadato sin guardar vídeo.
