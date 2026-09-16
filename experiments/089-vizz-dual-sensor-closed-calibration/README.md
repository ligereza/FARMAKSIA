# Experimento 089 — VIZZ: calibración dual cerrada

## Objetivo

Construir una calibración nueva en una sola sesión usando dos observadores del
mismo punto de pantalla:

- webcam del notebook, en luz visible;
- Hikvision DS-2CD1021G0-I, en posición oblicua y modo Night/IR.

Cada sensor obtiene su propio mapper. Después se comparan y se fusionan sus
estimaciones. La calibración anterior se carga sólo como línea base para medir
si la webcam cambió; no sustituye la nueva sesión.

## Corrección temporal importante

El punto aparece primero y la captura empieza inmediatamente. Tú miras el
punto y haces clic después de aproximadamente un segundo. El clic sólo cierra
la ventana anterior:

```text
ventana válida = [clic − 0.55 s − 0.18 s, clic − 0.18 s]
```

El periodo inicial de 0.45 s se descarta. Así no se analiza el recorrido del
ojo hacia el punto, el movimiento de la mano ni una mirada provocada por el
cursor durante el clic.

## Qué registra

Por cada sensor y punto se guarda únicamente un resumen robusto:

- seis features de VIZZ;
- calidad y MAD;
- posición y tamaño facial;
- separación ocular en píxeles;
- separación ocular normalizada por el ancho facial;
- área aproximada del recuadro facial (`face_bbox_area_px2`);
- orientación relativa de la línea ocular;
- señal angular del modelo de gaze independiente, cuando está habilitado;
- ray proxy binocular existente;
- para la Hikvision, diagnóstico óptico específico de pupila oscura y reflejo
  corneal brillante (`pupil_glint_vector_px`), junto con contraste, diámetro y
  confianza;
- timestamp, separación temporal entre sensores y posición del punto.

No se guarda vídeo, frame, texto escrito ni credenciales. El mouse sólo queda
como coordenada de confirmación y no como ground truth ocular.

## Ejecución sin cámara

Desde `C:\IA\FARMAXIA`:

```powershell
.\.venv\Scripts\python.exe experiments\089-vizz-dual-sensor-closed-calibration\run_dual_calibration.py --dry-run
.\.venv\Scripts\python.exe experiments\089-vizz-dual-sensor-closed-calibration\run_contract_test.py
```

El primer comando no abre ventana ni cámara. El segundo prueba la matemática,
la fusión con una o dos cámaras, la ventana pre-clic y la validación agrupada
por punto.

## Ejecución humana

Antes de iniciar:

1. Quitar los lentes.
2. Mantener la webcam y la Hikvision apuntando al rostro, aunque la Hikvision
   permanezca lateral/oblicua.
3. Mantener la Hikvision en `Night`, IR encendido y sin cambiar la posición
   durante el test.
4. Confirmar que la webcam no está siendo ocupada por otra aplicación.

El proceso es una sola ventana y una sola instancia de Python. Un muestreador
intercala las lecturas de webcam y RTSP y conserva su separación temporal. El
stream RTSP se entrega mediante la variable de
entorno `VIZZ_RTSP_URL`; no se escribe la URL ni la contraseña en el repo.
Si la lectura falla dos veces consecutivas, el lector libera y vuelve a abrir
el stream, registrando sólo los contadores de lectura y reconexión.

Ejemplo con una URL configurada sólo en la sesión actual de PowerShell:

```powershell
$env:VIZZ_RTSP_URL = 'rtsp://USUARIO:CONTRASENA@HOST:554/Streaming/Channels/101'
.\.venv\Scripts\python.exe experiments\089-vizz-dual-sensor-closed-calibration\run_dual_calibration.py --ir-state on --optical-state no_glasses
Remove-Item Env:VIZZ_RTSP_URL
```

El programa exige las dos fuentes; no cambia silenciosamente a una sola
cámara durante la captura. La salida se guarda en un JSON timestamped dentro
de `experiments/089-vizz-dual-sensor-closed-calibration/output/`.

## Matemática y alcance

El runtime carga por GPU tres modelos ONNX fijados en el manifiesto local:
RetinaFace para rostro/landmarks, el modelo de gaze de pantalla y MobileOne S0
de `yakhyo/gaze-estimation` como señal angular independiente. MobileOne no
alimenta todavía el mapper; sirve para comparar una segunda predicción y
detectar desacuerdo del modelo. Se puede desactivar con
`--disable-pretrained-gaze` si el presupuesto de GPU lo exige.

La rama IR no agrega otro modelo ni otra captura GPU. Reutiliza los centros
oculares ya detectados, convierte sólo el frame Hikvision a luminancia y
examina dos ROIs pequeñas: busca una región oscura compatible con la pupila y
un blob brillante pequeño compatible con un glint. Guarda únicamente números
resumidos. `PUPIL_GLINT` significa que ambos candidatos aparecieron; también se
conservan `PUPIL_ONLY`, `GLINT_ONLY` y `NO_FEATURES` para no convertir una
ausencia de señal en una falsa medición. Esta etapa es una medición óptica
diagnóstica, no profundidad, refracción ni gaze calibrado.

Como la iluminación activa puede generar pupila oscura o brillante, el detector
prueba ambas polaridades y registra `pupil_polarity`. Esto evita confundir una
respuesta óptica distinta con una caída de la cámara.

La decisión sigue el enfoque PCCR (vector pupila→reflejo corneal) usado en
seguimiento ocular basado en iluminación cercana al infrarrojo y la advertencia
de que una cámara visible/IR forma un problema cross-spectral: la apariencia
del mismo ojo cambia entre sensores. Referencias: [PCCR y seguimiento
infrarrojo](https://pmc.ncbi.nlm.nih.gov/articles/PMC3543256/) y
[correspondencias estéreo cross-spectral](https://openaccess.thecvf.com/content_cvpr_2018/papers/Zhi_Deep_Material-Aware_Cross-Spectral_CVPR_2018_paper.pdf).

La calibración usa el mismo vector de seis features y los mismos diez términos
regularizados del perfil VIZZ anterior, pero ajusta un mapper nuevo para cada
sensor. La validación es leave-one-target-out: ningún frame consecutivo se
trata como fold independiente.

Cada ventana también conserva un diagnóstico escalar de causa: cantidad de
frames leídos, features numéricas, muestras que pasan calidad y conteo por
motivo de rechazo. Para la Hikvision agrega además tasa de ojos con par
pupila-glint, diámetro pupilar mediano, vector pupila→glint, contraste y
confianza, incluyendo MAD del diámetro y del vector para detectar saltos
entre muestras. Así una caída de RTSP o de la señal óptica no queda reducida
solamente a `insufficient_sensor_samples`.

Al finalizar, cada punto también recibe `current_session_prediction`: una
predicción numérica en pantalla por sensor y su fusión. Está marcada como
diagnóstico in-sample porque se ajusta con todos los puntos de esta sesión; la
medida de generalización es `analysis.fused`, calculada dejando cada target
fuera.

La función de fusión devuelve siempre un par numérico. En los registros por
punto ese par es un diagnóstico del centro ocular normalizado en el espacio de
cada cámara; no es todavía una coordenada de pantalla:

```text
dos sensores válidos  → STEREO_DUAL_FUSION
uno válido             → WEBCAM_ONLY o HIKVISION_ONLY
ninguno en la ventana  → HOLD_LAST_ESTIMATE
```

Esto resuelve la salida nula del diagnóstico, pero `STEREO_DUAL_FUSION` todavía
significa consenso ponderado entre dos observaciones, no profundidad ni gaze
validado en pantalla. La triangulación métrica 3-D estricta
requiere además intrínsecos y extrínsecos medidos para ambas cámaras:

```text
p_webcam    ~ K_webcam [R_webcam | t_webcam] X
p_hikvision ~ K_hikvision [R_hikvision | t_hikvision] X
```

El test conserva los rayos y la separación ocular necesarios para añadir ese
solve sin volver a recolectar toda la calibración. La altura y el ángulo de la
Hikvision no se corrigen con un factor inventado: quedan absorbidos por su
mapper propio y, cuando exista el solve estéreo, por `R/t`.

## Kill tests y límites

- No se acepta una calibración nueva que haya empezado a muestrear después del
  clic.
- No se mezcla la posición del cursor con la etiqueta del punto.
- No se combinan silenciosamente dos sensores con timestamps demasiado
  separados.
- No se declara triangulación métrica sin `K`, `R` y `t`.
- Si la webcam y la Hikvision divergen, la salida numérica permanece disponible
  y la divergencia queda registrada para ponderación y auditoría.
- La rama IR entrega candidatos heurísticos de pupila/glint; todavía no es un
  pupil tracker validado, una medición oftalmológica ni una medición de
  profundidad.
- El vector IR no entra todavía al mapper. Sólo se aceptará como feature cuando
  mejore una validación held-out frente al baseline y no se explique por
  exposición, pose o posición de la cámara.
