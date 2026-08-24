# Resultados — experimento 024

El renderer sintético conservó la cobertura completa y la transición
`c04 → c07` con latencias de `0` y `100` ms del fixture. Con `101`, `250` y
`1000` ms se ocultaron eventos al aplicar la muestra de mirada retrasada; esos
casos devolvieron `unavailable` y no publicaron una transición parcial.

| Latencia del fixture | Cobertura | Consulta CODE-INE |
|---:|---|---|
| 0 ms | completa | `available` |
| 100 ms | completa | `available` |
| 101 ms | incompleta | `unavailable` |
| 250 ms | incompleta | `unavailable` |
| 1000 ms | incompleta | `unavailable` |

El borde 100/101 ms pertenece únicamente a la geometría y al calendario de
muestras declarados en `trace.json`. No es una medición de latencia tolerable
para personas, una propiedad de un monitor ni una recomendación para eye
tracking.

El resultado sí fija una regla computacional: si la adaptación no cubre el
ancla o cualquier evento posterior requerido, VIZZ no debe alimentar a
CODE-INE con un subconjunto como si fuera la sesión completa.

No hubo participantes, cámara, mirada real, red, escritura de sesión ni
inferencia farmacológica.
