# Resultados 001 — primera ejecución

Fecha: 2026-08-23

## Baseline ejecutado

Herramienta: Python 3.13.15, `xml.etree.ElementTree` de la biblioteca estándar.

Resultado de inspección:

- elementos SVG de primer nivel: 4;
- regiones cerradas examinadas: `left-region`, `right-region`;
- consulta: intersección con la línea `x = 200`;
- resultado: `left-region` intersecta; `right-region` no intersecta.

## Qué demuestra

1. La consulta geométrica puede verificarse sin convertir todavía el objeto a
   una base de datos, grafo o imagen raster.
2. La estructura XML/SVG ya contiene una representación suficiente para esta
   consulta.
3. Instalar más herramientas en este punto no produciría evidencia adicional.

## Clasificación provisional

La lectura del SVG como árbol estructurado es una operación de acceso, no
necesariamente KETAMINE.

La extracción de una tabla de regiones podría ser KETAMINE si conserva la
consulta y declara sus invariantes geométricos.

La adición de una variable temporal, una secuencia de eventos o una nueva
partición sería candidata a X-ANA-X porque habilita preguntas que no existen en
la consulta geométrica original.

## Resultado de falsación

Todavía no se ha demostrado que la distinción sobreviva transformaciones
reales. El resultado solo valida que el experimento es observable y pequeño.

## Próximo paso

Crear tres representaciones derivadas del mismo SVG —tabla geométrica, grafo de
relaciones y estado con dimensión temporal— y medir qué consultas preserva cada
una, qué consultas nuevas permite y qué información destruye.

## Segunda ejecución: representaciones derivadas

Se ejecutó `run_experiment.py` con Python 3.13.15 y biblioteca estándar. No se
instalaron dependencias nuevas. La temporalidad ya no está codificada dentro
del arnés: se lee desde `events.json`, un registro externo de cuatro eventos.

Consulta espacial declarada (`Q0`): regiones cerradas que intersectan la línea
central `x = 200`.

Resultado esperado y obtenido: `left-region`.

| Representación | Tamaño JSON | Q0 preservada | Consulta nueva | Residuo principal |
|---|---:|---|---|---|
| SVG derivado | 185 B | Sí | Ninguna | metadatos SVG omitidos en el baseline |
| tabla geométrica | 188 B | Sí | filtros numéricos | orden, estilos y tags originales |
| grafo relacional | 232 B | Sí | recorrido de relaciones | coordenadas y capacidad de recalcular geometría |
| geometría temporal | 283 B | Sí | `active_at(0.25)`, `active_at(0.75)` | el tiempo es una hipótesis añadida |
| control temporal constante | 282 B | Sí | `active_at(t)` sin distinción | campo temporal redundante |

Las consultas temporales produjeron:

- `active_at(0.25)` → `left-region`;
- `active_at(0.75)` → `right-region`.

El control temporal constante produjo `left-region` y `right-region` en ambos
instantes. Añadir una dimensión sin variación no creó una consulta nueva con
capacidad discriminativa.

Esto cambia la interpretación: el tiempo no fue descubierto por una conversión
del SVG. Fue incorporado como una fuente adicional de estado. Por tanto, la
operación temporal completa no es KETAMINE puro; es una combinación de
incorporación de estado y representación temporal, con un componente candidato
a X-ANA-X.

Los tiempos medianos de consulta estuvieron entre `0.0003 ms` y `0.0004 ms`.
No se consideran una comparación de rendimiento: el objeto es demasiado
pequeño y la variación está dominada por el entorno. Se conservarán solo como
baseline de reproducibilidad.

## Interpretación

La tabla geométrica es un candidato claro a KETAMINE: cambia la forma de
almacenar y consultar geometría, preservando `Q0` mediante invariantes
explícitos.

El grafo es un caso límite: preserva `Q0` como hecho derivado, pero no conserva
la capacidad de responder preguntas geométricas nuevas. Es una representación
útil para una consulta concreta, no una transformación generalmente reversible.

La geometría temporal es candidata a X-ANA-X: mantiene `Q0`, pero introduce una
variable y un espacio de estados nuevos. Las etiquetas temporales no provienen
del SVG; son una hipótesis de modelado. Por eso no deben contarse como
información descubierta.

El control evita una falsa conclusión: un campo temporal redundante no basta
para X-ANA-X. La dimensión adquiere relevancia solo cuando introduce estados,
observables o transiciones que permiten preguntas que la representación
original no podía responder.

## Decisión del ciclo

La frontera sobrevive provisionalmente, pero con una condición:

- KETAMINE debe declarar la consulta preservada y sus invariantes.
- X-ANA-X debe introducir variables, observables o estados que cambien el
  conjunto de preguntas posibles.

El resultado todavía no prueba que sean teorías independientes. El kill test
se ejecutó parcialmente mediante el control temporal. Al eliminar la variación
temporal, desaparece la discriminación entre regiones. Esto refuerza, pero
todavía no demuestra definitivamente, que el candidato X-ANA-X depende de una
modificación semántica del espacio de estados y no de añadir columnas.

El experimento también descarta una formulación demasiado fuerte de KETAMINE:
una representación no puede reclamar preservación de una dimensión que no
estaba en la entrada. Si la dimensión viene de otra fuente, debe registrarse
como entrada adicional, con su procedencia y autoridad.

## Artefactos

- entrada: `input.svg`;
- registro temporal: `events.json`;
- arnés: `run_experiment.py`;
- este registro: `results.md`.

## Procedencia y validación

`provenance.json` registra 10 entidades, 6 actividades, 3 consultas y 2 agentes.
Se validó con `validate_provenance.py`:

- caso íntegro: `PROVENANCE_VALID`;
- copia temporal con `input.svg` alterado: `PROVENANCE_INVALID: hash mismatch for farmaxia:input-svg`.

La prueba negativa demuestra que el registro detecta una entrada modificada.
El manifiesto también registra y verifica el hash del propio arnés de medición.
Esto deja explícito que `events.json` es una entrada adicional y no una
propiedad preservada del SVG, y que los resultados dependen de un código
identificable.
