# Experimento 024 — frontera de latencia y cobertura VIZZ

## Pregunta

¿Cuándo una actualización adaptativa dependiente de la mirada deja de cubrir
la ancla y el tramo posterior necesarios para la consulta CODE-INE?

## Diseño

Se usa una traza sintética de ocho eventos y una trayectoria sintética de
mirada que cambia de región antes de `c04` y `c07`. El renderer simulado
selecciona la muestra más reciente disponible en `evento.t_ms - latencia` y
expone un foco con radio fijo. Se comparan cinco latencias declaradas:

`0`, `100`, `101`, `250` y `1000` ms.

El valor 100/101 ms solo es un borde del fixture temporal; no es un umbral de
percepción ni una recomendación de hardware. La literatura 010 exige medir la
latencia real de extremo a extremo antes de extrapolar.

La consulta global se clasifica así:

- `available`: todos los eventos requeridos siguen visibles y el detector
  reproduce `c04 → c07`;
- `unavailable`: falta cualquier evento de la cobertura requerida, aunque el
  subconjunto visible pudiera producir una señal parcial.

El runner no calcula ni publica una transición a partir de un subconjunto
incompleto.

## Kill tests

- Latencia cero y 100 ms deben conservar la consulta completa del fixture.
- Latencias mayores que el borde del fixture deben ocultar al menos un evento
  y devolver `unavailable`.
- Ningún caso `unavailable` puede publicar `repetition_entry`.
- No se inician dispositivos, no se usa red, no se escribe una sesión y no se
  infiere percepción humana, fatiga, ansiedad, intoxicación o farmacología.

Esto prueba una propiedad de cobertura computacional, no la experiencia visual
de una persona.

Ejecutar:

```text
python experiments/024-vizz-latency-coverage-boundary/run_experiment.py
python experiments/024-vizz-latency-coverage-boundary/run_kill_test.py
```
