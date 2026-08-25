# Experimento 052 — VIZZ: auto-geometría binocular

## Idea

La pantalla se convierte en un estímulo geométrico activo. VIZZ presenta
targets conocidos en cada monitor; el proveedor ocular entrega dos centros y
dos direcciones de mirada; el punto de fijación se reconstruye como el punto
medio de los rayos más cercanos. Los targets reconstruidos se ajustan a un
plano por monitor.

```text
ray_L = eye_L + lambda * gaze_L
ray_R = eye_R + mu     * gaze_R

fixation = midpoint(closest(ray_L, ray_R))
screen_plane = fit(fixation ~ target_u + target_v)
```

El movimiento natural de cabeza no se elimina: excita el paralaje. Si la pose
facial transforma cada frame al mismo marco mundial, el plano debe permanecer
estable mientras cambia el origen de los rayos.

## Escala

Sin una referencia métrica, el resultado es `VALID_RELATIVE` en unidades del
marco ocular. Con el ancho/alto EDID concordante del experimento 050, el ajuste
puede resolver un factor de escala y devolver `VALID_METRIC`. Esto no significa
que el EDID haya entregado la pose: sólo aporta el tamaño del rectángulo.

Si los anchos y altos no producen el mismo factor de escala, el contrato
devuelve `UNKNOWN: edid_aspect_scale_conflict`.

## Por qué es la ruta adecuada para VIZZ

La literatura sobre gaze 3D y movimiento natural de cabeza usa rayos oculares,
compensación de cabeza y la intersección con el objeto observado. La auto-
geometría de esta prueba adapta esa idea a monitores conocidos por Windows,
sin usar el mouse como verdad y sin exigir una huincha en la primera fase.

Referencias: [Zhu y Ji — gaze 3D bajo movimiento natural](https://pubmed.ncbi.nlm.nih.gov/18075041/),
[Stefanov — webcam gaze bajo movimiento natural](https://arxiv.org/abs/1803.11088),
[estimación de profundidad por vergencia binocular](https://pmc.ncbi.nlm.nih.gov/articles/PMC11062346/).

## Ejecutar

```powershell
.\.venv\Scripts\python.exe experiments/052-vizz-binocular-auto-geometry/run_experiment.py
.\.venv\Scripts\python.exe experiments/052-vizz-binocular-auto-geometry/run_contract_test.py
```

## Kill tests

- Rayos paralelos o que no convergen producen `UNKNOWN`.
- Pocos targets o geometría colineal producen `UNKNOWN`.
- Sin EDID, el sistema no presenta una fit relativa como metros.
- Movimiento de cabeza cambia los rayos, no el plano estacionario.
- El mouse nunca participa en la reconstrucción.
- La prueba no abre cámara ni modifica el contenido de pantalla.

## Límite

Es una prueba sintética. El runtime real todavía debe entregar centros oculares
y gaze 3D con timestamps, confianza, pose de cabeza y una escala compatible.
La vergencia de una webcam puede ser ruidosa; el residual y la separación de
rayos deben gobernar `UNKNOWN`, no una animación visual optimista.
