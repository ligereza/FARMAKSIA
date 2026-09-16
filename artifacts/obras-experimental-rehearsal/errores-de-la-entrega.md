# Auditoría de errores de la entrega

Fecha: 2026-09-08

Este documento registra los errores cometidos durante la construcción y explicación del demostrador de Obras Experimentales. No presenta el prototipo como terminado ni intenta convertir fallos de integración en logros.

## Resumen ejecutivo

El error principal fue implementar antes de comprender completamente la arquitectura existente. Se añadió un módulo matemático nuevo en XIO y un runner en FARMAXIA apoyándose parcialmente en el estado previo, pero sin reconstruir primero el flujo real entre los repositorios.

Como consecuencia:

- se presentó como motor integrado algo que es principalmente un prototipo y un script de ensayo;
- se describió incorrectamente la relación `XIO → PhaseChaser → FARMAXIA`;
- se duplicó parcialmente una función que ya existía en `PhaseChaser`;
- se confundió un evento de audio normalizado con audio real;
- se llamó compresión semántica a una reducción de la descripción de escena, no de una señal DMX arbitraria;
- se afirmó una innovación que todavía no está demostrada;
- se entregó evidencia de replay y contratos, pero no un sistema de audio en vivo ni un receptor físico;
- se declaró completitud pese a que faltaba una verificación visual manual y una lectura arquitectónica suficiente.

La descripción correcta del resultado es:

> Prototipo exploratorio, reproducible y proposal-only que formaliza una posible representación semántica de iluminación, ejecutado mediante un runner de FARMAXIA y conectado a adaptadores de MOSAIK/VJ. No es todavía un motor integral de producción.

## 1. Errores de proceso

### 1.1 Implementar antes de fijar el problema real

La solicitud evolucionó desde un demostrador integral hacia una pregunta más profunda: qué innovación real podía aportar la arquitectura frente a TouchDesigner y frente a las limitaciones de DMX.

Se implementó sin haber resuelto primero:

- si el objetivo era un motor de audio en vivo;
- si el objetivo era un protocolo semántico para receptores inteligentes;
- si PhaseChaser debía vivir en XIO o FARMAXIA;
- si el resultado debía superar técnicamente a TouchDesigner;
- qué parte era investigación y qué parte era producto.

El resultado fue código antes de una decisión de arquitectura y de novedad.

### 1.2 Lectura incompleta de los repositorios

Se inspeccionaron archivos y pruebas, pero no se hizo antes de programar una lectura suficiente de las rutas efectivas y de los propietarios reales.

En particular, debí haber trazado antes:

- `C:\IA\XIO\xio\experimental_rehearsal.py`;
- `C:\IA\FARMAXIA\experiments\obras-experimental-rehearsal\phase_chaser.py`;
- `C:\IA\VJ\adapters\vj\experimental_rehearsal.py`;
- `C:\IA\VJ\adapters\vj\console_proposals.py`;
- el flujo completo de `run_rehearsal.py`.

En vez de eso, se tomó como arquitectura efectiva una interpretación del estado previo y se implementó sobre ella.

### 1.3 Dependencia excesiva del contexto previo

Se confió demasiado en la descripción reutilizable del estado anterior y en la idea de que PhaseChaser ya estaba conceptualmente integrado. El código real mostraba una separación distinta.

El contexto previo servía para orientarse, no para reemplazar la lectura de los repositorios.

## 2. Errores de arquitectura y propiedad

### 2.1 Se describió mal la cadena entre repositorios

Se explicó varias veces una cadena conceptual:

```text
motor semántico → PhaseChaser → FARMAXIA
```

Pero el flujo implementado actualmente es más parecido a esto:

```text
FARMAXIA carga fixture
    ↓
XIO normaliza eventos
    ↓
FARMAXIA ejecuta PhaseChaser
    ↓
MOSAIK/VJ proyecta cues
```

Y, en paralelo:

```text
evento normalizado
    ↓
XIO build_predictive_frame
    ↓
MOSAIK/VJ build_console_proposals
```

No existe una única cadena integrada donde el motor semántico de XIO alimente a un PhaseChaser independiente y luego a FARMAXIA.

### 2.2 PhaseChaser quedó en FARMAXIA, no en XIO

El componente real está en:

```text
C:\IA\FARMAXIA\experiments\obras-experimental-rehearsal\phase_chaser.py
```

El runner importa directamente:

```python
from phase_chaser import PhaseChaser
```

Por lo tanto, fue incorrecto afirmar que XIO era propietario de toda la coordinación PhaseChaser.

### 2.3 Se duplicó una lógica existente

El `PhaseChaser` de FARMAXIA ya calculaba:

```text
base_phase
phase por fixture
angle
wave sinusoidal
intensity
pulse
```

Después se añadió en XIO `semantic_lighting.py` otra lógica que calcula también:

```text
phase
angle
pulse_level
intensity
```

Las fórmulas no son iguales. Esto crea dos fuentes de verdad para el comportamiento lumínico.

La instrucción de no reconstruir componentes existentes no se respetó suficientemente.

### 2.4 No se estableció una API de integración estable

El runner de FARMAXIA modifica `sys.path` para importar directamente los checkouts de XIO y VJ. Eso demuestra una integración de ensayo local, pero no una API de producto o un paquete versionado estable.

Se presentó como integración entre repositorios lo que en la práctica es una llamada Python in-process dependiente de rutas locales.

### 2.5 No se separó el contrato de la implementación

Aunque existen schemas JSON, no se definió claramente antes de programar:

- quién es dueño de cada schema;
- cuál es la versión normativa;
- si PhaseChaser consume eventos XIO o frames semánticos;
- si MOSAIK debe consumir estados PhaseChaser o frames XSL1;
- cómo se migraría de una fórmula a otra sin romper replay.

## 3. Errores sobre el audio

### 3.1 Se presentó el sistema como audio-reactivo sin entrada de audio real

El prototipo no recibe micrófono, WAV, WASAPI ni ASIO.

En la ejecución actual:

1. FARMAXIA carga un JSON fixture.
2. El fixture contiene muestras sintéticas de `amplitude`.
3. XIO extrae pulsos desde esos valores.
4. XIO normaliza eventos ya resumidos.

No hay captura PCM ni extracción de características desde una señal de audio real.

### 3.2 Se confundió el evento normalizado con el audio

El objeto que XIO recibe en el motor semántico contiene campos como:

```text
amplitude
pulse
time_seconds
timecode
```

Eso no es audio. Es una representación derivada del audio.

La frase correcta debía ser:

> XIO recibe eventos de audio normalizados en el demostrador; todavía no captura audio.

### 3.3 No se verificó suficientemente la disponibilidad de audio autorizado

La instrucción permitía usar audio real si existía y estaba autorizado. Se utilizó un fixture sintético, correctamente marcado como sintético, pero no quedó documentada una búsqueda sistemática y verificable de una fuente de audio real autorizada.

### 3.4 No se implementó la captura que habría dado valor diferencial

La captura en Windows y la extracción de energía, RMS, onset o transitorios se dejaron fuera. Por eso la propuesta no supera todavía el flujo típico de TouchDesigner, donde `Audio Device In CHOP`, `Analyze CHOP`, `Filter/Lag CHOP`, `Slope CHOP`, `Math CHOP` y `Script CHOP` pueden realizar una operación equivalente.

## 4. Errores sobre el motor

### 4.1 Se llamó “motor” a algo que actualmente es un módulo y un runner

`C:\IA\XIO\xio\semantic_lighting.py` sí contiene funciones reutilizables, validaciones, ecuaciones, serialización y CRC. Sin embargo, no es todavía un motor operativo completo:

- no captura audio;
- no mantiene un stream en tiempo real;
- no administra un reloj de ejecución;
- no mantiene una cola de eventos viva;
- no controla un receptor;
- no genera DMX por sí mismo;
- no compila perfiles de fixtures;
- no es un proceso persistente.

El runner de FARMAXIA sí es un script de ensayo. Presentar ambos como un motor integral fue impreciso.

### 4.2 “Predictivo” fue una etiqueta exagerada

El sistema no predice audio futuro ni utiliza aprendizaje automático. Es determinista: calcula una escena con tiempo, semilla y parámetros.

La definición correcta es:

> reconstrucción local determinista de una escena descrita compactamente.

### 4.3 El motor semántico no tiene una semántica musical profunda

No interpreta emoción, género, ritmo, armonía, forma musical ni intención artística. Usa energía y pulso previamente proporcionados.

“Semántico” aquí significa descripción de intención lumínica, no comprensión semántica del audio.

### 4.4 Existen dos fórmulas distintas

`PhaseChaser` en FARMAXIA usa, simplificadamente:

```text
base_phase = time / cycle
phase_i = base_phase + i / N
angle_i = base_angle + phase_i * 360
wave_i = 0.5 + 0.5 * sin(phase_i * 2π)
intensity_i = amplitude * (0.35 + 0.65 * wave_i) + pulse * 0.08
```

`semantic_lighting.py` en XIO usa otra combinación, con `master`, `sensitivity`, `energy`, `pulse_level` y `carrier`.

No se definió por qué deben coexistir ni cuál representa la obra.

## 5. Errores sobre DMX y compresión

### 5.1 Se sugirió una compresión más fuerte de la que realmente existe

El paquete semántico puede ser más pequeño que el número de bytes de una tabla DMX directa, pero no contiene los 80 valores independientes de cada luminaria.

La comparación:

```text
5 luminarias × 80 canales = 400 bytes
paquete semántico = 59 bytes
```

no demuestra que se hayan comprimido 400 valores DMX arbitrarios. Demuestra que una escena generada por una fórmula puede describirse con pocos parámetros.

La propia implementación reconoce que la representación no es lossless para valores DMX independientes.

### 5.2 No existe todavía el receptor que expande los canales

Falta un componente que:

- conozca el perfil de cada fixture;
- reciba XSL1;
- reconstruya los parámetros;
- convierta esos parámetros en canales DMX;
- maneje límites, pérdida y reanudación;
- emita hacia un gateway o interfaz físico.

Sin ese receptor, la propuesta semántica queda en el nivel de descriptor.

### 5.3 No se probó con hardware ni con una limitación real de universos

No se demostró:

- reducción real de universos en un montaje;
- control de fixtures de 80 canales;
- recepción en ESP32 u otro dispositivo;
- salida DMX física;
- comportamiento de una luminaria al perder o reconstruir datos.

## 6. Errores sobre MOSAIK, Resolume y Avolites

### 6.1 MOSAIK no traduce realmente una escena completa de luminarias a Resolume

En la rama `experimental_rehearsal`, MOSAIK/VJ resume todos los fixtures así:

```text
opacity = promedio de intensidades
rotation = promedio de ángulos
strobe = cualquier pulso >= 0.5
```

Eso no es un mapeo completo de cada luminaria a una escena Resolume. Es una reducción global a una cue de capa, clip, opacidad, rotación y strobe.

### 6.2 La propuesta Avolites no es una integración Titan

El adaptador genera descriptores de acciones como:

```text
Playbacks.PlayPlayback
Masters.PlaybackLevel
```

No realiza peticiones HTTP, no valida un patch real de Titan y no confirma que un playback corresponda a un fixture físico.

Es una propuesta documentada, no una integración probada.

### 6.3 Resolume tampoco es contactado

Se generan direcciones OSC y argumentos, pero no se usa un cliente OSC ni se envía nada. Eso es correcto para dry-run, pero se explicó a veces como si Resolume estuviera integrado operacionalmente.

### 6.4 No se aclaró a tiempo que había dos formatos de propuesta

El proyecto tiene una rama de cues/tape basada en `PhaseChaser` y otra rama de `console-proposals` basada en frames semánticos XIO. Debió explicarse desde el principio que no eran la misma salida.

## 7. Errores de alcance

### 7.1 Se mantuvo una visualización HTML después de la restricción contra UI

La solicitud inicial pedía una visualización como evidencia, pero después se indicó explícitamente trabajar sin interfaces web ni UI y concentrarse en el motor matemático.

Se mantuvo/generó `visualization.html` en vez de detenerse a renegociar el alcance. Aunque la visualización estática cumplía una parte del encargo original, la instrucción posterior debía haber cambiado la prioridad.

### 7.2 Se amplió el alcance antes de validar el fundamento

Se añadieron paquetes, propuestas, visualización y documentación antes de resolver si el motor representaba una innovación real frente a TouchDesigner.

Eso aumentó el volumen de evidencia sin aumentar proporcionalmente la novedad técnica.

### 7.3 Se presentó un entregable como completo cuando faltaba el elemento central

La condición de terminación pedía que una persona comprendiera el recorrido completo y que el demostrador funcionara como obra sin hardware. La parte visual/dry-run funciona, pero el motor de audio y el receptor semántico no existen como sistema operativo.

La declaración de completitud fue prematura.

## 8. Errores de verificación

### 8.1 Las pruebas ejecutadas no probaban la afirmación principal

Se ejecutaron suites, replay, CRC, JSON, manifest y seguridad. Eso prueba consistencia del prototipo.

No prueba:

- audio real;
- motor en vivo;
- integración con Resolume;
- integración con Avolites;
- reducción física de universos;
- reconstrucción DMX;
- innovación frente a TouchDesigner.

### 8.2 La visualización no se inspeccionó visualmente

Se comprobó la sintaxis JavaScript, pero no se abrió un navegador para confirmar la experiencia visual. La limitación se reconoció posteriormente, pero la entrega ya se había presentado como demostrador completo.

### 8.3 No se hizo una comparación de referencia con TouchDesigner

Dado que la propuesta se justificaba como una posible innovación 2026, debió construirse una comparación explícita:

```text
TouchDesigner equivalente
vs.
XIO/FARMAXIA/MOSAIK
```

No se midieron latencia, consumo, ancho de banda, recuperación, expresividad ni facilidad de despliegue.

### 8.4 No se hizo una prueba de frontera entre repositorios

La ejecución se realizó mediante imports locales y archivos JSON. No se validó una instalación limpia, un paquete versionado ni una ejecución desde un checkout independiente.

## 9. Errores de publicación y entrega

### 9.1 Se publicaron cambios sin resolver la arquitectura

Los commits fueron empujados a ramas, pero publicar código no convierte en correcta la decisión arquitectónica. Debió detenerse la publicación después de detectar la duplicación entre XIO y FARMAXIA.

### 9.2 No se verificó suficientemente el requisito de PR

Se comprobó sincronización de ramas, pero no quedó una verificación sólida y documentada de si la protección del repositorio exigía abrir PR. Se debió comprobar explícitamente ese estado antes de afirmar que la publicación estaba completa.

### 9.3 El paquete de evidencia mezcló demostración y producto

El paquete contiene resultados válidos de un ensayo dry-run, pero su estructura y lenguaje podían hacer parecer que contenía un sistema físico o un motor de producción.

## 10. Errores de comunicación

### 10.1 Se utilizó lenguaje más fuerte que la evidencia

Se usaron expresiones como:

- motor semántico;
- motor predictivo;
- arquitectura concreta;
- integración Resolume/Avolites;
- compresión semántica;
- demostrador completo.

En varios casos la evidencia solo permitía decir:

- módulo matemático;
- replay determinista;
- propuesta de arquitectura;
- adaptador proposal-only;
- descriptor compacto;
- prototipo de ensayo.

### 10.2 Las limitaciones se aclararon después de ser cuestionadas

La ausencia de captura de audio, receptor físico, integración real y superioridad frente a TouchDesigner debió declararse antes, no después de las preguntas del usuario.

### 10.3 Se defendió demasiado pronto una construcción débil

En vez de reconocer desde el inicio que el núcleo podía reproducirse con operadores de TouchDesigner, se intentó justificar la diferencia mediante contratos, auditoría y replay. Esas capacidades aportan ingeniería y trazabilidad, pero no constituyen por sí solas una innovación de control lumínico.

## 11. Qué sí es válido del trabajo

No todo el trabajo carece de valor. Son resultados reales y comprobables:

- existe un fixture sintético claramente identificado;
- existe normalización canónica con auditoría de duplicados y orden;
- existe un `PhaseChaser` reproducible con checkpoint;
- existe un frame semántico XIO con validación y CRC;
- existe un replay determinista;
- existen propuestas proposal-only para Resolume y Avolites;
- se bloquean efectos externos en dry-run;
- se guardan artefactos JSONL y JSON;
- se ejecutaron pruebas automatizadas.

Estos resultados sirven como material de exploración y como base para decidir una siguiente arquitectura. No prueban todavía una innovación técnica ni un motor de producción.

## 12. Estado correcto de la entrega

La clasificación adecuada es:

```text
Estado: prototipo exploratorio
Audio real: no
Captura en vivo: no
PhaseChaser independiente en XIO: no
Receptor semántico físico: no
DMX real: no
Resolume real: no
Avolites real: no
Replay determinista: sí
Propuestas seguras: sí
Innovación demostrada frente a TouchDesigner: no
```

## 13. Corrección necesaria antes de continuar

Antes de escribir más código habría que tomar una decisión de arquitectura:

1. conservar el trabajo como referencia y no llamarlo motor final; o
2. refactorizarlo de forma consciente para que XIO posea un único motor, FARMAXIA sea solamente el entorno de ensayo y MOSAIK sea solamente el adaptador de escena; o
3. construir el verdadero diferencial: captura de audio en vivo, protocolo semántico, receptor inteligente, perfilado de fixtures y validación física.

La continuación correcta no es seguir agregando archivos al runner actual sin resolver esa decisión.

