# Resultados iniciales del experimento 089

## Estado

Implementado el contrato offline y realizada una captura humana dual en
`vizz-dual-closed-calibration-20260829-041052.json`, iniciada explícitamente
con ambas cámaras preparadas.

La captura anterior sí existe, pero no es una calibración dual válida: la
Hikvision quedó sin muestras después de las primeras ventanas y el formato
anterior no guardaba contadores de causa por muestra. Por eso sus fallos sólo
permiten localizar el problema a nivel de ventana, no atribuirlo con certeza a
RTSP o inferencia.

El runtime ahora incluye reconexión del stream tras dos lecturas consecutivas
fallidas y registra `read_failures`, `reconnect_attempts`,
`reconnect_successes` y `reconnect_failures`, sin guardar URL, credenciales ni
vídeo.

## Evidencia offline obtenida

```text
VIZZ_089_DUAL_SENSOR_CONTRACT_VALID
SUITE_VALID
```

La prueba verificó que:

- los puntos se etiquetan por la pantalla, no por el cursor;
- la ventana de muestras termina antes del clic;
- la calibración se ajusta por sensor;
- la validación deja juntos todos los registros de un target;
- cada punto puede recibir una predicción numérica de pantalla por sensor y una
  fusión explícitamente marcada como diagnóstico in-sample;
- no se persisten frames ni credenciales.

También se verificó con una geometría sintética que el módulo estéreo recupera
una profundidad conocida cuando se le entregan intrínsecos y pose relativa.
La suite global del repositorio terminó `SUITE_VALID` después de incorporar el
experimento 089 al runner.

## Evidencia de la captura humana 2026-08-29

- 24 ventanas solicitadas; 23 entraron en la validación agrupada y una quedó
  degradada por muestras insuficientes.
- La Hikvision tuvo 2 fallos de lectura y 1 reconexión exitosa; el muestreador
  no terminó con error.
- En las ventanas válidas, el par pupila-glint apareció casi siempre en ambos
  ojos y la tasa mediana fue 1.0. Esto confirma que la rama encuentra
  candidatos, no que sean reflejos corneales verdaderos.
- El diámetro candidato varió aproximadamente entre 5,2 y 17,8 px entre
  ventanas. En repeticiones del mismo target, el vector pupila→glint cambió
  varios píxeles y hasta más de 10 px en algunos ejes.
- El mapper Hikvision obtuvo mediana/P95 de 838/951 px; la webcam obtuvo
  270/388 px; la fusión obtuvo 438/569 px. Por tanto, el IR no debe entrar aún
  en la predicción de pantalla.

La captura fue anterior a la última corrección del resumen: no conserva
`pupil_polarity_counts` ni las MAD del vector/diámetro. El detector sí funcionó,
pero esas dos medidas serán necesarias en la siguiente captura para separar
señal consistente de falsos blobs.

## Límite declarado

El primer corte implementa doble calibración y fusión. No declara todavía
triangulación métrica 3-D: para eso faltan intrínsecos y extrínsecos de las dos
cámaras. La captura conserva el material escalar y los ray proxies necesarios
para añadir esa etapa sin repetir la interfaz de puntos.

## Segundo corte: rama óptica IR

Se añadió una rama específica para la Hikvision que reutiliza los landmarks
oculares ya calculados y examina dos ROIs pequeñas en luminancia. Busca dos
señales distintas:

- una región oscura compatible con la pupila;
- un blob pequeño y brillante compatible con el reflejo corneal (glint).

La salida por ojo queda etiquetada como `PUPIL_GLINT`, `PUPIL_ONLY`,
`GLINT_ONLY` o `NO_FEATURES`, junto con diámetro pupilar candidato, vector
pupila→glint, contraste y confianza. Sólo se guardan escalares; no se guarda
el frame ni se agrega otra inferencia ONNX/GPU.

La rama está deliberadamente fuera del mapper. La prueba sintética recupera
correctamente una pupila y un glint conocidos y la suite completa sigue en
`SUITE_VALID`. Eso demuestra que el camino de datos y sus estados funcionan,
no que la Hikvision produzca todavía una medición ocular válida en vivo.

## Siguiente captura

Repetir la calibración 089 con la Hikvision en Night/IR, sin cambiar su
posición. Luego revisar, por sensor y por ventana:

```text
ir_optics_status
ir_pupil_glint_pair_rate
ir_pupil_polarity_counts
ir_pupil_glint_vector_median_px
ir_pupil_glint_vector_mad_px
ir_pupil_diameter_median_px
ir_pupil_diameter_mad_px
ir_confidence_median
```

El criterio de avance es que la señal `PUPIL_GLINT` aparezca de forma estable
en ambos ojos, que la polaridad sea interpretable y que la MAD del vector y del
diámetro sea pequeña dentro de cada ventana. Si domina `NO_FEATURES`,
`PUPIL_ONLY` o el vector salta sin relación con la pose, se congela esta
heurística y se pasa a calibración estéreo con un patrón Charuco; no se
alimenta el mapper con una señal inestable.
