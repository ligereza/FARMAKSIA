# Investigación: grandMA3 onPC y Avolites Titan como superficies traducibles

Fecha de corte: 2026-08-27.

## Pregunta

¿Puede FARMAKSIA hacer que una persona familiarizada con Avolites opere o
aprenda grandMA mediante una transformación visual y semántica, sin convertir
los dos motores de iluminación en un único software ni escribir un showfile
en nombre del usuario?

## Fuentes primarias consultadas

- [MA Lighting: descargas de grandMA3](https://www.malighting.com/downloads/products/grandma3/).
- [MA Lighting: grandMA3 onPC](https://www.malighting.com/special/grandma3-onpc/).
- [MA Lighting: instalación de grandMA3 onPC en Windows](https://help.malighting.com/grandMA3/2.3/HTML/onpc_windows_installation.html).
- [MA Lighting: cues y sequences](https://help.malighting.com/grandMA3/2.4/HTML/cue_sequence.html).
- [MA Lighting: almacenar cues y usar executors](https://help.malighting.com/grandMA3/2.4/HTML/qsg_cue_executor.html).
- [MA Lighting: presets](https://help.malighting.com/grandMA3/2.4/HTML/presets.html).
- [Avolites: Titan PC Suite](https://www.avolites.com/support/titan-pc-suite/).
- [Avolites: manual de Titan](https://manual.avolites.com/docs/).
- [Avolites: ventanas de workspace](https://manual.avolites.com/docs/titan-basics/workspace-windows/).
- [Avolites: referencia de botones](https://manual.avolites.com/docs/titan-reference/button-reference/).
- [Avolites: funciones de Titan](https://www.avolites.com/support/titan-features/).

La versión de referencia de MA disponible durante esta auditoría es
grandMA3 onPC para Windows 2.4.2.2. La página de MA ofrece el software onPC
gratuitamente para preprogramación y visualización; los parámetros y la salida
física dependen de productos/hardware compatibles. No se debe confundir la
descarga gratuita con una licencia para controlar hardware de iluminación.

En esta máquina se encontró Avolites Titan y Titan Simulator 19.1.205.5 bajo
`C:\Program Files\Avolites`. El paquete de grandMA3 se descargó únicamente
desde MA Lighting y permanece fuera del repositorio:

```text
archivo: grandMA3_onPC_win_v2.4.2.2.zip
tamaño: 483269901 bytes
sha256: 91D16E94B636BC20DE2969AFA5AD2503A0F53AF0083D64ED156D912B995653E0
uso: observación offline; no DMX ni fixtures reales
```

## Hallazgo central

La unidad correcta de traducción no es el botón ni la palabra. Es la tarea
del operador y el objeto que la tarea modifica. La capa debe conservar:

```text
selección de fixtures → valores/atributos → objeto reutilizable →
transición temporal → salida observable
```

Una captura de pantalla puede reordenarse; la semántica no puede inventarse.
Por eso la primera versión será un adaptador visual reversible y de solo
lectura. La ejecución o el mapeo de inputs quedan para otra compuerta.

## Correspondencias iniciales

| Concepto canónico | grandMA3 | Titan | Estado |
|---|---|---|---|
| Selección de fixtures | Fixture/Group/Layout selection | Fixtures/Groups | compatible como intención |
| Estado de edición | Programmer | Programmer | compatible como intención, revisar prioridad |
| Valor reutilizable | Preset | Palette | analogía fuerte, no identidad exacta |
| Escena temporal | Cue | Cue | compatible como resultado, distinta organización |
| Contenedor de cues | Sequence | Cue List | analogía operativa fuerte |
| Control de reproducción | Executor que controla una sequence | Playback | analogía operativa fuerte |
| Organización espacial | View, Pool, Layout | Workspace, workspace layout | compatible como organización visual |
| Vista de salida | Fixture/Tracking/Sequence sheet | Attribute/Cue List/Visualiser | compatible como observables distintos |
| Visualización | grandMA3 visualizer | Capture Visualiser | compatible como previsualización |

Estas correspondencias no autorizan un traductor automático. En grandMA3, las
cues viven en sequences y los executors son handles que controlan sequences;
en Titan, los playbacks y cue lists tienen otra organización y otras reglas de
programación. La tabla expresa una intención de tarea, no una conversión de
IDs.

## Zonas sin equivalencia 1:1

Recipes, MAgic/MAtricks, phasers, worlds, prioridades y capas de timing de
grandMA3 pueden afectar el resultado sin que exista un botón o contenedor
equivalente en Titan. Titan tiene palettes, masks, curvas, playback groups,
macros, visualiser y otras construcciones propias. Cuando el adaptador no pueda
probar equivalencia debe mostrar `PARTIAL`, `UNKNOWN` o `UNSUPPORTED`; nunca
renombrar una función compleja como si fuera otra.

## Herramientas que sí se adoptan para este caso

La base técnica ya validada en FARMAKSIA es suficiente:

1. **Windows Graphics Capture** para un preview de la ventana elegida por el
   usuario.
2. **UI Automation/pywinauto** para consultar nombres, roles y rectángulos de
   controles cuando la aplicación los exponga.
3. **Renderer de proxy reversible** para reordenar regiones y aplicar una
   leyenda Avolites sin tocar el proceso de grandMA.
4. **Contrato declarativo** para describir una región como `source_role`,
   `canonical_task`, `target_vocabulary`, `confidence` y `reversible_transform`.

No se adopta OCR, inyección de teclado/mouse, scraping de memoria, red MA-Net,
salida DMX ni modificación de showfiles en la primera etapa. Son superficies
de riesgo y además impedirían saber si la traducción visual realmente ayuda.

## Próximo experimento de alto valor

Construir un `LightingSurfaceContract` para cinco tareas comunes:

1. seleccionar un grupo de fixtures;
2. aplicar un valor de posición, color o intensidad;
3. guardar o recuperar ese valor reutilizable;
4. registrar/avanzar una cue o cue list;
5. identificar qué playback/executor está actuando.

El contrato se probará primero con fixtures sintéticos y ventanas escogidas
explícitamente. Después se observarán grandMA3 onPC y Titan Simulator en modo
offline. La salida inicial será un preview que muestre, junto a cada región,
la tarea canónica y el término familiar de Titan. No activará botones ni
alterará el show.

## Criterio de éxito y kill tests

El caso continúa sólo si, en ambas superficies, el adaptador puede señalar la
misma tarea canónica, conservar la relación espacial de la fuente y devolver
la transformación inversa sin introducir acciones. Debe además registrar
`UNKNOWN` cuando una región no sea identificable.

Se mata o se reduce el alcance si ocurre cualquiera de estos casos:

- la equivalencia depende solo de texto parecido y no del estado observable;
- el mismo término de Titan representa estados distintos en grandMA3;
- la reordenación bloquea la ventana fuente o roba input sin consentimiento;
- una función compleja se presenta como equivalente aunque sólo sea parcial;
- el preview necesita DMX, red o modificación del show para demostrar algo;
- la versión real resulta ser grandMA2 y el contrato se estaba construyendo
  para grandMA3 sin una decisión explícita.

## Desconocidos que quedan abiertos

- El usuario puede referirse a grandMA2 o grandMA3; se toma grandMA3 como
  referencia provisional porque es la versión oficial actual descargada.
- No se ha observado todavía la UI real de grandMA3 onPC ni se ha comparado
  contra una sesión viva de Titan Simulator.
- No sabemos qué subconjunto de controles expone cada aplicación por UIA.
- No sabemos si el beneficio buscado es entrenamiento, operación asistida o
  una piel visual permanente; el primer slice sirve a los tres sin ejecutar.
