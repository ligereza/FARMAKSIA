# Research 058 — cómo obtener geometría física de pantallas para VIZZ

Fecha: 2026-08-25  
Estado: revisión exploratoria previa a implementación

## Pregunta

¿Qué puede conocer VIZZ de una pantalla, su orientación y su distancia a los
ojos usando Windows, una webcam y software open source, sin inventar escala ni
convertir una calibración 2D en una medición física?

## Resumen ejecutivo

La información de Windows resuelve identidad y rectángulos lógicos del
escritorio, pero no entrega por sí sola ancho, profundidad ni pose física del
monitor. La vía geométrica reproducible requiere correspondencias entre
puntos 3D conocidos y puntos 2D observados por una cámara calibrada; OpenCV
documenta precisamente ese flujo con patrones y `solvePnP`, incluyendo
reproyección como control de calidad.

Para VIZZ, la mejor ruta de investigación es híbrida:

1. conservar el layout lógico 050;
2. obtener el tamaño físico del monitor por medición manual y usar EDID sólo
   como comprobación;
3. localizar temporalmente cada superficie con cuatro o más marcadores
   AprilTag/ChArUco, o con esquinas detectadas si la evidencia de imagen es
   suficiente;
4. calibrar intrínsecos y distorsión de la webcam;
5. estimar la pose de cada plano y su incertidumbre;
6. usar una representación de rostro/ojos 3D sólo cuando la escala y los
   intrínsecos estén auditados;
7. devolver `UNKNOWN` si falta escala, una superficie no es visible o el
   residual de reproyección no es aceptable.

No es necesario mantener la cabeza inmóvil durante el funcionamiento. Sí es
necesario que cámara y pantallas permanezcan rígidas durante la calibración de
la escena, y que el tracker estime el movimiento de la cabeza durante el uso.

## Evidencia científica e informática

### 1. Pose de una superficie plana

La documentación oficial de OpenCV describe la calibración de cámara mediante
correspondencias entre puntos 3D conocidos y observaciones 2D. Su ejemplo de
`solvePnP` usa un tablero plano con tamaño de cuadrado conocido; el resultado
define rotación y traslación entre el sistema del tablero y la cámara, y el
error de reproyección permite verificar la solución.

Fuente primaria: [OpenCV — Camera calibration with square chessboard](https://docs.opencv.org/5.0/tutorials/calib3d/camera_calibration_square_chess/camera_calibration_square_chess.html).

Consecuencia para VIZZ: conocer únicamente la resolución del monitor no crea
los puntos 3D. El tamaño físico debe venir de una medida, de un marcador con
tamaño conocido o de una fuente equivalente auditada.

### 2. Marcadores sobre el monitor

Pupil Labs usa una estrategia directamente relacionada: `real-time-screen-gaze`
identifica la pantalla en la cámara de escena mediante AprilTags. Su
documentación recomienda varias marcas dentro del mismo plano y señala que
usar más de dos mejora la robustez; el tracker de superficies transforma la
mirada hacia coordenadas de la superficie.

Fuentes open source de alta reputación: [Pupil Labs — real-time-screen-gaze](https://github.com/pupil-labs/real-time-screen-gaze),
[Pupil Labs — Surface Tracker](https://docs.pupil-labs.com/core/software/pupil-capture/).

Consecuencia para VIZZ: para la fase de desarrollo conviene usar cuatro o más
marcadores temporales en el bezel o cerca de las esquinas. No es necesario
dejar esos marcadores en el producto final; pueden servir para medir y
validar la pose, y luego probar una fase sin ellos.

### 3. Rostro, pose y escala métrica

MediaPipe Face Geometry separa los landmarks en coordenadas de pantalla de un
espacio 3D métrico. Su modelo canónico define la unidad de escala y la cámara
virtual debe aproximarse a los parámetros de la cámara física. El resultado
incluye una transformación rígida con escala uniforme, rotación y traslación.

Fuente primaria: [MediaPipe Face Geometry](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/face_mesh.md).

OpenFace expone landmarks 3D, pose de cabeza y vectores de mirada, pero indica
que necesita `fx`, `fy`, `cx` y `cy` de la cámara para estimar correctamente la
pose y el gaze en coordenadas 3D.

Fuentes open source: [OpenFace](https://github.com/TadasBaltrusaitis/OpenFace),
[OpenFace — API de pose y gaze](https://github.com/TadasBaltrusaitis/OpenFace/wiki/API-calls/84a8dac60c1c6d0210f223fdaeaf87146875b2ef).

Consecuencia para VIZZ: un landmark facial con `z` relativo no equivale a una
distancia física validada. Debemos registrar qué escala aporta el modelo y no
mezclarla silenciosamente con metros.

### 4. Movimiento natural de cabeza

La literatura de eye tracking con webcam trata el movimiento de cabeza como
una fuente estructural de error, no como ruido que deba descartarse siempre.
La investigación sobre mapeo adaptativo muestra que una homografía fija puede
depender de la posición actual de la cabeza y de la dirección de mirada.

Fuentes: [Webcam-based Eye Gaze Tracking under Natural Head Movement](https://arxiv.org/abs/1803.11088),
[Towards Accurate and Robust Cross-Ratio based Gaze Trackers](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/ETRA2014-075-huang.pdf).

Consecuencia para VIZZ: la calibración debe identificar la escena y el modelo
de ojos/cabeza por separado. No debemos “arreglar” el movimiento con una
transformación 2D fija ni entrenar sólo con la cabeza recta.

### 5. Límite de una sola webcam

Una cámara monocular puede estimar pose relativa, pero la escala absoluta no
queda determinada por la imagen si no existe un objeto de tamaño conocido, una
distancia conocida, una referencia facial métrica confiable u otra señal
adicional. El problema de escala es conocido en reconstrucción monocular.

Referencia: [Estimating Metric Poses of Dynamic Objects Using Monocular Visual-Inertial Fusion](https://arxiv.org/abs/1808.06753).

Consecuencia para VIZZ: `depth mask` puede ayudar a producir una hipótesis de
profundidad, pero no debe aceptarse como metros sin una prueba de escala y una
validación independiente.

## Comparación de rutas

| Ruta | Qué aporta | Qué no aporta | Decisión |
|---|---|---|---|
| Sólo Windows/EDID | identidad, resolución, rectángulo lógico, posible tamaño declarado | pose 3D, distancia ocular, confiabilidad universal del EDID | mantener como 050 |
| Medición manual + layout | escala física de ancho/alto | pose relativa cámara-monitor | requisito mínimo |
| Cuatro+ AprilTags/ChArUco | pose y orientación de superficie con cámara calibrada | no sustituye un tracker de ojos | ruta recomendada para validación |
| Esquinas/bezel sin marcadores | experiencia más limpia, posible pose planar | detección frágil ante reflejos, recortes y marcos ocultos | fase posterior |
| MediaPipe Face Geometry | rostro 3D relativo/métrico según modelo canónico | no garantiza precisión ocular ni pose del monitor | candidato de proveedor facial |
| OpenFace | pose, landmarks y vectores de gaze con intrínsecos | despliegue/actualidad/licencia deben auditarse | baseline informático, no instalación automática |
| `depth mask` monocular | hipótesis visual de profundidad | escala absoluta y robustez no garantizadas | sólo evidencia auxiliar |

## Requisitos que ahora sí están justificados

### Mínimo viable

- monitor plano;
- ancho y alto físicos medidos o fuente métrica equivalente;
- cámara rígida durante el setup;
- calibración de intrínsecos/distorsión;
- cuatro marcadores temporales con tamaño conocido por monitor;
- pose de monitor con residual de reproyección registrado;
- centros oculares y pose de cabeza con timestamps y confianza;
- layout lógico 050 versionado;
- `UNKNOWN` para huecos, oclusiones, pérdida de ojos, pose ambigua o escala no
  identificable.

### Robustez deseada

- seis o más marcadores o una superficie con más correspondencias que el
  mínimo;
- repetición del setup en tres capturas independientes;
- validación con monitor no usado en el ajuste;
- comparación entre pose por marcadores y pose por esquinas;
- cabeza libre durante validación, no sólo durante calibración;
- error por monitor, posición de cabeza, lentes, reflejos y distancia;
- modelo cilíndrico o por segmentos para una TV curva.

## Kill tests propuestos

1. Cambiar sólo la resolución: no puede cambiar el tamaño físico del plano.
2. Mover el monitor: la versión del layout o la pose debe cambiar y la
   calibración anterior debe invalidarse.
3. Quitar la escala física: el sistema debe producir `UNKNOWN` en distancia,
   no una estimación en metros.
4. Ocultar un marcador: cuatro+ marcas deben permitir degradación; con
   insuficientes correspondencias debe fallar explícitamente.
5. Mover la cabeza con la pantalla fija: el plano no debe moverse; sólo cambia
   el origen del rayo y la intersección.
6. Usar una pantalla curva con un plano: si el residual espacial muestra
   estructura, marcar el modelo plano como inadecuado.
7. Cambiar cámara o resolución de captura: invalidar intrínsecos hasta
   recalibrar.
8. Comparar con un patrón físico de tamaño conocido: la distancia estimada no
   puede depender únicamente de la máscara de profundidad.

## Qué queda desconocido

- si la webcam actual puede resolver la posición de ambos ojos con suficiente
  estabilidad para un rayo 3D;
- si el rostro del usuario y sus lentes producen oclusiones o reflejos que
  rompan el proveedor facial;
- si las esquinas de los monitores quedan visibles desde la cámara;
- si la TV es suficientemente plana para el modelo de un solo plano;
- qué error de reproyección y qué latencia se obtendrán en el host real;
- si una adaptación geométrica mejora la experiencia perceptual de VIZZ.

## Recomendación

No implementar aún una promesa de “distancia automática”. Implementar primero
un contrato 051 que acepte una especificación física declarada, haga la
intersección 3D y rechace datos provenientes sólo de Windows. En paralelo,
preparar una validación temporal con AprilTags/ChArUco. Si esa validación
funciona, intentar retirar los marcadores y medir cuánto se degrada el modelo.
