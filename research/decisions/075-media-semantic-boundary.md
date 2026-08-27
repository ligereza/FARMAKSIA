# Decisión 075 — frontera semántica de media

**Estado:** adoptada para auditoría local  
**Fecha:** 2026-08-27

## Decisión

FARMAKSIA tratará media como un adapter sobre el núcleo común, no como un
segundo sistema de eventos. La nueva semántica mínima es:

1. reloj de eventos separado del reloj editorial/de reproducción;
2. `value/rate` exacto para timebase, rangos y posiciones de frames;
3. relación entre `available_range` del asset y `source_range` del clip;
4. composición de tracks y sincronía audio/video;
5. capacidad de codec y permiso de preview como precondiciones verificables.

El contrato se probó en [experimento 072](../../experiments/072-farmaxia-media-timeline-adapter/README.md)
y su portabilidad se comparó en el [experimento 073](../../experiments/073-farmaxia-media-representation-bridge/README.md).
La operación sólo previsualiza y requiere confirmación. No se instala ningún
framework ni se decodifica media.

## Por qué no basta el evento genérico

El evento puede decir que una timeline fue publicada a cierta hora, pero no
puede sustituir la posición de un frame dentro de la timeline. Confundir ambos
relojes desplaza marcadores y puede romper sincronía aun cuando el replay de
eventos sea perfecto.

La auditoría adopta tres referencias consolidadas como guía, sin convertirlas
en dependencias:

- [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/index.rst)
  separa datos editoriales de los archivos audiovisuales, y su documentación
  describe clips, tracks, transiciones, `available_range` y `source_range`;
- [FFmpeg](https://ffmpeg.org/ffmpeg.html) documenta que timestamps y keyframes
  se resuelven según el timebase del encoder, por lo que un segundo decimal no
  siempre identifica un frame físico único;
- [WebCodecs](https://www.w3.org/TR/webcodecs/) conserva `timestamp` y
  `duration` al producir frames, haciendo explícita la semántica temporal de
  reproducción.

La comparación 073 mostró que una representación de streams estilo `ffprobe`
no debe ascender silenciosamente a timeline editorial: puede compartir
identidad, hash, codec y timebase con OTIO-style, pero necesita un sidecar para
rangos de clips y marcadores. El experimento 074 verificó la composición
read-only de ese sidecar por `asset_ref`, hash y versión, manteniendo
`PARTIAL_UNKNOWN` hasta que las tres llaves y los rangos exactos coinciden.

## Límites

El fixture no prueba VFR, drop-frame, keyframes, time-warp, transiciones,
efectos, derechos, hardware clocks ni compatibilidad con una API real. Una
fuente real debe seguir siendo read-only hasta contar con verificación
independiente, permisos y una política de exportación explícita.

## Regla de crecimiento

No se añadirá un renderer media completo. Primero se compondrán fuentes
read-only por hash/versiones; sólo un campo cuya semántica no pueda preservarse
con esa composición justificará una extensión. Dos sidecars incompatibles no se
resolverán por orden de llegada: deben conservarse y producir `CONFLICT` o
`UNKNOWN`.
