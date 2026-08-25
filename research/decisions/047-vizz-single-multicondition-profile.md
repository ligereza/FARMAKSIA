# ADR-047 — VIZZ: un perfil único para lentes y sin lentes

## Estado

Aceptada.

## Decisión

VIZZ no alternará entre dos perfiles durante el runtime. La calibración
visible ejecutará dos sesiones estáticas dentro del mismo flujo:

1. `with_glasses`;
2. `without_glasses`.

Cada condición repite los 12 puntos, para un total de 24 observaciones
agregadas. El perfil resultante se sella una sola vez y el runtime utiliza ese
perfil sin pedir al usuario que seleccione la condición.

Si ya existe un perfil `0.3` de una sola condición, el flujo incremental
captura únicamente la condición faltante. El perfil legado se carga con su
condición declarada explícitamente, se concatenan las observaciones por punto
y se vuelve a ajustar un único mapper. No se promedian coeficientes de dos
modelos, porque eso no equivale en general al ajuste sobre los datos reunidos.

La condición queda registrada como metadato de auditoría, pero no se entrega
como entrada al mapper: en funcionamiento normal VIZZ no debe depender de que
el sistema conozca si el usuario lleva lentes. El modelo aprende una
transformación común a ambas distribuciones.

## Motivo

Los lentes pueden cambiar reflejos, contraste, visibilidad del iris y la
apariencia de los ojos. Guardar las dos sesiones permite medir si una
transformación común es suficiente. Si el ajuste conjunto empeora, eso será
evidencia de que la representación actual no es suficientemente invariante;
no se resolverá ocultando el problema mediante dos perfiles seleccionables.

## Contratos

- El perfil `0.4` exige ambas condiciones y al menos 24 muestras agregadas.
- Las dos sesiones usan la misma cámara, pantalla y protocolo temporal.
- La UI solicita explícitamente retirar o mantener los lentes antes de la
  segunda sesión.
- Una sesión legado puede actualizarse con `--merge-existing` sin repetirse.
- Un perfil legado sin condición explícita no se fusiona: el sistema exige que
  el operador declare si fue `with_glasses` o `without_glasses`.
- El runtime sigue siendo headless y utiliza un único archivo.
- La validación debe reportar error separado por condición y error conjunto.

## Límites

Esto no demuestra invariancia frente a otras monturas, reflejos, iluminación,
distancia o prescripción óptica. Tampoco convierte el sistema en un instrumento
clínico. Si una sola transformación no generaliza, el siguiente paso será
mejorar las características o añadir una adaptación aprendida que no requiera
selección manual de perfil.
