# Decisión 027 — X-ANA-X no añade una decisión en la compuerta de la suite

Fecha: 2026-08-24

## Evidencia

El experimento 018 aplicó X-ANA-X a un problema real pequeño del repositorio:
qué protege el marcador `SUITE_VALID` en `research/tools/run_suite.py`.

La ruta directa por AST detectó la guarda de retorno y el marcador terminal.
La ruta analógica los describió como una línea con compuertas. Ambas rutas
produjeron los mismos hechos y la misma decisión:
`terminal_requires_failure_guard`.

Los kill tests detectaron la inversión del comparador y la eliminación del
marcador, lo que demuestra que el control directo es sensible a cambios reales
del código.

## Decisión

En este problema X-ANA-X no muestra una decisión adicional. El resultado debilita
la hipótesis de novedad y evita confundir una analogía explicativa con una
capacidad computacional. X-ANA-X se conserva provisionalmente como protocolo de
transferencia auditable, pero no como operador o ventaja demostrada.

## Próximo objetivo

Solo se justifica un último intento en un problema donde el mapeo relacional
genere una predicción comprobable que no sea una paráfrasis de la inspección
directa. Si ese control también coincide, X-ANA-X deberá fusionarse con
reformulación/state augmentation y archivarse como hipótesis independiente.
