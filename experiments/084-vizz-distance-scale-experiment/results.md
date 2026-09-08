# Resultados — experimento 084

## Estado

El contrato sintético queda preparado para la primera prueba de distancia vs.
resolución. Usa las dos medidas exigidas —distancia entre ojos y ancho facial—,
compensa una pose acotada, fusiona en logaritmos y se abstiene cuando hay
discrepancia.

La figura de control es un Landolt C. Con una referencia de 100 px a 600 mm,
la geometría predice 75 px a 450 mm y 150 px a 900 mm para conservar el ángulo.
El resultado es una predicción matemática del fixture, no una medición humana.

## Evidencia ejecutable

```text
FARMAXIA_084_VIZZ_DISTANCE_SCALE_CONTRACT_VALID
FARMAXIA_084_VIZZ_DISTANCE_SCALE_KILL_TESTS_VALID
FARMAXIA_084_VIZZ_TRACE_ANALYZER_TEST_VALID

## Primera traza humana

El registro `.vizz-distance-scale-trace.jsonl` contiene una sesión de unos
30,33 s con 606/606 muestras válidas. La mediana de discrepancia logarítmica
entre las reglas de ojos y cara fue `0,0168` y el máximo `0,0693`, por debajo
del límite de abstención `0,25`. La escala facial fusionada tuvo mediana
`0,5284` y la razón de distancia relativa mediana fue `1,8925`; el objetivo
varió entre `100,4` y `297,0` px.

El primer decil tuvo mediana de escala `0,9322` y el último `0,7631`. Esto es
compatible con que la persona se alejara o cambiara de distancia durante el
trabajo, y confirma que el efecto visual se activó. La experiencia subjetiva
reportada fue positiva, pero todavía no constituye una medición de comodidad
ni de reducción de fatiga.
```

## Desconocido

Todavía no conocemos la distancia física en milímetros, porque no se registró
una medida externa, ni tenemos corrección 3-D de yaw/pitch. Tampoco podemos
atribuir el efecto subjetivo sólo a la deformación con una sesión. La siguiente
fase debe comparar tamaño fijo frente a tamaño ajustado en bloques pareados y
conservar sólo resúmenes y metadatos necesarios; no afirmar precisión clínica
ni empezar con una MLP.
