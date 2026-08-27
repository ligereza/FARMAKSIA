# Resultados — experimento 080

## Evidencia local

En Excel real, el modo scratch observó esta secuencia sin guardar archivos:

```text
create_entity → modify_property → revert
```

El correlacionador produjo tres `unassociated_native_delta` porque no se
introdujo ningún input humano en esa ejecución. Esa salida es deliberada: no
convierte una mutación controlada por el laboratorio en actividad humana.

El modo `live-excel` queda preparado para una sesión abierta. Si encuentra una
única observación de teclado de la misma aplicación dentro de 750 ms antes de
un delta, informa `candidate_association`; si hay dos o más, informa
`ambiguous_association`.

## Interpretación

El input ya puede ser motor de aprendizaje sin ser un oráculo de intención:

```text
input observado + contexto
→ ventana temporal
→ delta nativo
→ asociación candidata
```

La postcondición del estado sigue siendo la evidencia fuerte. La proximidad
temporal sólo decide qué hipótesis vale la pena revisar.

## Desconocido

- si una asociación candidata se mantiene con interacción humana rápida;
- si Excel expone suficiente granularidad para distinguir editar, navegar y
  seleccionar sólo con snapshots sin contenido;
- cómo implementar el mismo snapshot live dentro de Blender sin depender de
  screenshots;
- cuánto retardo existe entre input físico, evento UIA y delta nativo.
