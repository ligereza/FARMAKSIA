# Experimento 028 — compuerta de calidad y procedencia gaze-contingent VIZZ

## Pregunta

¿Puede VIZZ habilitar adaptación dependiente de la mirada únicamente cuando un
adaptador declara consentimiento, procesamiento permitido, calibración,
latencia, cobertura, pose estable y herramienta conocida?

## Diseño

Se usa la sesión sintética VIZZ 022 para conservar la transición CODE-INE base
`c04 → c07`. El experimento no reproduce una webcam ni un headset. Compara diez
once perfiles de metadatos contra la política declarada en `tool_candidates.json`.

Clasificaciones:

- `available`: todas las compuertas pasan; el contrato permite adaptación,
  sin afirmar que la mirada sea correcta en una persona;
- `blocked`: falta consentimiento o se viola la política local/sin red;
- `unavailable`: faltan calidad, calibración, cobertura o latencia;
- `rejected`: herramienta desconocida o metadato mal formado.

La adaptación es solo una bandera de contrato. No se cambia una pantalla, no se
lee una cámara, no se guardan coordenadas humanas y no se interpreta la mirada
como atención, fatiga, ansiedad, pupila, intoxicación o neurotransmisores.

## Kill tests

- Ningún perfil que no sea `available` puede habilitar adaptación.
- Sin consentimiento, con red o con un candidato Pupil Core que use su API de
  red, la política debe bloquear.
- Calibración ausente, error alto, latencia alta o cobertura parcial deben
  quedar `unavailable`.
- Candidato desconocido y latencia mal formada deben ser rechazados.
- La transición base debe permanecer `c04 → c07`.

Ejecutar:

```text
python experiments/028-vizz-gaze-quality-gate/run_experiment.py
python experiments/028-vizz-gaze-quality-gate/run_kill_test.py
```
