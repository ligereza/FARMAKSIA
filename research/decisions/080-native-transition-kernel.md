# Decisión 080 — kernel de transición para X-ANA-X

## Decisión

Usar transiciones de estado como unidad mínima de analogía entre aplicaciones:

```text
create_entity → select_entity → modify_property → revert
```

El kernel no afirma que las entidades sean iguales. Afirma que una operación
puede transferirse sólo cuando conserva sus precondiciones, su tipo de cambio,
su resultado observable y su reversibilidad.

## Evidencia

El experimento 078 ejecutó Excel real mediante COM y Blender real mediante su API
Python en procesos efímeros. Excel calculó `2 + 3 = 5`, limpió el rango y volvió
a cero celdas no vacías. Blender creó un objeto, lo seleccionó, cambió su
posición y restauró el conteo, la selección y el objeto activo originales.

## Consecuencia para el input

El input humano debe convertirse en una transición sólo después de observar el
cambio de estado. Un click, una tecla o una señal de VIZZ son evidencia de
entrada, no equivalentes automáticos de intención. La intención queda como
hipótesis hasta que la transición y su postcondición la respalden.

## Regla de ensamblaje

No mapear `cell → object` por nombre o apariencia. Mapear únicamente:

```text
precondición compatible
→ operación tipada
→ delta observable
→ postcondición verificable
→ reversión disponible
```

La siguiente prueba debe incorporar input humano local y autorizado sobre una
tarea pequeña, manteniendo la misma observación nativa independiente.
