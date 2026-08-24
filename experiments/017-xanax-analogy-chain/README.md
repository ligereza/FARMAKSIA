# Experimento 017 — cadena mínima X-ANA-X

Fecha: 2026-08-24

## Pregunta

¿Puede una analogía seleccionada por una búsqueda explícita producir una
predicción transferible y verificable sobre una consulta temporal, y mostrar
su propio punto de ruptura?

## Cadena

El runner conserva la secuencia:

`confusión → laguna → búsqueda → fuente → mapeo → predicción → verificación → ruptura`

El objetivo es un fixture local ya existente: determinar qué región SVG está
activa en `t=0.25` y además cruza el centro `x=200`. La búsqueda compara dos
tarjetas de fuente declaradas en un catálogo controlado: una estructura de
intervalos con `enter/exit` y una estructura de contención estática. El
“information scent” se calcula por solapamiento de términos declarados; no se
consulta la web durante la ejecución.

La analogía seleccionada mapea `job → region`, `interval → active interval`,
`enter/exit → temporal events` y `slot → target point`. Predice la región
activa; la geometría del centro se verifica en el dominio objetivo y no se
inventa desde la fuente.

## Ruptura

Al pedir “qué región activa está a la derecha del centro en `t=0.75`”, la
analogía de intervalos todavía puede decir qué está activo, pero no puede
transportar la relación geométrica `right_of_center`. El resultado correcto es
`unavailable_without_target_geometry`, aunque el verificador del objetivo sí
puede obtener `right-region`.

## Límites y kill tests

- Sin `events.json`, la predicción temporal queda no disponible.
- Una fuente estática sin `enter/exit` no puede ganar la consulta temporal.
- La analogía no puede responder la relación geométrica que no mapea.
- La misma respuesta no prueba novedad teórica: el runner conserva entradas,
  relaciones, autoridad y residuo.

No se usa corpus creativo, red, datos humanos ni modelo generativo. Las
tarjetas son fixtures declarados para probar la cadena.

Ejecutar:

```text
python experiments/017-xanax-analogy-chain/run_experiment.py
python experiments/017-xanax-analogy-chain/run_kill_test.py
```
