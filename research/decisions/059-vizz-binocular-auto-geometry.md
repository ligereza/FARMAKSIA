# ADR 059 — VIZZ: auto-geometría binocular con escala EDID opcional

Fecha: 2026-08-25  
Estado: contrato sintético aceptado para la siguiente validación

## Decisión

La ruta principal de investigación de VIZZ será una auto-geometría binocular
activa:

1. Windows identifica cada monitor y entrega sus coordenadas lógicas.
2. EDID aporta ancho/alto declarados cuando hay checksum válido y consenso.
3. VIZZ presenta targets conocidos en nueve posiciones por monitor.
4. Un proveedor ocular entrega dos orígenes y dos direcciones de mirada.
5. Cada fijación se reconstruye como el punto medio de los rayos más cercanos.
6. Los puntos se ajustan a un plano por monitor.
7. Si EDID es consistente, el fit obtiene escala métrica; sin EDID queda en
   unidades relativas y nunca se presenta como metros.

La cabeza puede moverse durante la captura. La pose de cabeza debe llevar los
rayos a un marco común; el movimiento sirve como excitación de paralaje y el
plano del monitor debe permanecer estable.

## Base de research

Zhu y Ji describen gaze 3D bajo movimiento natural de cabeza mediante un modelo
de los ojos y la intersección del gaze con el objeto observado
([PubMed](https://pubmed.ncbi.nlm.nih.gov/18075041/)). Stefanov estudia gaze con
una webcam ordinaria bajo movimiento natural y reporta que la reconstrucción
3D está limitada por la cámara monocular, por lo que la salida debe ser
conservadora ([arXiv](https://arxiv.org/abs/1803.11088)). Estudios de gaze
binocular muestran que la profundidad por vergencia es útil pero sensible al
ruido de las direcciones oculares ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11062346/)).

## Evidencia sintética

`experiments/052-vizz-binocular-auto-geometry/` recuperó los dos planos del
fixture con nueve targets cada uno y recuperó las dimensiones EDID `0.38×0.21`
metros y `0.70×0.39` metros. Al quitar EDID, el mismo algoritmo devolvió
`VALID_RELATIVE` y dejó `width_m`/`height_m` en `null`. Los rayos paralelos y
los targets insuficientes devolvieron `UNKNOWN`.

Esto valida la arquitectura algebraica, no la webcam ni la mirada humana.

## Requisitos del proveedor real

- centro de cada ojo por frame;
- dirección visual de cada ojo en un marco común;
- pose de cabeza y timestamps;
- confianza y separación entre rayos;
- estado de parpadeo/oclusión;
- no usar el mouse como etiqueta.

Si el proveedor sólo ofrece ángulos 2D o features normalizadas del runtime 033,
049 debe seguir devolviendo `UNKNOWN: missing_world_geometry`.

## Kill tests

1. Rayos paralelos o no convergentes: `UNKNOWN`.
2. Pocos targets o geometría colineal: `UNKNOWN`.
3. Escala EDID contradictoria: `UNKNOWN`.
4. Sin EDID: nunca escribir metros.
5. Movimiento de cabeza: no mover el plano estacionario.
6. Cambiar layout o monitor: invalidar la versión correspondiente.

## Próximo paso

Adaptar la salida del proveedor GPU existente a dos rayos oculares con pose y
timestamps, sin abrir todavía una interfaz de producción. La primera captura
real debe ser una prueba de calidad/UNKNOWN, no una promesa de precisión ni
una modificación del contenido de pantalla.
