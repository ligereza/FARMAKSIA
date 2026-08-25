# ADR-052 — VIZZ: separar calibración caótica y sesión controlada

## Estado

Aceptada como protocolo de comparación. El perfil caótico queda conservado
como artefacto de estrés; todavía no se acepta como calibración productiva.

## Evidencia de la sesión recién capturada

La nueva calibración contiene 24/24 muestras con `eye_centric`, distancia
interocular y roll completos, repartidas en 12 puntos con lentes y 12 sin
lentes. La captura temporal fue aceptada con 13–15 muestras válidas por punto,
calidad media global aproximada de 0,989 y MAD de features máximo aproximado de
0,0717, dentro del umbral de captura pero cercano a él.

Los proxies registrados muestran variación deliberada:

- distancia interocular: 52,93–83,52 px, media 71,59 px, desviación 10,10 px;
- ancho facial normalizado: 0,178–0,264;
- altura facial normalizada: 0,307–0,476;
- centro facial X: 0,470–0,654.

Esto confirma que la sesión cubre distancia y pose más amplias que una postura
fija. No demuestra todavía que el mapper pueda separar target, pose y distancia:
si el movimiento ocurrió de forma distinta según el punto, los factores quedan
confundidos.

## Decisión

Sí conviene hacer ahora una segunda sesión con cabeza quieta y recta, cámara y
monitor en la misma posición, distancia cómoda constante y orden de targets
reproducible. Esa sesión no reemplaza ni borra la caótica: funciona como
control instrumental para estimar cuánto error queda cuando se reduce la
confusión de pose.

El orden de análisis será:

```text
perfil caótico ──► estrés / cobertura de pose-distancia
perfil controlado ──► repetibilidad / baseline geométrico
ambos ──► comparación eye-centric vs legacy en targets agrupados
```

Durante el control no se debe forzar una inmovilidad antinatural ni cerrar un
ojo. La instrucción es mantener la cara orientada a la cámara y el torso/cabeza
apoyados o relajados, mirando sólo los targets; después se probará movimiento
como condición separada. Así no se confunde un control de repetibilidad con el
comportamiento normal de uso.

## Kill tests

- Si el control quieto sigue mostrando variación eye-centric grande, el problema
  está en detector, iluminación, lentes o cámara, no sólo en la pose humana.
- Si el control mejora mucho pero el perfil caótico falla, no declarar
  invariancia: el sistema necesita pose explícita o más cobertura equilibrada.
- Si el perfil caótico mejora el test controlado pero empeora su propia sesión,
  revisar fuga de target/pose antes de aceptar el mapper.
- Si una condición de lentes se separa sistemáticamente, mantener el resultado
  como diagnóstico y no atribuirlo a la potencia óptica sin control adicional.

## Estado de archivos

El perfil recién generado se conserva localmente como
`.vizz-calibration-chaotic.json`; no se versiona y no se usará para afirmar
precisión de producción hasta compararlo con la sesión controlada.
