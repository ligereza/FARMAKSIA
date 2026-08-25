# ADR 058 — VIZZ: gate de research antes de la calibración física

Fecha: 2026-08-25  
Estado: research completado; implementación 051 autorizada sólo como contrato

## Decisión

La calibración física de VIZZ tendrá dos capas independientes:

1. **Escena:** tamaño y pose de cada monitor, con una referencia métrica y
   correspondencias visibles.
2. **Percepción:** centros oculares, dirección de mirada y pose de cabeza por
   frame.

El layout lógico de Windows será sólo identidad/rectángulos/versionado. No se
usará para fabricar metros ni planos 3D.

## Por qué

OpenCV documenta que `solvePnP` obtiene la pose a partir de puntos 3D
conocidos, observaciones 2D e intrínsecos/distorsión de cámara. Pupil Labs
resuelve una versión operativa del problema localizando superficies mediante
AprilTags. MediaPipe Face Geometry ofrece una representación facial métrica
basada en un modelo canónico, mientras que OpenFace exige parámetros de cámara
para sus salidas 3D de pose y gaze. Estas fuentes convergen en la necesidad de
separar escala, cámara, superficie y percepción.

## Protocolo decidido

### Fase A — contrato sin cámara

Implementar 051 para aceptar exclusivamente una especificación física:

- monitor lógico de 050;
- ancho y alto físicos;
- centro/origen del plano;
- ejes ortogonales;
- fuente de la medida;
- versión y residual de validación.

El contrato debe poder resolver rayos sintéticos contra uno o varios planos y
debe rechazar configuraciones que sólo contengan píxeles.

### Fase B — validación instrumental

Usar temporalmente cuatro o más AprilTags/ChArUco por monitor, con tamaño
conocido, cámara calibrada y monitor fijo. Registrar pose, residual, visibilidad
y pérdida de correspondencias. La cámara no debe mover la pantalla ni cambiar
la interfaz normal de trabajo.

### Fase C — percepción binocular

Conectar sólo un proveedor que exponga centros oculares, gaze y pose con
timestamps/confianza. 049 continuará devolviendo `UNKNOWN` si recibe sólo
features de imagen del runtime legado.

### Fase D — retiro de marcadores

Comparar la pose por marcadores con esquinas/bezel o una referencia de
superficie sin marcadores. No retirar marcadores por estética hasta comprobar
el error held-out y la estabilidad ante movimiento de cabeza.

## No se aceptará

- distancia en metros derivada sólo de resolución, DPI o `depth mask`;
- homografía fija presentada como solución 3D multimonitor;
- precisión de gaze inferida desde el mouse;
- una pantalla curva representada como plana sin auditoría de residuales;
- una calibración que funcione sólo con cabeza inmóvil si el objetivo es uso
  natural.

## Próximo bloque

Implementar 051 como contrato sintético y preparar un archivo de configuración
para que el usuario introduzca las medidas físicas. La captura con cámara se
hará después de inspeccionar el proveedor de landmarks/gaze y confirmar sus
intrínsecos, escala y licencia.
