# Experimento 010 — familia metamórfica X-ANA-X / KETAMINE

## Pregunta

¿Los invariantes y límites observados en los experimentos 005, 006 y 008
persisten sobre una familia de fixtures SVG sintéticos, en vez de depender de
un único dibujo?

## Diseño

`generate_cases.py` produce 40 casos reproducibles con semilla fija. Cada caso
contiene rectángulos, estilos, una región que cruza el centro, otra región de
control, consultas espaciales/de área/estilo, y eventos temporales externos.

Se comparan fuente, tabla geométrica, tabla indexada, grafo relacional, grafo
con bounding boxes y estado temporal. No es corpus creativo: sirve únicamente
como control metamórfico de invariantes.

## Propiedades

- tabla geométrica preserva espacialidad y área, pero no estilo;
- tabla indexada preserva espacialidad/estilo mediante materialización;
- grafo relacional responde la relación precalculada, no área ni estilo;
- grafo con bounding boxes responde espacialidad/área, no estilo;
- estado temporal responde solo con `events.json`;
- `X_after_K_graph` no puede recuperar coordenadas, mientras las composiciones
  con tabla sí pueden responder el temporal.

## Kill test

Si alguna propiedad cambia de forma inesperada en la familia, el resultado
anterior se considera dependiente del fixture y se reabre el contrato. Si todas
persisten, solo aumenta la robustez dentro del dominio de rectángulos; no
demuestra generalización a curvas, capas complejas, escenas o corpus creativo.
