# Resultados — experimento 018

El problema real elegido fue la compuerta reutilizable de
`research/tools/run_suite.py`. La ruta directa encontró una guarda de
`returncode != 0` que eleva un error y el marcador final `SUITE_VALID`. La ruta
X-ANA-X mapeó la misma estructura a una línea de producción con compuertas.

| Ruta | Decisión |
|---|---|
| reformulación directa | `terminal_requires_failure_guard` |
| X-ANA-X | `terminal_requires_failure_guard` |

Las rutas produjeron los mismos hechos y la misma decisión. El vocabulario de
la fuente aporta una descripción, pero no una capacidad o decisión adicional.
Por tanto, la novedad de X-ANA-X no queda demostrada en este problema; el
resultado es un control negativo necesario, no una confirmación nominal.

Los kill tests detectaron la inversión adversarial del comparador y la
eliminación del marcador terminal. No hubo red, corpus, datos humanos ni
modelo generativo.
