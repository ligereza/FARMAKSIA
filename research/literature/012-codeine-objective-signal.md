# Investigación 012 — señal de objetivo para CODE-INE

Fecha: 2026-08-24

## Resultado científico

La comprensión de código no tiene un marcador químico único. Un estudio de
fMRI encontró una red frontoparietal que también participa en inferencia lógica
y que distingue estructuras de código; otro trabajo estudia carga cognitiva
con factores de tarea y de la persona. Estos resultados apoyan medir tarea,
verificación y resultado, no inferir dopamina, GABA, noradrenalina o ansiedad
desde actividad informática:

- https://elifesciences.org/articles/59340
- https://pubmed.ncbi.nlm.nih.gov/37626489/
- https://pubmed.ncbi.nlm.nih.gov/36825214/

## Señal operacional

Para hablar de deriva hace falta una referencia de objetivo independiente del
mero número de eventos. En FARMAXIA se adopta provisionalmente una señal
`objective_score` declarada por fixture, acotada a `[0, 1]`, con una regla
explícita de aceptación y una tolerancia de descenso. La señal permite
clasificar la traza computacional como estable, regresada o recuperada; no
prueba que la persona comprenda el objetivo ni que el score sea verdadero.

Un score emitido por el propio proceso puede estar sesgado. Una futura sesión
humana necesitaría definir quién o qué verifica el criterio, cómo se registra
la aceptación y cómo se separan resultado objetivo, autoinforme y actividad.

## Consecuencia para CODE-INE

CODE-INE queda como vocabulario de dos capas:

1. transición de actividad, mejora y repetición, observable en el envelope
   mínimo;
2. relación con objetivo, disponible solo cuando existe una señal declarada,
   completa y validada.

La ausencia de la segunda capa debe producir `unavailable`, no una etiqueta de
deriva. Ninguna capa autoriza equivalencias con codeína, sedación,
neurotransmisores o diagnósticos psicológicos.
