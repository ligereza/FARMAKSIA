# Experimento 025 — invariancia de condición de display VIZZ

## Pregunta

¿Puede VIZZ cambiar condiciones de display —día, tarde, noche, escala y foco—
sin mutar los datos de tarea ni convertir una condición visual en una
afirmación de fatiga, pupila, ansiedad, intoxicación o farmacología?

## Diseño

Se reutiliza la sesión sintética 022 y se comparan perfiles declarados:

- texto completo de día, tarde y noche;
- foco nocturno que conserva el ancla `c04` y todo el tramo posterior;
- foco nocturno que oculta el ancla;
- campo agregado nocturno sin identidad ni orden de eventos.

Los parámetros de luminancia, contraste, temperatura cromática y escala son
metadatos de presentación. El runner verifica que no alteren el fingerprint
semántico de la sesión completa. La consulta CODE-INE se considera disponible
solo si conserva el ancla y todos los eventos posteriores requeridos; perder
contexto anterior se registra como residuo, no se oculta.

`night` no significa pupila dilatada, melatonina, sueño, ansiedad ni consumo de
sustancias. La receta de lentes tampoco se aplica desde este prototipo.

## Kill tests

- Los tres perfiles completos deben tener el mismo fingerprint semántico.
- El foco nocturno con ancla y tramo posterior puede conservar la consulta,
  pero debe declarar contexto anterior perdido.
- El foco sin ancla y el campo agregado deben devolver `unavailable`.
- Ningún perfil puede producir una afirmación fisiológica o farmacológica.

Ejecutar:

```text
python experiments/025-vizz-display-condition-invariance/run_experiment.py
python experiments/025-vizz-display-condition-invariance/run_kill_test.py
```
