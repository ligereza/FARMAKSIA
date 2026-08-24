# Decisión 019 — bounding boxes no preservan geometría arbitraria

Fecha: 2026-08-23

## Evidencia

El experimento 011 comparó geometría completa, tabla de vértices, grafo de
bounding boxes y relaciones exactas sobre 20 casos poligonales. La tabla
preservó la consulta `point-in-polygon` en `20/20`; el grafo de bounding boxes
produjo falsos positivos en `20/20`.

## Decisión

Queda falsada la afirmación amplia de que un grafo con bounding boxes preserva
consultas geométricas arbitrarias. El resultado positivo del experimento 006
era específico de rectángulos, donde la caja coincide con la forma.

KETAMINE debe declarar clase de geometría, consulta preservada y residuo. La
pérdida observada se explica por una representación resumida conocida; no
aporta novedad conceptual por sí misma.

## Próximo límite

Probar curvas, capas, orden de composición y una obra autorizada. Un grafo más
rico solo sería una diferencia relevante si preservara una consulta necesaria
sin convertirse simplemente en una representación geométrica o índice ya
conocido.
