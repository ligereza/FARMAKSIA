# Experimento 050 — VIZZ: layout de monitores de Windows

## Objetivo

Obtener de forma reproducible la disposición lógica de los monitores activos
en Windows para que VIZZ pueda identificar un monitor del escritorio virtual.
El probe usa sólo APIs de lectura: no abre cámara, no captura vídeo, no
modifica ventanas, no cambia el contenido de pantalla y no usa red.

## Qué registra

- nombre estable del dispositivo (`\\.\\DISPLAYn`) y, cuando Windows lo
  entrega, descripción/identificador del adaptador;
- `monitor_rect` y `work_rect` en coordenadas del escritorio virtual de
  Windows, incluyendo coordenadas negativas de monitores a la izquierda o
  encima del primario;
- monitor primario;
- DPI efectivo cuando `Shcore!GetDpiForMonitor` está disponible;
- orientación cuando `EnumDisplaySettingsExW` la devuelve;
- dimensiones declaradas por EDID cuando sus bloques tienen checksum válido y
  todos los candidatos del fabricante coinciden;
- un `layout_version` determinista para invalidar calibraciones si cambia el
  layout lógico.

## Límite esencial

Un rectángulo de píxeles y un DPI no indican por sí solos el tamaño físico, la
distancia a los ojos ni la orientación 3D del plano. El EDID puede aportar un
tamaño declarado por el fabricante; el probe lo marca como
`PARTIAL_EDID_ONLY` y conserva `physical_plane: null`. Si hay candidatos EDID
contradictorios, también queda `UNKNOWN`.

La siguiente calibración debe aportar tamaño físico medido y pose relativa
cámara/ojos-monitor. Sin ese dato, 046/049 no pueden convertir un rayo ocular
en distancia o intersección física de forma honesta.

## Ejecutar

```powershell
.\.venv\Scripts\python.exe experiments/050-vizz-windows-display-layout-probe/run_experiment.py
.\.venv\Scripts\python.exe experiments/050-vizz-windows-display-layout-probe/run_contract_test.py
```

## Kill tests

- En un sistema Windows sin monitores enumerables, el resultado es `UNKNOWN`;
  no se inventa un monitor.
- El probe no puede marcar geometría física como válida a partir de píxeles.
- El layout lógico se versiona; una calibración con otra versión debe quedar
  obsoleta.
- Un monitor secundario no se proyecta a una escala global del primario.
- Las coordenadas negativas se conservan, no se recortan al origen `(0, 0)`.
- Un tamaño EDID no se eleva a pose física sin validarlo contra cámara y ojos.

## Estado de evidencia

Es una observación instrumental del sistema, no una medición de mirada ni una
prueba de reducción de fatiga. La geometría física y cualquier efecto visual
siguen siendo incompletas hasta diseñar y validar la calibración correspondiente.
