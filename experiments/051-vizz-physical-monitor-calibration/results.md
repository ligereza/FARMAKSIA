# Resultados — Experimento 051

Estado observado: `VIZZ_051_PHYSICAL_CALIBRATION_CONTRACT_VALID`.

El fixture sintético debe demostrar:

- dos monitores físicos convertidos a planos 3D;
- 18 targets presentados, nueve por monitor;
- intersección válida de un rayo con el plano primario;
- versión física derivada de la versión lógica y de las medidas;
- rechazo explícito de `windows_pixels` como fuente de metros;
- ausencia de cámara, red, datos humanos y mutación de pantalla.

Valores sintéticos observados:

- dos planos físicos preservados;
- `calibration_target_count=18`;
- intersección primaria válida con `uv=(0.6338, 0.6190)`;
- distancia sintética al punto: `0.7255 m`;
- versión física: `828d14e4694f12ac`;
- rechazo de fuente pixel-only: `true`.

Estos resultados no representan la geometría real del escritorio del usuario
ni validan precisión de gaze o reducción de fatiga.
