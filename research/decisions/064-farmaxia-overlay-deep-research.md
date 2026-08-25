# Decision 064 - Deep research del overlay GPU, input y multimonitor

## Estado

Recomendación arquitectónica. El backend `058` ya implementa la primera
hipótesis de composición, pero el click-through entre procesos permanece
pendiente de aceptación manual. No se debe presentar como funcionalidad
confirmada hasta superar ese kill test.

## Pregunta

¿Cómo debe FARMAXIA dibujar una capa visual sobre aplicaciones existentes sin
convertirse en una segunda interfaz que robe el foco, bloquee el mouse,
capture la pantalla o consuma GPU continuamente?

La respuesta separa cuatro contratos: composición, input, geometría de
monitores y privacidad. Mezclarlos fue la causa conceptual del primer fallo.

## Evidencia primaria

### Windows y Microsoft

- [Window Features - Layered Windows](https://learn.microsoft.com/en-us/windows/win32/winmsg/window-features)
  documenta que una ventana layered con `WS_EX_TRANSPARENT` pasa los eventos de
  mouse a las ventanas inferiores. También distingue este camino del contenido
  alpha y del legacy de ventanas layered.
- [WM_NCHITTEST](https://learn.microsoft.com/en-us/windows/win32/inputdev/wm-nchittest)
  define `HTTRANSPARENT` como transparente respecto de ventanas del mismo
  thread. Por sí solo no es un contrato suficiente para una ventana top-level
  frente a otra aplicación.
- [WM_MOUSEACTIVATE](https://learn.microsoft.com/en-us/windows/win32/inputdev/wm-mouseactivate)
  define `MA_NOACTIVATE`: no activar la ventana y no descartar el clic.
- [Extended Window Styles](https://learn.microsoft.com/en-us/windows/win32/winmsg/extended-window-styles)
  distingue `WS_EX_TRANSPARENT` (orden de pintura de hermanos),
  `WS_EX_LAYERED` (ventana layered), `WS_EX_NOACTIVATE` y
  `WS_EX_NOREDIRECTIONBITMAP` (visual proporcionado por otro mecanismo).
- [DirectComposition architecture](https://learn.microsoft.com/en-us/windows/win32/directcomp/architecture-and-components)
  describe un árbol retenido, commits atómicos, composición en DWM y la
  posibilidad de omitir trabajo cuando una ventana está completamente oculta.
- [DXGI_SWAP_CHAIN_DESC1](https://learn.microsoft.com/en-us/windows/win32/api/dxgi1_2/ns-dxgi1_2-dxgi_swap_chain_desc1)
  exige `FLIP_SEQUENTIAL` para `CreateSwapChainForComposition`.
- [DXGI flip model](https://learn.microsoft.com/en-us/windows/win32/direct3ddxgi/dxgi-flip-model)
  explica que los back buffers se comparten con DWM y se evita una copia extra.
- [Multiple Monitor System Metrics](https://learn.microsoft.com/en-us/windows/win32/gdi/multiple-monitor-system-metrics)
  exige tratar el escritorio virtual explícitamente, incluyendo coordenadas
  negativas y `EnumDisplayMonitors` para cada monitor.
- [High DPI Desktop Application Development](https://learn.microsoft.com/en-us/windows/win32/hidpi/high-dpi-desktop-application-development)
  recomienda Per-Monitor V2 y obliga a redimensionar/re-renderizar ante
  `WM_DPICHANGED`.

### Proyectos open source de referencia

- [Chromium `child_window_win.cc`](https://chromium.googlesource.com/chromium/src.git/+/refs/tags/133.0.6943.117/ui/gl/child_window_win.cc)
  crea superficies D3D con `WS_EX_LAYERED | WS_EX_TRANSPARENT |
  WS_EX_NOREDIRECTIONBITMAP` y explica que esa combinación hace transparente
  el input, mientras que `NOREDIRECTIONBITMAP` evita la bitmap innecesaria.
  Es la referencia más cercana al caso GPU sin input.
- [winpane design](https://github.com/peteretelej/winpane/blob/main/docs/design.md)
  propone superficies out-of-process, árbol retenido, thread propio del motor,
  separación `Hud`/`Panel` y una frontera JSON-RPC. Su [modelo de input](https://github.com/peteretelej/winpane/blob/main/docs/design/input.md)
  usa `HTTRANSPARENT` para HUD y un `HitTestMap` físico para paneles.
- [winpane rendering](https://github.com/peteretelej/winpane/blob/main/docs/design/rendering.md)
  confirma la cadena D3D11 hardware → swap chain de composición → alpha
  premultiplicado → DirectComposition, con dirty tracking y `Present(1)`.
- [procmod/overlay](https://github.com/procmod/overlay)
  mantiene click-through y no-activación como estado por defecto, y cambia a
  modo interactivo sólo de forma explícita. Es una referencia útil para el
  futuro estado `Panel`, no una dependencia que debamos descargar ahora.
- [ShaderGlass](https://github.com/votality/shaderglass)
  demuestra la utilidad de un overlay de shaders sobre múltiples aplicaciones,
  modo click-through y división de FPS para reducir carga. Su ruta de captura
  de escritorio es deliberadamente distinta de VIZZ y no debe introducirse en
  el renderer actual.
- [DisplayXR transparent overlay](https://github.com/DisplayXR/displayxr-leia-plugin/blob/main/docs/chroma-key-overlay.md)
  muestra otro diseño válido: DComp + flip-model + alpha premultiplicado. Su
  recomendación de no añadir estilos layered/transparent corresponde a su
  ruta de transparencia y hit-testing selectivo, por lo que no contradice el
  patrón Chromium elegido para un HUD completamente pasivo.

## Conclusiones técnicas

### 1. Input: dos productos, no uno

VIZZ necesita al menos dos clases de superficie:

| Superficie | Input | Implementación | Uso |
|---|---|---|---|
| `Hud` | 100% pasivo | layered + transparent + no redirection + no activate | foco, periferia, ritmo, guías |
| `Panel` | regiones explícitas | hit-test map físico y `MA_NOACTIVATE` | calibración, diagnóstico, controles |

No se debe hacer interactivo el HUD completo. Si se necesitan controles, deben
vivir en otra ventana o entrar en un modo `Panel` explícito. El renderer no
debe inferir que una marca visual puede recibir clic.

El cambio de `058` corrige la hipótesis original al añadir el patrón de
Chromium y conservar `WM_NCHITTEST`/`WM_MOUSEACTIVATE` como defensa de foco. La
prueba estática no equivale a prueba de usuario: el kill test pendiente es que
una aplicación de otro proceso conserve el foco y reciba un clic con el HUD
visible.

### 2. Composición: DirectComposition sí; bitmap CPU no

La ruta correcta para VIZZ es:

`plan semántico -> constant buffer -> shader D3D11 -> swap chain de composición
-> visual DirectComposition -> DWM`

El plan debe actualizarse sólo cuando cambia la representación. Una escena
quieta no debe presentar continuamente. `Present(1)` es razonable para no
introducir tearing, pero hay que medir la latencia y la cola de presents si el
gaze llega a 60 Hz o más. No usar `UpdateLayeredWindow`, capturas de pantalla
ni copias BGRA completas.

El estilo `WS_EX_LAYERED` se usa aquí para el contrato de input junto con
`WS_EX_NOREDIRECTIONBITMAP`; no se debe llamar a las APIs legacy de bitmap
layered sobre esta swap chain flip-model sin demostrar que no se rompe alpha o
visibilidad.

### 3. Monitores: el rectángulo virtual es una primera fase, no el modelo final

El rectángulo del escritorio virtual permite probar rápido, pero un rectángulo
único puede contener gaps, DPI distintos y áreas que no son ningún monitor.
Para la versión escalable:

1. Enumerar cada monitor con `EnumDisplayMonitors`/`GetMonitorInfo`.
2. Guardar `HMONITOR`, rectángulo físico, DPI, orientación y un `layout_id`.
3. Crear un surface por monitor o, como mínimo, enmascarar las regiones de gap.
4. Convertir coordenadas de gaze mediante `logical -> physical -> monitor`;
   nunca aplicar una escala global al escritorio.
5. Escuchar `WM_DISPLAYCHANGE`, `WM_DPICHANGED` y cambios de configuración;
   incrementar `layout_id` e invalidar la calibración cuando cambien posición,
   resolución, rotación o escala.

Un surface por monitor reduce el área de shader cuando las pantallas no son
coplanares o tienen formas de escritorio muy distintas. También hace posible
devolver `UNKNOWN` en un bezel/gap, en lugar de fabricar una coordenada.

### 4. GPU y temperatura: medir, no adivinar

El backend actual evita una copia de imagen y presenta sólo ante cambios, pero
eso no prueba una temperatura aceptable. La evaluación debe registrar, bajo el
mismo plan y duración:

- `presents`, cambios de plan, latencia y tiempo de CPU del proceso;
- uso del motor `GPU Engine 3D` de Windows;
- frecuencia de reloj/temperatura/energía si el driver lo expone;
- estado quieto, cursor/mirada estable y movimiento de 30/60 Hz;
- una comparación directa contra `057`.

Kill test: si con una escena estática el compositor presenta o el uso de GPU
sube de forma sostenida, la arquitectura retenida no está cumpliendo su
contrato. Si el gaze produce más cambios que el presupuesto visual, se debe
aplicar un filtro temporal/dirty threshold antes del renderer.

### 5. Privacidad: reducir superficie, no prometer invulnerabilidad

La separación correcta es cámara/observación local -> features mínimos -> plan
semántico -> renderer. `058` no abre cámara, sockets ni captura pantalla. El
renderer no debe recibir frames ni texto bruto.

`SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE)` puede excluir una ventana de
ciertas APIs públicas de captura, pero Microsoft advierte que no es DRM ni
protege contra una fotografía o un proceso privilegiado. Por eso es una capa
opcional de privacidad, nunca el mecanismo de seguridad principal.

## Decisión para FARMAXIA

Mantener `058` como renderer GPU-first, pero con esta corrección conceptual:

- `Hud` pasivo primero; no controles embebidos.
- `Panel` separado para calibración y diagnóstico.
- `059` debe ser un `MonitorSurfaceManager`, no otra animación visual.
- El adaptador Python sólo envía planes semánticos versionados por
  `layout_id`, nunca imágenes.
- La aceptación de input requiere una prueba cruzada con una aplicación
  inferior; si falla, no se sigue agregando visuales.
- Después del input, medir GPU/temperatura y recuperación de device antes de
  ampliar efectos.

## Qué queda desconocido

- Si el Windows/GPU concreto de desarrollo mantiene simultáneamente visibilidad
  DComp y click-through con esta combinación top-level.
- Si `Present(1)` introduce una espera o cola excesiva con cambios de gaze
  frecuentes.
- Si el rectángulo virtual actual cubre correctamente la configuración Barrier
  y los DPI de ambos equipos/monitores.
- Cómo se comportan fullscreen exclusivo, DRM y escritorios virtuales.

## Kill tests obligatorios antes de seguir

1. HUD visible + editor inferior: clic y foco llegan al editor.
2. HUD visible + teclado: escritura llega al editor; VIZZ no recibe teclas.
3. Escena quieta: `presents` no crece continuamente.
4. Cambio de monitor/DPI: cambia `layout_id` y no se reutiliza calibración vieja.
5. Renderer sin cámara/captura/red: el source y la ejecución lo demuestran.
6. Si se crea un Panel: sólo sus regiones declaradas interceptan input.

## Veredicto

La dirección técnica es sólida, pero la evidencia actual permite decir
“arquitectura respaldada y compilada”, no todavía “click-through validado en
esta máquina”. La próxima acción correcta es cerrar esos kill tests en una sola
ejecución controlada y recién después implementar superficies por monitor.
