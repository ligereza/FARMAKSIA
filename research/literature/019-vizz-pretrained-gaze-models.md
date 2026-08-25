# VIZZ — modelos preentrenados y frontends geométricos

Fecha de corte: 2026-08-24.

## Pregunta

La validación local de VIZZ completó la captura, pero el perfil actual obtuvo
aproximadamente 668 px de mediana y 1015 px en P95. La búsqueda se enfocó en
proyectos abiertos que separen ojos, pose, escala/distancia y dirección de
mirada, con ejecución GPU o una ruta razonable hacia ONNX.

## Candidatos principales

### ptgaze: MPIIGaze, MPIIFaceGaze y ETH-XGaze

El repositorio `hysts/pytorch_mpiigaze_demo` ofrece pesos preentrenados para
MPIIGaze, MPIIFaceGaze y ETH-XGaze, dispositivo `cuda`, landmarks, pose de
cabeza y visualización de las imágenes normalizadas que recibe el modelo. Su
documentación explicita que la normalización depende de la cámara y que el
pitch/yaw de la pose normalizada forman parte del input. Es el candidato que
mejor coincide con la hipótesis revisada de VIZZ.

Limitaciones: declara pruebas en Ubuntu; Windows/GPU debe ser un probe separado.
La salida es dirección de mirada, no coordenada de pantalla.

Fuentes: [repositorio y CLI](https://github.com/hysts/pytorch_mpiigaze_demo),
[notas de normalización](https://github.com/hysts/pytorch_mpiigaze_demo#notes-on-data-normalization).

### MobileGaze

`yakhyo/gaze-estimation` ofrece ResNet, MobileNetV2 y MobileOne con pesos
preentrenados, inferencia ONNX Runtime y exportación ONNX. Es el candidato más
atractivo para una ruta GPU ligera y comparar coste térmico sin cambiar el
contrato de inferencia.

Antes de usarlo hay que auditar la normalización y orientación de ángulos de
cada peso. El repositorio declara MIT, pero los pesos y datasets mantienen sus
propias condiciones de procedencia.

Fuente: [repositorio MobileGaze](https://github.com/yakhyo/gaze-estimation).

### UniGaze

UniGaze usa preentrenamiento a gran escala y publica modelos `B/L/H`, inferencia
CUDA, entrada normalizada 224x224 y salida pitch/yaw. Su objetivo explícito es
mejorar la generalización entre dominios, relevante para el salto observado en
VIZZ.

No es la primera opción de producción: los pesos usan la licencia
`ModelGo Attribution-NonCommercial-ResponsibleAI`, los modelos pueden ser
costosos y no existe aún una ruta ONNX/CUDA integrada en FARMAKSIA. Queda como
comparación de investigación.

Fuentes: [proyecto](https://ut-vision.github.io/UniGaze),
[implementación](https://github.com/ut-vision/UniGaze),
[carga CUDA y licencia](https://pypi.org/project/unigaze/).

### OpenVINO `gaze-estimation-adas-0002`

Es un baseline pequeño y conceptualmente limpio: recibe recortes de ambos ojos
y yaw/pitch/roll de la cabeza, y devuelve un vector 3D de mirada. La ficha
oficial reporta 1.882 M de parámetros, 0.139 GFLOPs y MAE angular interno de
6.95 grados. Ese valor no es una garantía para VIZZ: usa un conjunto interno de
60 personas y no mide coordenadas de pantalla.

Sirve como referencia de arquitectura, pero no se adopta directamente en el
runtime CUDA actual porque su ruta oficial es OpenVINO y su backend GPU no
equivale automáticamente a CUDA/NVIDIA.

Fuente: [modelo oficial](https://docs.openvino.ai/2023.3/omz_models_model_gaze_estimation_adas_0002.html).

### MediaPipe Iris / Face Landmarker

MediaPipe Iris aporta landmarks de párpados, iris y contorno ocular, además de
una estimación de distancia cámara-persona basada en el diámetro aproximado del
iris. La documentación también aclara que Iris no infiere el lugar de la
pantalla al que mira la persona. Es un frontend geométrico, no un reemplazo del
modelo de gaze. Tiene grafos GPU nativos; la disponibilidad exacta en
Python/Windows debe probarse.

Fuente: [documentación oficial](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/iris.md).

### Pose facial independiente

`6DRepNet` ofrece una representación continua de rotación, licencia MIT y
modelos PyTorch. `yinguobing/head-pose-estimation` usa ONNX Runtime, 68
landmarks y PnP con un modelo 3D facial. Esta segunda ruta es especialmente
interesante para VIZZ porque separa pose de la regresión ocular y se acerca al
backend CUDA/ONNX existente.

Fuentes: [6DRepNet](https://github.com/thohemp/6DRepNet),
[pose ONNX + PnP](https://github.com/yinguobing/head-pose-estimation).

## Referencias de sistema completo

- [EyeTheia](https://github.com/patherstevenson/EyeTheia) implementa calibración
  personalizada, iTracker, backend Python y exportación ONNX. Es una referencia
  de protocolo, pero GPL-3.0 impide copiar código sin revisión legal.
- [Pupil](https://github.com/pupil-labs/pupil) y [pye3d](https://docs.pupil-labs.com/core/developer/pye3d/)
  aportan un modelo matemático 3D de ojo, pero están orientados al ecosistema
  de cámaras oculares Pupil Core, no a sustituir la webcam frontal de VIZZ.
- [screen-eye-tracking](https://github.com/PINTO0309/screen-eye-tracking), ya
  adoptado en FARMAKSIA, aporta ONNX Runtime, CUDA/TensorRT y proyección
  binocular de pantalla. Se conserva como baseline de integración, no como
  evidencia de que el mapper actual sea suficiente.

## Selección provisional

```text
frame
  ├─ ambos ojos + iris
  ├─ normalización eye-centric + escala interocular + distancia
  ├─ pose facial independiente
  ├─ vector de mirada preentrenado
  └─ ray/plane + calibración personal -> pantalla o UNKNOWN
```

Orden de evaluación:

1. `ptgaze` con ETH-XGaze como baseline científico de normalización y pose.
2. `MobileGaze` como baseline ligero exportable a ONNX/CUDA.
3. MediaPipe Iris/Face Landmarker o frontend ONNX equivalente para distancia y
   escala.
4. `6DRepNet` o landmarks+PnP para pose independiente.
5. UniGaze solo como comparación de generalización y después de revisar la
   licencia de pesos.

## Kill tests

- Cambiar distancia altera la mirada normalizada más allá de la incertidumbre:
  falla el frontend de escala.
- Un giro leve se interpreta como cambio ocular aun con pose explícita: falla
  la separación ojo/cabeza.
- La salida depende del mapper antiguo y no del vector de mirada: falla la
  independencia geométrica.
- El proveedor GPU no está activo: el modelo no entra en runtime; no se permite
  fallback CPU silencioso.
- Licencia incompatible: el proyecto queda como referencia, no dependencia.
