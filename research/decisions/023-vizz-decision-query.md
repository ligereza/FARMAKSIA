# Decisión 023 — VIZZ necesita un ancla antes de llamar global a una repetición

Fecha: 2026-08-24

## Evidencia

El experimento 014 reutiliza exactamente la traza sintética del 013. Declara
`e06` como última mejora significativa (`gain >= 0.2`) y `e07–e10` como tramo
posterior, con ganancia total `0.14` y un error.

- texto y timeline conservan ancla, orden, cobertura completa, ganancia y
  errores; la consulta global queda disponible;
- foco `38m ± 16m` también contiene `e06–e10`, por lo que la consulta queda
  disponible en esta traza, pero ventanas de 4 u 8 minutos la pierden;
- el campo agregado conserva una señal proxy de baja ganancia y errores, pero
  no puede demostrar que la señal ocurre después de la última mejora porque no
  conserva identidad ni orden.

## Decisión

El contrato VIZZ se especializa como:

`consulta global → ancla + orden + cobertura + valores necesarios → decisión`

La adaptación de exposición debe declarar el residuo antes de presentar una
señal. “Veo repetición” y “sé que comenzó después de la última mejora” son
consultas distintas; la primera puede sobrevivir a una agregación y la segunda
no.

Esto sigue siendo una propiedad de información computacional. No demuestra
mejor detección humana, comodidad, reducción de carga visual ni beneficio de
eye tracking.

## Kill tests

La hipótesis queda falsada si el runner permite que un foco sin ancla o sin
todo el tramo posterior responda la consulta global, o si el campo agregado
recupera identidad y orden. También sería un fallo que una representación
completa pierda la consulta.

Los kill tests pasan en la traza declarada. KETAMINE permanece en cuarentena y
no se introducen datos humanos.

## Próximo objetivo

Instrumentar una sesión local no intoxicada con eventos explícitos de objetivo,
acción, ganancia, error y pausa, manteniendo la captura opt-in y sin contenido
personal. Solo después de verificar que la instrumentación mide las mismas
variables sin pérdida accidental se decidirá si el prototipo VIZZ necesita
eye tracking o una evaluación humana.
