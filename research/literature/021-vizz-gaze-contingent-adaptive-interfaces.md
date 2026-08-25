# VIZZ — interfaces adaptativas al campo visual: ciencia, proyectos y límites

Fecha de corte: 2026-08-25.

## Pregunta de investigación

¿Qué existe ya alrededor de VIZZ y qué parte de la idea tiene respaldo
científico suficiente para convertirse en una interfaz de escritorio que
adapte el contenido a la relación entre ojos, cabeza, tarea y pantalla?

La conclusión no es que exista un repositorio que resuelva VIZZ completo. Las
piezas maduras aparecen separadas: seguimiento ocular, pose de cabeza,
geometría de monitores, rendering foveal y diseño de interacción. VIZZ debe
ser tratado como una composición experimental de esas capas.

## Hallazgo central

El nombre técnico más preciso para el concepto es:

> **interfaz de escritorio adaptativa al campo visual, consciente de pose y
> contingente a la mirada**.

No es, por definición, un mouse ocular. Tampoco es automáticamente 3D,
tratamiento visual o una promesa de reducir fatiga. La primera pregunta
experimental debe ser si una asignación dinámica de detalle, contraste,
movimiento y jerarquía mejora una tarea concreta sin introducir errores,
saltos o incomodidad.

La diferencia con el rendering foveal clásico es importante. En VR se reduce
el coste de renderizar una escena; en un escritorio VIZZ transformaría una
interfaz existente y debe conservar la legibilidad, los avisos periféricos y
la interacción normal cuando la mirada no pueda estimarse.

## Ciencia detrás del concepto

### 1. La visión no tiene la misma resolución en todo el campo

La fóvea concentra la mayor agudeza. La periferia conserva información de
contexto, movimiento, orientación y estructura general, pero pierde detalle y
sufre *crowding*: elementos cercanos pueden mezclarse y dificultar la
identificación. Por eso “bajar resolución fuera del punto de mirada” no debe
convertirse en “borrar la periferia”. La periferia puede ser precisamente la
señal que orienta la siguiente sacada o avisa de un cambio.

La literatura describe la visión periférica como una representación limitada
pero funcional para búsqueda, contexto y selección de candidatos; su alcance
depende de la tarea, el contraste y la densidad de estímulos. Un estudio de
escenas naturalistas reportó un span perceptual de aproximadamente 8° de radio
en su tarea concreta, no una constante universal para todas las personas o
interfaces. Fuentes: [revisión de visión periférica](https://www.annualreviews.org/content/journals/10.1146/annurev-vision-082114-035733),
[búsqueda de fovea a periferia](https://pmc.ncbi.nlm.nih.gov/articles/PMC8802022/) y
[crowding en búsqueda visual](https://pmc.ncbi.nlm.nih.gov/articles/PMC3084938/).

**Implicación para VIZZ:** el efecto debe depender de la excentricidad visual
respecto de la mirada, pero la política debe preservar al menos siluetas,
estructura, movimiento y alertas fuera de la zona de máximo detalle.

### 2. La mirada y la cabeza son señales diferentes

Cuando la cabeza se mueve, el reflejo vestíbulo-ocular desplaza los ojos en
sentido opuesto para estabilizar la escena. Por tanto, una variación de los
landmarks en la cámara no equivale automáticamente a que la persona haya
cambiado de objetivo. El modelo debe separar:

```text
movimiento de cámara en la imagen
    → pose de cabeza y escala/distancia
    → posición/orientación de los ojos
    → dirección de mirada
    → intersección con el plano de cada monitor
```

Fuente: [procesamiento central y reflejo vestíbulo-ocular](https://openstax.org/books/anatomy-and-physiology/pages/14-2-central-processing).

**Implicación para VIZZ:** no se debe entrenar un mapper que aprenda
directamente “landmark → píxel” sin conservar pose, escala interocular,
timestamps y configuración del monitor. La salida puede ser una región de
mirada e incertidumbre, no un píxel con falsa precisión.

### 3. Distancia, ángulo y dos ojos son geometría, no sólo clasificación

Para un monitor plano de ancho físico `W`, alto `H` y distancia perpendicular
`D`, su extensión angular aproximada es:

```text
theta_h = 2 atan(W / (2D))
theta_v = 2 atan(H / (2D))
```

Un monitor de 27 pulgadas 16:9 a 72 cm ocupa aproximadamente 45° en
horizontal y 26° en vertical. Eso puede caber dentro del campo binocular total,
pero no significa que todo sea legible con una sola fijación: la resolución
foveal sigue siendo local.

Para varios monitores, cada uno debe representarse por un plano y un
rectángulo físico. Con el centro de cada ojo `E_i` y un punto de mirada `P`:

```text
g_i = normalize(P - E_i)
gamma = acos(g_L · g_R)       # vergencia
d_i = norm(P - E_i)            # distancia a cada ojo
```

El punto debe hallarse intersectando un rayo incierto con cada plano, no
escalando globalmente píxeles del escritorio. Si ningún plano es compatible,
la salida es `UNKNOWN`; si varios lo son, se conservan hipótesis hasta tener
más evidencia. La distancia de pantalla también determina la demanda de
acomodación aproximadamente como `1/d_i` dioptrías. Si se dibuja profundidad
virtual o disparidad artificial en una pantalla fija, puede aparecer conflicto
vergencia–acomodación; eso obliga a ser conservador con cualquier experimento
estereoscópico.

Fuentes: [modelo de cámara y proyección de OpenCV](https://docs.opencv.org/4.10.0/d9/d0c/group__calib3d.html),
[formación de imagen en el ojo](https://openstax.org/books/f%C3%ADsica-universitaria-volumen-3/pages/2-5-el-ojo),
[conflicto vergencia–acomodación](https://pmc.ncbi.nlm.nih.gov/articles/PMC2879326/).

### 4. La latencia es parte de la percepción

Una pantalla contingente a la mirada tiene un tiempo entre el cambio de mirada
y el cambio visual. Ese tiempo puede producir bordes que “persiguen” la mirada,
parpadeo de calidad o una ventana desplazada. La medición debe incluir cámara,
inferencia, filtrado, composición y refresco de pantalla; no basta medir la
latencia del modelo.

El trabajo de medición directa de sistemas gaze-contingent subraya que incluso
demoras muy pequeñas pueden ser perceptibles en ciertos estímulos. En
experimentos de profundidad estereoscópica, el seguimiento impreciso y el
retardo también aparecen como fuentes de incomodidad. Fuentes:
[medición directa de latencia](https://pmc.ncbi.nlm.nih.gov/articles/PMC4077667/) y
[profundidad de campo contingente a la mirada](https://doi.org/10.1145/2628257.2628259).

**Implicación para VIZZ:** la política inicial debe tener histéresis, un área de
seguridad y una caída gradual. Si la confianza cae, congela la transformación
o vuelve al contenido estático; nunca debe perseguir cada frame ruidoso.

### 5. La tarea manda sobre la transformación

El mismo cambio visual puede ayudar a leer y perjudicar a programar o
monitorizar. Un estudio de resaltado controlado por mirada mejoró búsquedas de
palabras con alta similitud entre objetivo y distractores, pero no mostró el
mismo beneficio para todos los estímulos, incluyendo dígitos en la condición
reportada. Fuente: [eye-controlled highlighting](https://pmc.ncbi.nlm.nih.gov/articles/PMC6120491/).

**Implicación para VIZZ:** “lo que la persona mira” es una señal, no una orden.
La interfaz necesita un estado de tarea: escritura, lectura, navegación,
monitorización o pausa. El teclado, el mouse y el foco de la ventana son
covariables de contexto; no deben convertirse silenciosamente en verdad ocular.

## Proyectos similares y qué conviene extraer

| Proyecto o estándar | Qué resuelve | Qué conviene tomar | Qué no demuestra para VIZZ |
|---|---|---|---|
| [Pupil Labs / Pupil](https://github.com/pupil-labs/pupil) | Plataforma abierta de eye tracking, eventos, plugins y modelos de ojo 3D | Contratos de eventos, timestamps, separación de percepción y consumidores, geometría 3D | Requiere ecosistema de hardware Pupil Core para su mejor precisión; no es una solución webcam de pantalla |
| [WebGazer.js](https://github.com/brownhci/webgazer) | Estimación de mirada desde webcam en navegador y calibración con interacción | Protocolo de calibración local, adaptación incremental, modo de prueba rápido | Su salida depende de la cámara/usuario y no resuelve por sí sola plano físico, multimonitor ni incertidumbre; su mantenimiento oficial está discontinuado según su README |
| [MediaPipe Face Landmarker](https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/modules/face_landmark/README.md) | Landmarks faciales con ruta CPU/GPU | Frontend de ojos, escala interocular, párpados y pose como señales separadas | Landmarks no equivalen a gaze en pantalla; la integración GPU concreta debe medirse en el equipo real |
| [OpenSeeFace](https://github.com/emilianavt/OpenSeeFace) | Landmarks faciales en tiempo real y expresiones | Comparar estabilidad de landmarks con distintas poses, luz y resolución | Es un detector facial; no entrega automáticamente coordenadas fiables de monitor |
| [OpenFace](https://github.com/TadasBaltrusaitis/OpenFace) | Landmarks, pose, acción facial y gaze | Referencia de formato de salida y separación de pose/gaze | La versión visible en el repositorio es antigua para adoptarla sin un probe y revisión de dependencias |
| [OpenTrack](https://github.com/opentrack/opentrack) | Seguimiento de cabeza, filtrado, curvas, deadzone y recenter | Diseño de filtros de pose, calibración de centro y curvas de respuesta | Sigue la cabeza, no la mirada; no debe usarse como ground truth visual |
| [OptiKey](https://github.com/Optikey/Optikey/) | Interfaz asistiva Windows controlada por mirada | Dwell, selección segura, fallback físico y accesibilidad | Es un teclado/control ocular, no una política de detalle visual ni un sistema de alivio de fatiga |
| [OpenXR eye gaze](https://registry.khronos.org/OpenXR/specs/1.0/man/html/XR_EXT_eye_gaze_interaction.html) | Contrato estándar para entrada de gaze en XR | Semántica de sample time y poses; separación de proveedor y consumidor | Está orientado a XR; no define calibración de webcam para escritorio Windows |
| [Unity OpenXR foveated rendering](https://docs.unity.cn/Packages/com.unity.xr.openxr%401.14/manual/features/foveatedrendering.html) y [NVIDIA VRS](https://developer.nvidia.com/vrworks/graphics/variablerateshading) | Reducción de calidad periférica para ahorrar rendering | Idea de niveles de calidad y proveedor GPU/variable shading | Optimiza escenas renderizadas; no es un transformador seguro para cualquier aplicación 2D |

### Selección de adopción

La preferencia de FARMAXIA es GitHub de alta reputación y evitar corpus o pesos
arbitrarios. Con ese criterio:

1. **Adoptar primero como frontend experimental:** MediaPipe Face Landmarker
   GPU o el frontend ya presente si su contrato y proveedor están verificados.
2. **Usar como referencia de pose y filtrado:** OpenTrack; no como fuente de
   mirada.
3. **Usar como referencia de arquitectura y eventos:** Pupil; no copiar una
   dependencia de hardware que no tenemos.
4. **Usar para comparar protocolos de interacción:** OptiKey y WebGazer,
   manteniendo separados sus objetivos.
5. **Usar OpenXR/VRS sólo como inspiración de política de calidad** hasta que
   exista un renderer o compositor con control de regiones.

No se recomienda descargar todavía un modelo adicional. Primero hay que
probar el contrato local, licencia, proveedor GPU, latencia y comportamiento
fuera de dominio. Un modelo preentrenado de gaze puede producir un vector
angular útil y aun así fallar al convertirlo en un punto de pantalla.

## Arquitectura propuesta para VIZZ

```text
captura de cámara + monitor layout + teclado/mouse + ventana activa
                         │
                         ▼
1. percepción GPU
   ojos, iris, párpados, landmarks, pose, timestamps, calidad
                         │
                         ▼
2. estado geométrico
   escala interocular, posición de cabeza, rayos, planos de monitores,
   distancia/vergencia, configuración DPI, hipótesis de monitor
                         │
                         ▼
3. estado atencional
   región de mirada + incertidumbre + fijación/sacada/parpadeo + tarea
                         │
                         ▼
4. política visual
   detalle, contraste, densidad, movimiento, foco, prioridad y transición
                         │
                         ▼
5. compositor reversible
   overlay o capa por aplicación; fallback estático; kill switch
```

### Salida correcta del tracker

El tracker no debe prometer un píxel. Debe producir:

```text
GazeState {
  timestamp_capture,
  timestamp_display,
  eye_centers_camera/world,
  head_pose,
  gaze_ray_or_region,
  monitor_hypotheses,
  confidence,
  covariance_or_radius,
  fixation_state,
  unknown_reason
}
```

La región visual se puede modelar como una elipse sobre el plano del monitor.
Una primera política prudente puede hacer que su radio sea función de la
incertidumbre y la velocidad:

```text
r_safe = r_base + v_gaze * latency_estimate + k * sigma_gaze
```

Esto es una regla de ingeniería propuesta, no una ley fisiológica. Si `r_safe`
es grande, VIZZ debe reducir la agresividad de la adaptación o congelarla.

### Política visual en tres zonas

1. **Fóvea estimada:** texto, controles y gráficos prioritarios conservan el
   máximo detalle.
2. **Parafóvea:** conservar estructura, bordes, palabras parcialmente útiles,
   continuidad espacial y affordances; reducir sólo el detalle de baja
   prioridad.
3. **Periferia:** reducir densidad, textura o animaciones no esenciales, pero
   mantener cambios bruscos, siluetas, alertas y orientación general.

Los radios deben expresarse en grados visuales o en distancia física estimada,
no como un círculo fijo de píxeles. Los valores iniciales son hiperparámetros a
comparar, no recomendaciones clínicas.

## Programa experimental recomendado

### Fase A — geometría sin transformación visual

Registrar sólo la cadena `cámara → landmarks → pose → rayos → plano de
monitor`, incluyendo movimiento de cabeza, distancia, monitor activo, DPI y
`UNKNOWN`. Validar con escenas sintéticas y una pantalla física de geometría
conocida. No modificar todavía la pantalla del usuario.

**Éxito:** la salida conserva el monitor correcto y la incertidumbre crece de
forma honesta cuando la cámara se mueve, se pierde un ojo o el layout cambia.

### Fase B — playback controlado

Aplicar una máscara o niveles de detalle a capturas reproducidas. Comparar:

```text
estático completo
estático con clutter reducido
adaptativo a mirada con incertidumbre
adaptativo a mirada sin protección  (control de fallo)
```

Medir latencia extremo a extremo y artefactos antes de una prueba prolongada.

### Fase C — overlay pasivo durante trabajo real

El sistema observa y registra mirada, teclado, mouse y ventana activa, pero sólo
muestra un diagnóstico no intrusivo. La posición del mouse es una covariable de
interacción; el input de teclado puede marcar que se está escribiendo, pero no
se etiqueta como “mirada en texto” sin evidencia independiente.

### Fase D — comparación A/B por tarea

Comparar el mismo usuario y tareas contrabalanceadas entre interfaz estática y
VIZZ. Separar lectura, escritura de código, navegación y monitorización.
Evaluar por sesión/tarea completa, no por frame:

- tiempo y errores de tarea;
- relecturas, regresiones y longitud de recorrido visual;
- número/amplitud de sacadas y duración/dispersión de fijaciones;
- detección de alertas periféricas;
- latencia y porcentaje `UNKNOWN`;
- comodidad, fatiga y síntomas molestos auto-reportados.

Una mejora sólo se acepta si no degrada precisión, alertas periféricas,
latencia o comodidad. No se afirma beneficio médico.

## Kill tests obligatorios

- La estimación salta entre regiones o persigue sacadas: volver a contenido
  estático y revisar latencia/histéresis.
- El blur o reducción de detalle empeora la detección periférica o la búsqueda:
  conservar estructura y retirar esa política.
- El cambio de distancia/cabeza hace crecer el error sin que crezca la
  incertidumbre: falla la geometría eye-centric.
- Cambiar monitor, DPI, resolución o cámara mantiene una coordenada antigua:
  invalidar la calibración y devolver `UNKNOWN`.
- VIZZ mejora una tarea pero empeora otra: separar políticas por tarea; no
  generalizar el resultado.
- Sólo mejora frente a una interfaz deliberadamente desordenada, pero no
  frente a un baseline estático limpio: no hay efecto VIZZ demostrado.
- Una transformación de profundidad en pantalla produce incomodidad o
  conflicto vergencia–acomodación: retirar la estereoscopía y conservar sólo
  adaptación 2D.

## Qué queda demostrado y qué no

**Respaldado:** la resolución espacial es desigual; la periferia aporta
contexto; el crowding importa; el gaze-contingent rendering es una técnica
establecida; la latencia y la precisión del tracker limitan su utilidad; la
pose y la geometría física deben separarse de la salida de gaze.

**Hipótesis de VIZZ:** una interfaz 2D que asigna detalle, contraste y
movimiento de forma consciente de tarea, cabeza, distancia e incertidumbre
puede sentirse más coherente y eficiente durante trabajo normal.

**No demostrado:** que VIZZ mejore la visión, reduzca fatiga para cualquier
persona, corrija miopía/hipermetropía/astigmatismo, compense una receta de
lentes, mida distancias exactas con una webcam o sea seguro durante intoxicación.

## Fuentes principales

- [A Summary Statistic Representation in Peripheral Vision](https://pmc.ncbi.nlm.nih.gov/articles/PMC4032502/)
- [Capabilities and Limitations of Peripheral Vision](https://www.annualreviews.org/content/journals/10.1146/annurev-vision-082114-035733)
- [Visual search in naturalistic scenes](https://pmc.ncbi.nlm.nih.gov/articles/PMC8802022/)
- [Gaze-Contingent Multiresolutional Displays: review](https://journals.sagepub.com/doi/10.1518/hfes.45.2.307.27235)
- [Towards foveated rendering for gaze-tracked VR](https://doi.org/10.1145/2980179.2980246)
- [An integrative view of foveated rendering](https://www.sciencedirect.com/science/article/pii/S0097849321002211)
- [Direct measurement of system latency](https://pmc.ncbi.nlm.nih.gov/articles/PMC4077667/)
- [The applicability of eye-controlled highlighting](https://pmc.ncbi.nlm.nih.gov/articles/PMC6120491/)
- [Pupil Labs](https://github.com/pupil-labs/pupil)
- [WebGazer.js](https://github.com/brownhci/webgazer)
- [MediaPipe Face Landmarker](https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/modules/face_landmark/README.md)
- [OpenSeeFace](https://github.com/emilianavt/OpenSeeFace)
- [OpenTrack](https://github.com/opentrack/opentrack)
- [OptiKey](https://github.com/Optikey/Optikey/)
- [OpenXR eye gaze interaction](https://registry.khronos.org/OpenXR/specs/1.0/man/html/XR_EXT_eye_gaze_interaction.html)
