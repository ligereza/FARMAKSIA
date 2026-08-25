# Experimento 049 — VIZZ: puente cerrado del runtime a geometría física

## Objetivo

Impedir que las seis features legacy o los ángulos de gaze en espacio de
imagen se conviertan directamente en una coordenada de monitor. El puente sólo
acepta la salida nueva cuando recibe:

- centros de ambos ojos en coordenadas mundiales;
- dirección de mirada mundial;
- layout versionado de monitores;
- calidad e incertidumbre.

Sin esos datos devuelve `UNKNOWN: missing_world_geometry` y mantiene cerrado el
mapper físico. Esto es intencional: la falta de una cámara calibrada no se
resuelve inventando una transformación.

## Ejecutar

```powershell
.\.venv\Scripts\python.exe experiments/049-vizz-runtime-geometry-bridge/run_experiment.py
.\.venv\Scripts\python.exe experiments/049-vizz-runtime-geometry-bridge/run_contract_test.py
```

## Límite

El proveedor de centros oculares y rayo mundial aún no está implementado. El
runtime 033 puede seguir usándose como diagnóstico legacy, pero sus coordenadas
no alimentan la política VIZZ de geometría hasta que este puente reciba la
geometría completa.
