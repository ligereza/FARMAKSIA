# ADR-050 — selección de modelos preentrenados para VIZZ

## Estado

Aceptada como plan de investigación y evaluación. Ningún modelo externo se
incorpora todavía al runtime de producción ni sustituye el perfil actual.

## Contexto

La representación vigente mezcla seis proxies 2D/geométricos con un mapper de
pantalla. El diagnóstico más reciente produjo aproximadamente 668 px de error
mediano y 1.015 px en P95 sobre validación independiente. Además, el perfil de
calibración histórico no conserva pose suficiente para una comparación
multisesión completa. Por tanto, pedir otra calibración antes de mejorar la
representación sería prematuro.

La hipótesis de trabajo es que VIZZ debe separar cuatro capas:

```text
frame
  ├─ ojos izquierdo/derecho e iris
  ├─ normalización eye-centric y escala interocular
  ├─ pose facial independiente
  ├─ vector de mirada en coordenadas de cámara
  └─ rayo/plano de monitor + calibración personal -> pantalla o UNKNOWN
```

Un modelo preentrenado de gaze no conoce por sí solo la geometría de la cámara,
la distancia al monitor ni el escritorio virtual. Tampoco se acepta como
evidencia de precisión en pantalla el MAE publicado sobre otro dataset.

## Decisión

Evaluar los candidatos en este orden:

1. `pytorch_mpiigaze_demo` con MPIIGaze/ETH-XGaze como primer baseline de
   mirada en GPU. Tiene pesos preentrenados, normalización de imagen y pose de
   cabeza, y permite comparar directamente un vector de mirada antes del
   mapper personal.
2. `MobileGaze` como baseline de despliegue ONNX/CUDA con backbone pequeño.
   Se medirá latencia, memoria y estabilidad además del error; no se asumirá
   que el nombre mobile garantiza menor temperatura en la configuración local.
3. Un frontend de landmarks/iris y distancia interocular. MediaPipe Iris se
   usará primero como referencia de extracción, no como estimador de gaze,
   porque sus propios documentos aclaran que no determina hacia dónde mira la
   persona.
4. Un estimador independiente de pose facial, inicialmente 6DRepNet o
   landmarks + PnP/ONNX. Su salida será una covariable de normalización y una
   señal de calidad, no la etiqueta de gaze.
5. UniGaze queda como línea de investigación posterior: puede aportar
   representación cross-domain, pero su coste y licencia
   `ModelGo Attribution-NonCommercial-ResponsibleAI` requieren una revisión
   separada antes de cualquier uso del producto.

Pupil/pye3d y EyeTheia se conservan como referencias de arquitectura y
protocolo. No se copian al runtime sin revisar sus licencias y su dependencia
de hardware o de un flujo distinto al de VIZZ. El modelo pequeño de OpenVINO
se conserva como sanity check científico de vector 3D, no como decisión de
backend CUDA.

## Contrato de integración

El adaptador de cualquier candidato deberá exponer una salida común:

```text
track(frame) ->
  left_eye,
  right_eye,
  eye_landmarks,
  interocular_distance,
  head_rotation,
  gaze_vector_camera,
  confidence,
  unknown_reason
```

El adaptador no devolverá coordenadas de pantalla directamente. Esa conversión
requiere intrínsecos/extrínsecos, pose del monitor, distancia y calibración
personal. Si falta un ojo, la escala interocular está fuera de rango, la pose
sale del dominio, la confianza es insuficiente o CUDA no está activa, el estado
es `UNKNOWN`; no se degrada silenciosamente a CPU ni se inventa una posición.

## Experimento siguiente

Se implementará primero un probe sin datos humanos nuevos:

1. detectar disponibilidad real de CUDA y dependencias en Windows;
2. ejecutar cada modelo sobre frames sintéticos o de prueba permitidos,
   midiendo forma de entrada, salida, latencia, memoria y proveedor ONNX;
3. comprobar invariancia aproximada frente a escala, traslación y pequeña
   rotación del recorte facial;
4. comparar el vector de mirada y la pose antes de tocar el mapper de pantalla;
5. sólo si el probe es reproducible, hacer una sesión corta con los mismos
   targets, manteniendo los frames agrupados por sesión/target y sin guardar
   vídeo crudo.

La primera comparación será `M0` (mapper actual), `M1` (vector de mirada más
pose/distancia) y un baseline afín/ridge. La validación se hará por sesiones y
targets completos, nunca con un split aleatorio de frames.

## Kill tests

- Si el modelo sólo funciona con un ojo, o su error cambia de forma no
  explicada al variar escala/distancia, no se adopta como representación
  eye-centric.
- Si la salida cambia al mover la cabeza manteniendo la diana fija y no se
  corrige con `head_rotation`, queda como `UNKNOWN` fuera del rango probado.
- Si el proveedor CUDA no está activo, el probe falla cerrado y no continúa con
  CPU.
- Si el baseline preentrenado mejora sólo el ajuste interno pero no la sesión
  held-out, no se incorpora.
- Si la licencia, los pesos o el dataset no permiten el uso previsto, el código
  queda como referencia de investigación y no se integra.

## Desconocidos explícitos

Todavía no sabemos cuál candidato es compatible con la GPU y cámara concretas,
qué preprocesamiento exige cada peso, si la salida está en el sistema de
coordenadas esperado, ni qué precisión de pantalla alcanzará después de la
calibración personal. Esas preguntas requieren probes reproducibles y no se
resuelven con las métricas publicadas por los autores.

## Fuentes primarias

- [ptgaze / MPIIGaze / ETH-XGaze](https://github.com/hysts/pytorch_mpiigaze_demo)
- [ETH-XGaze oficial](https://github.com/xucong-zhang/ETH-XGaze)
- [MobileGaze](https://github.com/yakhyo/gaze-estimation)
- [MediaPipe Iris](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/iris.md)
- [6DRepNet](https://github.com/thohemp/6DRepNet)
- [OpenVINO gaze-estimation-adas-0002](https://docs.openvino.ai/2023.3/omz_models_model_gaze_estimation_adas_0002.html)
- [UniGaze](https://github.com/ut-vision/UniGaze)
- [Pupil Labs / pye3d](https://github.com/pupil-labs/pupil)
- [EyeTheia](https://github.com/patherstevenson/EyeTheia)
