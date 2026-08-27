# Decisión 082 — asociación temporal, no intención automática

## Decisión

El motor de input usará una ventana temporal para buscar deltas nativos de la
misma aplicación, pero conservará tres resultados distintos:

```text
candidate_association
ambiguous_association
unassociated_native_delta
```

Ninguno equivale a intención. La intención sólo puede proponerse después de
observar la postcondición de una tarea y mantener explícitamente la hipótesis.

## Evidencia

El experimento 080 ejecutó Excel real en un libro efímero, observó
`create_entity → modify_property → revert` y no inventó input humano. Sus
pruebas adversariales rechazan coincidencias entre aplicaciones, coincidencias
fuera de ventana y asociaciones con múltiples inputs como si fueran certezas.

## Consecuencia

El modo `live-excel` puede observar una instancia abierta sin modificarla. La
traza sólo conserva conteos, clases allowlisted y resultados de asociación; las
firmas de contenido se quedan en memoria con sal de sesión.

## Próximo criterio

Una sesión humana debe medir latencia, tasa de asociaciones únicas, ambigüedad y
deltas sin input. No se aceptará un traductor de X-ANA-X hasta demostrar que la
asociación mejora una tarea y que el delta puede verificarse de forma
independiente.
