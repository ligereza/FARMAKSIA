# Experimento 086 — VIZZ: webcam real → cámara de Blender

## Qué faltaba

El experimento 085 tenía una cámara virtual controlable, pero no estaba
conectada a la webcam. Este experimento cierra ese circuito:

```text
webcam
  ↓
GPU tracker: distancia entre ojos + ancho facial
  ↓
escala relativa respecto a P0
  ↓
archivo local JSON atómico
  ↓
timer de Blender
  ↓
VIZZ_CONTROLLER[observer_distance_m]
  ↓
driver de VIZZ_CAMERA
```

El foco usa un segundo canal independiente, `focus_distance_m`. El lanzador
elige `locked`: la cámara sigue tu distancia, pero el foco permanece en el
baseline virtual de `0.60 m`, haciendo visible el efecto. Para la comparación
óptica en que la pantalla siempre permanece enfocada, se puede usar
`--focus-mode screen`.

La webcam entrega una razón relativa, no metros absolutos. Para este experimento
no hace falta medir con una regla: `0.60` es sólo una distancia virtual inicial
para la cámara de Blender. Si `s` es el tamaño facial aparente relativo a P0:

```text
d_virtual = 0.60 / s
```

P0 se sella con la barra espaciadora cuando estés en una postura cómoda. Esto
preserva el cambio relativo al acercarte o alejarte, pero no afirma que Blender
esté midiendo metros físicos reales.

La cámara de Blender se mueve; la geometría del monitor no se mueve. El puente
no renderiza cada frame automáticamente, porque eso puede saturar la GPU. La
vista 3-D o renderizada de Blender se actualiza con la cámara, y F12 se usa sólo
cuando quieras congelar un estado.

## Requisitos

- Blender 4.5.4 instalado;
- el `.blend` del experimento 085 ya generado;
- `.venv` del repositorio con el tracker GPU y el modelo local existente;
- no se descarga nada y no se usa red.

## Ejecución exacta

### Opción recomendada: un solo lanzador

Desde PowerShell, ejecuta una sola vez:

```powershell
Set-Location C:\IA\FARMAXIA
.\experiments\086-vizz-blender-live-distance-bridge\start_vizz_blender.ps1
```

El lanzador abre Blender, activa el puente y arranca el tracker CUDA a 5 Hz
sin límite de tiempo. No abre una segunda PowerShell. El tracker queda oculto
como consola; la ventana de cámara aparece únicamente durante P0 para que
puedas pulsar `ESPACIO`. Al cerrar Blender, el lanzador detiene el tracker.

Si PowerShell bloquea la ejecución de scripts, usa:

```powershell
powershell -ExecutionPolicy Bypass -File C:\IA\FARMAXIA\experiments\086-vizz-blender-live-distance-bridge\start_vizz_blender.ps1
```

### 1. Abrir la escena

```powershell
$blender = "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
& $blender "C:\IA\FARMAXIA\experiments\085-vizz-blender-focus-distance\output\vizz_focus_distance.blend"
```

### 2. Activar el puente dentro de Blender

Abre `Scripting → Python Console` y pega una sola línea:

```python
exec(compile(open(r"C:\IA\FARMAXIA\experiments\086-vizz-blender-live-distance-bridge\blender_live_bridge.py", encoding="utf-8").read(), r"C:\IA\FARMAXIA\experiments\086-vizz-blender-live-distance-bridge\blender_live_bridge.py", "exec"))
```

Debe aparecer `VIZZ_LIVE_BRIDGE_ACTIVE`. No cierres Blender.

### 3. Iniciar la webcam en otra PowerShell

```powershell
Set-Location C:\IA\FARMAXIA
.\.venv\Scripts\python.exe experiments\086-vizz-blender-live-distance-bridge\run_live_distance.py --sample-hz 5 --no-trace
```

Durante P0 aparecerá la cámara. Si ves `ROSTRO + 2 OJOS OK`, pulsa `ESPACIO`.
El programa captura una ventana robusta de referencia y después cierra la
previsualización. Desde ese momento, acercarte o alejarte mueve la cámara de
Blender mediante el archivo local. El proceso no termina solo: usa `Ctrl+C`
cuando quieras detenerlo.

Para una prueba limitada se puede añadir `--duration 600`, pero no es necesario
para el uso normal.

Para parar la webcam: `Ctrl+C` en esa PowerShell. Para parar el puente en
Blender:

```python
bpy.app.driver_namespace["vizz_stop_live_bridge"]()
```

## Contrato de seguridad

- Se persiste sólo el último estado geométrico; no se guarda vídeo.
- No se guarda texto, identidad de teclas ni contenido de pantalla.
- Un estado `UNKNOWN` no mueve la cámara ni conserva una nueva distancia.
- Si las dos reglas faciales discrepan, el puente escribe `UNKNOWN`.
- Si la cara desaparece, el puente escribe `UNKNOWN`.
- El archivo JSON se escribe temporalmente y se reemplaza atómicamente para que
  Blender nunca lea una escritura parcial.
- No hay sockets, HTTP, descargas, ejecución remota ni inyección de input.

## Límites

Este puente mide distancia relativa al P0. Si P0 está mal medido, todos los
metros quedan desplazados proporcionalmente. La cámara virtual sigue siendo un
proxy óptico; no es el ojo humano y no demuestra comodidad ni profundidad 3-D.
El render Cycles se conserva como salida realista, pero el seguimiento en vivo
se mantiene separado del render pesado.
