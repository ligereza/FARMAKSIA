# VIZZ 035 — normalización eye-centric

Este experimento implementa la primera capa geométrica independiente del
mapper de pantalla. Toma puntos de los dos ojos, calcula el punto medio y la
distancia interocular, elimina traslación/escala/roll en el plano de imagen y
devuelve una representación común.

No pretende corregir por sí sola un giro 3D de la cabeza. El yaw/pitch facial
debe estimarse por separado y, si no es identificable, la salida debe ser
`UNKNOWN`. El experimento usa sólo nubes sintéticas: no abre cámara, no guarda
frames y no recoge datos humanos.

## Ejecución

```powershell
.\.venv\Scripts\python.exe experiments/035-vizz-eye-centric-normalization/run_experiment.py
```

El test aplica escala, traslación y roll distintos a la misma configuración de
ojos. También comprueba que dos ojos colapsados se rechacen en vez de generar
una escala infinita.

Esta capa aún no reemplaza las seis features del runtime ni invalida el perfil
actual. Primero debe conectarse a landmarks/iris reales, añadirse pose facial y
compararse contra `M0` con sesiones completas held-out.
