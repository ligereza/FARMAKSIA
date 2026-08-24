# Decisión 025 — CODE-INE queda como descriptor de transición, no como operador

Fecha: 2026-08-24

## Evidencia

El experimento 016 usa ocho eventos sintéticos con tiempo, clase de acción,
ganancia y errores. Encuentra dos mejoras (`c02`, `c04`), toma `c04` como última
ancla y ubica una entrada en repetición en `c07`, cuando `maintain` reaparece.

Una vista reducida a tiempo, ganancia y errores conserva una señal proxy de
baja ganancia, pero no puede ubicar la repetición exacta. La deriva permanece
no disponible porque no se declaró una medida de objetivo o distancia.

## Decisión

CODE-INE puede continuar como vocabulario de una transición de sesión:

`actividad → mejora → repetición`

No se rescata como operador independiente. La evidencia es compatible con un
detector de eventos y una política de clasificación ordinarios. El nombre no
autoriza inferir codeína, sedación, dopamina, noradrenalina ni ansiedad.

## Kill tests

La hipótesis descriptiva queda debilitada si se elimina la clase de acción y el
detector sigue afirmando una entrada exacta en repetición, o si declara deriva
sin objetivo. Ambos límites se conservan en el runner y pasan en la traza
sintética.

## Próximo objetivo

Reutilizar el envelope opt-in de VIZZ para una sesión manual local, sin texto
personal ni captura cruda, y comprobar si las clases de acción pueden declararse
sin interrumpir la tarea. No recoger todavía participantes ni señales
neurofisiológicas.
