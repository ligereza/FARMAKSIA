# Experimento 051 — VIZZ: contrato de calibración física por monitor

## Objetivo

Convertir medidas físicas y una pose validada de cada pantalla en planos 3D
compatibles con el contrato geométrico 046. El experimento no abre cámara, no
modifica el escritorio, no usa red y no afirma que una webcam ya pueda medir
distancias.

## Contrato de entrada

Cada monitor necesita:

- `monitor_id` y `logical_rect` del snapshot 050;
- `width_m` y `height_m` medidos o respaldados por una referencia métrica;
- `origin`, el centro del plano en un marco mundial común;
- `horizontal_axis` y `vertical_axis`, ortogonales y normalizados por el
  contrato;
- `scale_source` y `pose_source` auditables;
- `measurement_id` para no mezclar configuraciones.

El origen y los ejes no se deducen de la resolución. En una futura fase,
`pose_source=marker_pose` podrá venir de OpenCV `solvePnP` con AprilTags o
ChArUco; en la primera prueba se puede usar `manual_measurement`.

## Targets

Se generan nueve targets por monitor en `(u,v) = {0.10, 0.50, 0.90}²`. El
target presentado por VIZZ es la etiqueta de referencia; el mouse se conserva
como contexto y nunca como verdad ocular.

## Ejecución

```powershell
.\.venv\Scripts\python.exe experiments/051-vizz-physical-monitor-calibration/run_experiment.py
.\.venv\Scripts\python.exe experiments/051-vizz-physical-monitor-calibration/run_contract_test.py
```

## Kill tests

- Una resolución o un DPI no pueden convertirse en metros.
- Un monitor sin tamaño físico o sin pose debe fallar, no producir un plano.
- Rectángulos lógicos cambiados deben quedar visibles para invalidar la
  calibración.
- Dos monitores deben conservar sus propios planos y sus propios tamaños.
- El hueco entre monitores no recibe una etiqueta silenciosa.
- Los targets no pueden depender del cursor.

## Qué falta para una captura real

1. Ejecutar 050 y guardar el snapshot del layout.
2. Medir ancho y alto de cada pantalla.
3. Elegir una referencia de pose: medición manual o cuatro+ marcadores
   temporales visibles para una cámara de escena.
4. Calibrar los intrínsecos/distorsión de esa cámara.
5. Verificar residual y estabilidad en tres capturas.
6. Conectar sólo un proveedor de ojos/cabeza que entregue geometría y
   timestamps auditables.

Una TV curva no debe entrar como plano sin una auditoría; su modelo futuro
será cilíndrico o una colección de planos.
