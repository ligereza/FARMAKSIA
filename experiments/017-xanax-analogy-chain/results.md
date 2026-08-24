# Resultados — experimento 017

La cadena seleccionó `queue-interval` por mayor solapamiento de señales
(`active`, `time`, `enter`, `exit`, `interval`) frente a la tarjeta estática.
El mapeo predijo que `left-region` estaría activa en `t=0.25`; la verificación
de `events.json` confirmó esa predicción y la consulta geométrica del objetivo
confirmó que cruza el centro.

La ruptura también quedó explícita. En `t=0.75`, el objetivo puede verificar
`right-region` como región activa que está a la derecha del centro, pero la
analogía de intervalos no puede producir la relación `right_of_center` porque
esa relación no existe en la fuente. Debe devolver “no disponible sin geometría
del objetivo”.

| Etapa | Resultado |
|---|---|
| búsqueda | selecciona `queue-interval` |
| mapeo | conserva actividad temporal; declara residuo geométrico |
| predicción | `left-region` |
| verificación | coincide con objetivo |
| ruptura | geometría no transferible |

Esto demuestra una cadena reproducible de analogía y verificación sobre
fixtures locales, no novedad teórica, comprensión humana ni eficacia de una
analogía en una persona. No se usó red, corpus creativo ni datos humanos.
