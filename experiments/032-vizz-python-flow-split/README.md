# VIZZ 032 — flujo Python dividido

Este experimento cambia la frontera de VIZZ: la interfaz visible existe solo
durante la calibración. Después de sellar el perfil, la ventana se cierra y el
runtime Python opera como proceso de fondo; su salida es una modificación del
contenido normal mediante un modificador transparente, no una interfaz VIZZ.

## Flujo

```text
CALIBRATION_UI -> PROFILE_SEALED -> HEADLESS_RUNTIME -> CONTENT_MODIFIER
       |                |                  |                  |
   puntos y        perfil local       CUDA-only         overlay/efecto
   consentimiento  sin vídeo crudo     sin UI propia     sobre contenido normal
```

### 1. `CALIBRATION_UI`

Es la única superficie que puede mostrar puntos, instrucciones, botones o
estado de VIZZ. La ventana recoge puntos de pantalla y características del
backend ocular. No se acepta un perfil si falta una muestra o si el backend no
confirma CUDA.

### 2. `PROFILE_SEALED`

El perfil se guarda localmente como una estructura pequeña: versión, geometría
de pantalla, muestras de calibración y hash del modelo. No contiene vídeo ni
frames de cámara. Sellar el perfil es la única transición que permite iniciar
el runtime.

### 3. `HEADLESS_RUNTIME`

El proceso de fondo no importa Tkinter, no crea una ventana propia y no dibuja
controles. Exige `onnxruntime-gpu` con `CUDAExecutionProvider` y solicita la
cámara solo después de que la sesión CUDA haya sido creada. Si CUDA no está
disponible, termina sin pedir cámara.

### 4. `CONTENT_MODIFIER`

El resultado de gaze se entrega a un modificador de contenido. Su primera
implementación será un overlay transparente/click-through que puede cambiar
contraste, color, foco o atenuación de zonas de la pantalla. El contenido de
la aplicación normal queda debajo; VIZZ no aparece como aplicación visible.

## Estado de implementación

032 fija y prueba la separación de procesos, privacidad y compuerta CUDA. El
Python global del equipo todavía no tiene `onnxruntime-gpu`, OpenCV ni un
modelo ocular ONNX entrenado; por tanto este commit no inventa una captura ni
declara que el tracker ya esté operativo. El siguiente paso es instalar el
runtime en un entorno aislado, probar `CUDAExecutionProvider` con la RTX 4070
y conectar el primer modificador de contenido.

La ruta elegida usa ONNX Runtime CUDA porque el delegado GPU de MediaPipe
Python no está disponible de forma soportada en Windows. Referencias:

- https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html
- https://github.com/google-ai-edge/mediapipe/issues/5126
