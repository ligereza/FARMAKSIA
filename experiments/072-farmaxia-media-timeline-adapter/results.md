# Resultados 072 — adapter de timeline media

**Fecha de ejecución:** 2026-08-27  
**Estado:** `MEDIA_TIMELINE_ADAPTER_VERIFIED`

## Evidencia obtenida

- una superficie audiovisual sintética reutilizó el núcleo común
  `research/tools/cloudevents_contract.py`;
- 4 entregas se redujeron a 3 eventos únicos y 1 duplicado, conservando los
  sobres originales;
- tres órdenes de llegada produjeron el mismo orden canónico:
  `ev-asset-ingested`, `ev-timeline-published`, `ev-marker-declared`;
- el asset H.264 sintético usa un timebase exacto de `24/1`, un rango fuente de
  frames `48..143` y un marcador en el frame 60;
- el oráculo separó el reloj de eventos del reloj de media y calculó el
  marcador en el frame editorial 12, exactamente `1/2` segundo;
- el codec, el rango fuente, la timeline, la procedencia, el permiso de preview
  y la sincronía audio/video pasaron verificación independiente;
- la acción quedó en `DRY_RUN_ONLY`, requirió confirmación y no decodificó,
  exportó ni escribió media;
- los 10 kill tests bloquearon evento faltante, rango inválido, codec no
  soportado, drift audio/video, timebase cero, marcador inconsistente, permiso
  ausente, exportación, hash viejo y procedencia ausente.

## Interpretación

Media sí introduce una diferencia semántica material: un evento tiene un reloj
de entrega, mientras una timeline tiene un reloj de frames y rangos de fuente.
Además, una reproducción puede ser incorrecta por codec o sincronía aunque el
evento haya llegado y su procedencia sea válida.

La diferencia se encapsuló en el adapter 072. No se creó otro ledger, otro
replay ni otro sistema de permisos. El resultado demuestra reutilización en un
fixture sintético, no interoperabilidad con un editor, navegador, codec o
player reales.

## Seguridad y alcance

No hubo red, descargas, datos humanos, cámara, decodificación, ejecución
externa ni escritura. Quedan fuera VFR, drop-frame, keyframes reales,
transiciones, efectos, time-warp, derechos de reproducción y clocks de
hardware.

## Siguiente objetivo

El experimento 073 ya comparó este contrato con representaciones OTIO-style y
ffprobe-style: la primera es compatible; la segunda necesita un sidecar para
completar la semántica editorial. El siguiente avance es componer ese sidecar
por hash/versiones, manteniendo ambas fuentes read-only.
