# Experimento 014 — VIZZ y la consulta de entrada en repetición

Fecha: 2026-08-24

## Pregunta

¿Qué representaciones permiten decidir, de forma reproducible, que una sesión
entró en repetición después de la última mejora significativa?

## Contrato

La consulta global requiere cuatro condiciones observables:

1. identificar la última mejora significativa (`gain >= 0.2`);
2. conservar el orden temporal;
3. observar todos los eventos posteriores;
4. calcular que la ganancia posterior es baja (`gain < 0.2`) y conservar los
   errores de ese tramo.

La consulta local puede describir una señal de repetición dentro de una
ventana, pero no puede llamarla global si la ventana no contiene el ancla o no
contiene todo el tramo posterior. Un campo agregado puede producir una señal
proxy de baja ganancia y errores, pero no atribuirla a una secuencia completa.

## Fixture y límites

Se reutiliza, sin copiar ni modificar, la traza sintética declarada por el
experimento 013. No hay participantes, eye tracking, receta óptica,
mediciones de confort ni exposición bajo intoxicación. El resultado mide
disponibilidad computacional de una decisión, no que una persona la detecte ni
que una interfaz sea mejor.

## Kill tests

- Una ventana de foco de 4 u 8 minutos no puede afirmar la consulta global si
  oculta el evento ancla o parte del tramo posterior.
- El campo agregado no puede afirmar la consulta global ni recuperar identidad
  y orden de eventos, aunque sí puede emitir una señal proxy.
- Una representación con tiempo, ganancia, errores y cobertura completa no
  puede perder artificialmente la consulta global.

Ejecutar:

```text
python experiments/014-vizz-decision-query/run_experiment.py
python experiments/014-vizz-decision-query/run_kill_test.py
```
