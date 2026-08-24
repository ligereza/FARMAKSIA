# Decisión 007 — instrumento VIZZ listo, eficacia aún desconocida

Fecha: 2026-08-23

## Evidencia

El experimento 003 generó tres condiciones desde el mismo fixture y verificó:

- igualdad de información mediante firma común;
- cuatro ramas presentes en cada vista;
- misma evidencia y valores numéricos;
- ausencia de recomendación automática en el piloto;
- ausencia de llamadas de red;
- sintaxis JavaScript válida;
- procedencia íntegra mediante el validador común.

## Decisión

Adoptar temporalmente HTML/SVG/JavaScript estándar como instrumento de piloto.
No adoptar todavía Vega-Lite, Cytoscape.js, ParaView ni otra dependencia. La
elección evita que un framework introduzca una diferencia que luego se atribuya
erróneamente a VIZZ.

## Lo que no se puede afirmar

La paridad computacional no demuestra mejora perceptual. No hay todavía datos
de personas, por lo que VIZZ no ha sobrevivido ni fallado su kill test.

## Siguiente evidencia

Obtener JSONs exportados por el piloto y analizar por condición:

- duración;
- error según la regla analítica declarada;
- confianza y calibración;
- detección de incertidumbre;
- explicación;
- cambios de decisión.

Una discrepancia con la regla analítica no será tratada automáticamente como
error artístico; debe conservarse la explicación humana.
