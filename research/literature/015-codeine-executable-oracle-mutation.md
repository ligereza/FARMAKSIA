# Investigación 015 — CODE-INE, oracle ejecutable y mutation testing

Fecha: 2026-08-24

## De score declarado a aceptación ejecutable

La encuesta de Barr et al. describe especificaciones, contratos y modelos como
rutas para automatizar el problema del oráculo; también advierte que una
especificación informal puede seguir dependiendo de una persona:

- [The Oracle Problem in Software Testing: A Survey](https://discovery.ucl.ac.uk/id/eprint/1471263/)

El experimento 027 ya separó el score del oracle, pero sus valores booleanos
eran declarados directamente en `cases.json`. Eso permite probar la compuerta
de procedencia, no la sensibilidad del oracle a una falla concreta.

El experimento 029 agrega una especificación JSON independiente y un módulo
ejecutable que inspecciona los eventos. La especificación exige IDs, acción,
ganancia y errores; el runner produce la aceptación por evento y deriva
`stable`, `regressed` o `recovered` sin leer `objective_scores`.

## Mutation testing

Mutation testing introduce cambios pequeños y deliberados para comprobar si
una suite los detecta. La revisión de Jia y Harman lo trata como un criterio de
adecuación de tests, no como una prueba de verdad del dominio:

- [An Analysis and Survey of the Development of Mutation Testing](https://doi.org/10.1109/TSE.2010.62)
- [Mutation Testing Repository](https://mutationtesting.uni.lu/)

Para adoptar una herramienta externa se consideró [mutmut](https://mutmut.readthedocs.io/en/latest/): es una herramienta open source de
mutation testing para Python, pero su propia documentación indica que necesita
fork y debe ejecutarse en WSL. FARMAXIA mantiene por ahora un mutador explícito
de fixtures con la biblioteca estándar para que el ciclo sea portable,
inspeccionable y no introduzca dependencia.

## Límite epistemológico

Un oracle ejecutable puede demostrar que una traza sintética satisface una
especificación de tarea y que ciertas mutaciones son detectadas. No demuestra
que la especificación represente comprensión, ansiedad, sedación, intoxicación,
neurotransmisores ni una experiencia humana. La decisión de aceptación sigue
siendo válida solo dentro del fixture y su contrato.
