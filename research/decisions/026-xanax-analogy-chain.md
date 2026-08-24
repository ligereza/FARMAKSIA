# Decisión 026 — X-ANA-X necesita predicción y ruptura declaradas

Fecha: 2026-08-24

## Evidencia

El experimento 017 ejecutó la cadena `confusión → laguna → búsqueda → fuente →
mapeo → predicción → verificación → ruptura` sobre fixtures locales.

La búsqueda por señales seleccionó una tarjeta de intervalos sobre una tarjeta
de contención estática. El mapeo predijo `left-region` como región activa en
`t=0.25`; la consulta objetivo confirmó la predicción y la intersección con el
centro. Cuando se pidió una relación geométrica `right_of_center`, la fuente
no pudo transferirla y el runner devolvió no disponible, aunque el dominio
objetivo sí podía verificarla.

## Decisión

X-ANA-X queda como contrato de transferencia verificable, no como sinónimo de
explicación, búsqueda o cambio de consulta:

`fuente seleccionada → relaciones conservadas → predicción → prueba → residuo`

La búsqueda mejora la selección de fuente solo dentro del catálogo declarado.
No se presenta como evidencia de comprensión ni de novedad conceptual; la
frontera con reformulación y state augmentation sigue abierta.

## Kill tests

Sin eventos la consulta temporal queda no disponible. La fuente estática no
puede responderla. La analogía no puede inventar geometría ausente en su
mapeo. Estos límites pasan en la ejecución 017.

## Próximo objetivo

Aplicar la misma cadena a un problema pequeño real del propio repositorio con
una fuente documental primaria explícita, manteniendo la verificación local y
sin descargar ni incorporar corpus creativo. Si la transferencia no cambia
ninguna decisión frente a una reformulación ordinaria, X-ANA-X deberá
fusionarse con ese control.
