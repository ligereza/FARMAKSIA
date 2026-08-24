# Resultados — experimento 019

La validación directa y la analogía de cadena de custodia produjeron los
mismos estados en los cuatro casos:

| Caso | Directo | Analogía |
|---|---|---|
| manifiesto válido | válido | válido |
| hash roto | inválido | inválido |
| referencia desconocida | inválido | inválido |
| archivo ausente | inválido | inválido |

El mapeo `sello → sha256` y `entrega → referencia` es una explicación útil,
pero no añade un estado del validador ni una decisión que la ejecución directa
no produzca. Este segundo control negativo, en un dominio diferente al de la
suite, no demuestra novedad independiente para X-ANA-X.

El experimento usó solo manifiestos efímeros de control, sin red, corpus ni
datos humanos. La cadena de custodia no se interpreta como experiencia humana
ni como mecanismo neuroquímico.
