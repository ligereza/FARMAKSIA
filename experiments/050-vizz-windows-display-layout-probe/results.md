# Resultados — Experimento 050

Estado observado: `VIZZ_050_WINDOWS_DISPLAY_LAYOUT_PROBE_VALID`.

Ejecución en el host Windows del laboratorio, 2026-08-25:

- layout virtual: `(0, 0, 3926, 960)`;
- `DISPLAY1` primario: `(0, 0, 1707, 960)`, área de trabajo hasta `y=912`, DPI efectivo `96×96`, orientación `0`;
- `DISPLAY2` secundario: `(2560, 0, 3926, 768)`, DPI efectivo `96×96`, orientación `UNKNOWN` porque Windows no devolvió un valor válido;
- EDID válido y concordante: `DISPLAY1=38×21 cm` (3 candidatos iguales), `DISPLAY2=70×39 cm` (1 candidato);
- ambos monitores fueron enumerados sin cámara, red ni mutación del contenido;
- `layout_version=0561e7fb0c475e42`;
- `physical_geometry_status=PARTIAL_EDID_ONLY`: hay tamaño físico declarado,
  pero aún no hay plano, pose ni distancia ojo-pantalla.

La separación entre `DISPLAY1` y `DISPLAY2` deja una región lógica sin monitor
entre `x=1707` y `x=2560`; esa región no debe convertirse silenciosamente en
un punto válido de ningún monitor.

La salida debe separar explícitamente:

- layout lógico del escritorio virtual;
- identidad y área de trabajo de cada monitor;
- DPI/orientación sólo si la API los devuelve;
- dimensiones físicas EDID como evidencia parcial;
- geometría física 3D, que debe permanecer `UNKNOWN` en este experimento.

No se considerará evidencia de distancia ojo-pantalla, precisión de gaze,
comodidad o beneficio perceptual.
