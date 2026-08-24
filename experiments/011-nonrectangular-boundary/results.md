# Resultados 011 — frontera no rectangular

Fecha: 2026-08-23

## Ejecución

Se generaron `20` casos sintéticos de triángulos con semilla `20260823` y se
consultó el mismo punto en cada caso.

| Representación/consulta | Resultado |
|---|---:|
| tabla de vértices preserva point-in-polygon exacto | 20/20 |
| grafo de bounding boxes preserva consulta exacta | 0/20 |
| casos con falso positivo del bounding box | 20/20 |
| relación exacta precalculada preserva su propia consulta | 20/20 |

El grafo de bounding boxes marca `bbox-only` como candidato aunque el punto
está fuera del triángulo. El grafo relacional puede responder la relación que
ya fue materializada, pero no permite reconstruir la geometría exacta ni
resolver un punto nuevo.

## Decisión

Queda falsada la hipótesis amplia de que un grafo con bounding boxes preserva
consultas geométricas arbitrarias. El resultado de 006 era válido para
rectángulos, donde el bounding box coincide con la forma; no se generaliza a
polígonos.

KETAMINE debe declarar explícitamente el residuo geométrico y la clase de
consulta preservada. La pérdida no mata el contrato experimental, pero reduce
aún más cualquier afirmación de novedad frente a índices, caches y
representaciones resumidas conocidas.

El fixture sigue siendo sintético: no prueba valor artístico ni sustituye una
obra autorizada.
