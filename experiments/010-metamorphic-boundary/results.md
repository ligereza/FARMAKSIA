# Resultados 010 — familia metamórfica X-ANA-X / KETAMINE

Fecha: 2026-08-23

## Ejecución

Se generaron `40` casos sintéticos con semilla `20260823`. Todas las
propiedades declaradas pasaron `40/40` y no hubo violaciones.

| Propiedad | Pasos |
|---|---:|
| tabla geométrica preserva espacialidad | 40/40 |
| tabla geométrica preserva área | 40/40 |
| tabla geométrica pierde estilo | 40/40 |
| tabla indexada preserva espacialidad y estilo | 40/40 |
| grafo relacional preserva relación precalculada | 40/40 |
| grafo relacional carece de área y estilo | 40/40 |
| grafo con bounding boxes preserva espacialidad y área | 40/40 |
| grafo con bounding boxes pierde estilo | 40/40 |
| estado temporal preserva el observable con eventos | 40/40 |
| temporal requiere `events.json` | 40/40 |
| composición gráfica no conmuta | 40/40 |
| composiciones tabulares equivalentes | 40/40 |

## Decisión

Los resultados de los fixtures 005, 006 y 008 no dependen de los números del
SVG inicial dentro del dominio probado. La pérdida de invariantes, la
dependencia temporal externa y la no-conmutatividad del grafo se mantienen.

Esto fortalece la reproducibilidad del kill test, pero no prueba generalidad
artística: todos los casos son rectángulos axis-aligned generados por máquina.
No se incorporan como corpus creativo ni justifican adoptar una herramienta
externa.

## Próximo kill test

Repetir con curvas, capas, orden de composición, metadata y al menos una obra
autorizada. Si la frontera cambia allí, el resultado metamórfico actual se
conserva como control de dominio limitado, no como ley general.
