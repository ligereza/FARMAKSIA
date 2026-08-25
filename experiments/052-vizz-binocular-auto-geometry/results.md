# Resultados — Experimento 052

Estado observado: `VIZZ_052_BINOCULAR_AUTO_GEOMETRY_CONTRACT_VALID`.

Debe demostrar:

- ajuste de dos planos a 18 fijaciones binoculares sintéticas;
- recuperación de `0.38×0.21 m` y `0.70×0.39 m` usando escala EDID;
- fit relativo válido cuando EDID no se entrega, sin inventar metros;
- estabilidad del plano frente a tres estados de traslación de cabeza;
- rechazo de rayos paralelos y muestras insuficientes;
- ausencia de cámara, red, datos humanos, mouse como verdad y mutación de pantalla.

Valores sintéticos observados:

- 18 muestras: 9 por monitor;
- tres estados de traslación natural de cabeza;
- `DISPLAY1`: `0.38×0.21 m`, residual máximo `2.94e-14` en el fixture;
- `DISPLAY2`: `0.70×0.39 m`, residual máximo `3.77e-13` en el fixture;
- ambos factores de escala recuperados aproximadamente como `0.064 m` por
  unidad relativa;
- sin EDID: `VALID_RELATIVE`, sin presentar metros;
- rayos paralelos y muestras insuficientes: `UNKNOWN`.

No constituye validación de la webcam ni de precisión de mirada humana.
