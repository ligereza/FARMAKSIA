# Resultados 012 — curvas, agujeros y capas

Fecha: 2026-08-23

## Ejecución

Se generaron `20` escenas sintéticas con curvas Bézier cerradas, un anillo con
agujero y capas. La consulta pide la forma visible en un punto.

| Representación/propiedad | Resultado |
|---|---:|
| tabla de curvas muestreadas preserva forma visible | 20/20 |
| grafo de bounding boxes preserva forma visible | 0/20 |
| falsos positivos por agujero | 20/20 |
| relación visible precalculada | 20/20 |
| tabla conserva orden de capas | 20/20 |

El grafo de bounding boxes elige el `donut-curve` de capa superior porque su
caja contiene el punto, aunque el agujero lo deja fuera. La tabla conserva
contornos y capa, por lo que devuelve `solid-curve`; el grafo relacional solo
responde correctamente porque la relación ya fue calculada antes de perder la
geometría.

## Decisión

La pérdida geométrica y la pérdida de composición son invariantes separados.
Conservar bounding boxes no preserva visibilidad en curvas con agujeros, y
conservar forma sin capa tampoco bastaría para reconstruir la imagen visible.

KETAMINE debe declarar contornos, regla de relleno, capas y orden, además de la
consulta y el residuo. El resultado sigue siendo un control sintético, no
evidencia sobre una obra creativa ni novedad frente a representaciones
geométricas conocidas.
