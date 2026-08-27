# Experimento 072 — adapter de timeline media

Este experimento comprueba si una superficie audiovisual exige algo que el
núcleo genérico de FARMAKSIA no expresa por sí solo. La respuesta provisional
es sí, pero la diferencia es acotada: media tiene un reloj editorial propio,
rangos racionales de frames, composición de tracks, capacidad de codec y
sincronía audio/video.

La analogía es simple: el sobre CloudEvents dice **cuándo llegó la noticia**;
la timeline dice **en qué instante del material debe aparecer el frame**. Son
dos relojes y mezclarlos produciría una reproducción incorrecta aunque el
evento se hubiera verificado.

El fixture usa un asset sintético H.264, una timeline de 24 fps, un clip que
empieza en el frame fuente 48 y un marcador en el frame 60. El adapter calcula
que el marcador aparece en el frame 12, es decir `1/2` segundo dentro del clip,
manteniendo el cálculo como fracción exacta. Audio y video parten alineados.

## Qué se reutiliza

- sobre CloudEvents, identidad `source + id`, deduplicación y orden canónico;
- procedencia de claims y referencias a la fuente;
- replay con tres órdenes de entrega;
- verificación independiente y permiso de destino;
- acción reversible `DRY_RUN_ONLY` con confirmación.

## Qué es específico de media

- separación entre reloj de eventos y reloj de media;
- `timebase` racional, `source_range` y posición editorial;
- comprobación de que el rango cabe dentro del asset;
- codec disponible y sincronía audio/video.

No se decodifica ningún archivo, no se abre un player real y no se descargan
OpenTimelineIO, FFmpeg, MLT ni codecs. Las referencias se usan como guía de
contrato, no como dependencias del laboratorio.

## Reproducir

```powershell
python experiments/072-farmaxia-media-timeline-adapter/run_experiment.py
python experiments/072-farmaxia-media-timeline-adapter/run_contract_test.py
python experiments/072-farmaxia-media-timeline-adapter/run_kill_test.py
```

El resultado no demuestra interoperabilidad con un editor, navegador o codec
real. Quedan fuera derechos de reproducción, keyframes reales, VFR, drop-frame,
transiciones, efectos, decodificación y sincronización con hardware.
