# VIZZ 053 — adaptador de dos rayos del proveedor GPU

Este incremento adopta la primera salida explícita de binocularidad del
proveedor CUDA real de `033`. Antes, el runtime retenía los ángulos por ojo
pero exponía principalmente su promedio (`binocular_gaze_deg`). Ahora cada
muestra puede conservar dos orígenes y dos direcciones en un marco relativo
versionado: `camera_proxy_normalized_v1`.

## Qué demuestra

- se conserva la separación entre ojo izquierdo y derecho;
- se puede propagar la separación interocular como señal de escala relativa;
- una discrepancia binocular excesiva se rechaza como `UNKNOWN`;
- la salida no se presenta como metros ni como pose 3-D del mundo;
- el contrato no abre cámara, no usa red, no muta pantalla y no guarda vídeo.

La transformación usa una convención explícita `x=derecha, y=abajo,
z=adelante` para los ángulos del tracker. Los centros oculares se normalizan
por el tamaño de imagen y quedan en un plano proxy; por ello esta etapa puede
alimentar geometría relativa, pero todavía necesita intrínsecos, profundidad
ocular y pose de cabeza independiente para convertirse en rayos métricos.

## Qué no demuestra

No valida precisión de webcam, estimación de distancia, selección real de
monitor ni reducción de fatiga. Tampoco convierte el cursor en ground truth.
La siguiente etapa será una captura pasiva de calidad usando el proveedor CUDA
real. No exige recalibrar ni modificar el contenido de pantalla.

## Ejecución

```powershell
python experiments/053-vizz-gpu-binocular-ray-adapter/run_experiment.py
python experiments/053-vizz-gpu-binocular-ray-adapter/run_contract_test.py
```

Cuando quieras hacer la primera captura real, desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe experiments/053-vizz-gpu-binocular-ray-adapter/run_quality_capture.py --seconds 60 --pointer
```

Durante 60 segundos no aparecerá una ventana VIZZ ni un preview. Puedes
trabajar con movimientos naturales; no necesitas mirar puntos ni recalibrar.
`Ctrl+C` termina antes. El archivo `.vizz-binocular-quality.jsonl` guarda sólo
resúmenes temporales, rayos relativos, calidad, pose proxy y cursor opcional.

## Kill tests

- discrepancia binocular mayor a 45 grados -> `UNKNOWN`;
- centros coincidentes -> `UNKNOWN`;
- valores no finitos -> `UNKNOWN`;
- una salida relativa nunca se etiqueta como métrica;
- no hay cámara, red, cursor como verdad ni contenido de pantalla.
