# ADR-048 — VIZZ: diagnóstico del perfil multicondición 0.4

## Estado

Exploratorio; no aprobado como calibración precisa.

## Evidencia observada

El perfil local `0.4` contiene 24 observaciones sobre los mismos 12 targets:
12 `with_glasses` y 12 `without_glasses`. El runtime inició con el perfil
único y la agregación declara `pooled_observations_refit`; no se promediaron
coeficientes.

La captura temporal fue consistente: la condición sin lentes produjo 13–14
muestras válidas por target, calidad media entre 0.969 y 0.997 y MAD máximo
0.0723, bajo el umbral inicial pero cercano a él.

La representación ocular no fue invariante entre condiciones. En la sesión con
lentes, los yaw de los bordes fueron aproximadamente `±1.95` en las filas
superiores y cercanos a `±0.2` en las inferiores. Sin lentes se observó casi el
patrón inverso. La diferencia pareada de yaw tuvo desviación aproximada 1.29,
por lo que no puede modelarse inicialmente como un pequeño offset constante.

## Comparación interna

Estos números son residuales sobre las mismas observaciones usadas para
ajustar, no una validación independiente:

- refit polinomial conjunto uniforme: mediana aproximada 195 px, máximo 703 px;
- mapper anterior aplicado sin lentes: mediana aproximada 527 px, máximo 2.679 px;
- baseline afín conjunto: mediana aproximada 200 px;
- refit preliminar ponderado por `valid_count/MAD`: mediana aproximada 216 px,
  y 278 px para sin lentes.

La ponderación no se adopta todavía. Los resúmenes median/MAD no contienen
autocorrelación ni covarianzas cruzadas suficientes para afirmar un GLS exacto,
y el resultado fue sensible a la elección de pesos.

## Interpretación

La fusión de observaciones funciona como operación de datos, pero el patrón no
permite atribuir causalidad a los lentes. Las hipótesis siguen abiertas:

1. cambio de pose, distancia o recorte facial al retirar los lentes;
2. efecto óptico-mecánico de la montura o reflejos;
3. limitación del detector ocular ante pitch/yaw extremos;
4. convención o geometría de cámara mal compensada.

El perfil no debe presentarse como preciso ni como instrumento clínico.

## Siguiente kill test

Repetir targets pareados con apoyo de mentón, cámara/pantalla fijas, orden de
condiciones aleatorizado y al menos tres repeticiones por target. Registrar
pose de cabeza independiente (`yaw`, `pitch`, `roll`, escala y traslación).
Comparar modelos anidados con y sin pose y reportar error por condición, fila y
sesión completa. Si la inversión desaparece al equilibrar pose, no se atribuye
a lentes. Si persiste con pose fija y landmarks crudos, queda compatible con
efecto óptico o artefacto del detector, no demostrado causalmente.
