# Resultados 003 — preparación del piloto VIZZ

Fecha: 2026-08-23

## Generación

Se generaron tres condiciones desde `decision-state.json` con Python estándar:

- [tabla](conditions/table.html);
- [vista estática](conditions/static.svg);
- [vista interactiva candidata](conditions/vizz.html).

Las tres comparten la firma de información:

`7422A6FB4117FD3C64AFCF8DB2CFCBB03C5578E5919AB96522AC7912CBC93BA4`

## Verificación automática

`verify_conditions.py` produjo:

`CONDITIONS_VALID`

La verificación comprobó:

- tres condiciones registradas;
- cuatro ramas presentes en cada condición;
- mismos valores numéricos;
- misma evidencia textual;
- misma firma del estado normalizado.

El manifiesto de procedencia produjo:

`PROVENANCE_VALID`

con 14 entidades, 6 actividades y 3 consultas.

## Instrumento humano

Se generó [pilot.html](pilot.html), un instrumento local que:

- aleatoriza el orden de las tres condiciones mediante una semilla;
- registra condición, elección, duración, confianza, explicación y detección de
  incertidumbre;
- conserva la firma de información en cada respuesta;
- permite descargar un JSON local;
- no realiza llamadas de red;
- no incluye la respuesta analítica de referencia.

`verify_pilot.py` produjo `PILOT_VALID` y comprobó la sintaxis JavaScript con
Node.

Se añadió [analyze_pilot.py](analyze_pilot.py). Al ejecutarlo sin entrada
produjo `NO_HUMAN_DATA` y no calculó ninguna métrica. Esto confirma que el
laboratorio no convierte la ausencia de participantes en datos sintéticos.

La revisión de accesibilidad estática quedó registrada en
[accessibility-audit.md](accessibility-audit.md). Se corrigieron idioma,
teclado, foco visible, semántica de selección, objetivos táctiles y anuncio de
errores. La validación automática volvió a producir `PILOT_VALID`; las pruebas
con lector de pantalla, zoom y contraste medido siguen pendientes.

La auditoría metodológica detectó además `CARRYOVER_RISK=high`: las tres
condiciones repiten un solo estado. El piloto queda listo como instrumento de
paridad y accesibilidad, pero no para inferencia causal hasta incorporar
conjuntos distintos y balanceados.

## Qué todavía no demuestra

Esto demuestra paridad computacional, no eficacia perceptual. Todavía no hay
datos humanos sobre tiempo, errores, confianza o decisiones. No se puede decir
que VIZZ funcione hasta ejecutar la tarea con participantes y registrar su
autoridad sobre la decisión.

## Riesgo encontrado

La vista interactiva permite ordenar y seleccionar, pero no recomienda una
acción. Si la persona interpreta el ordenamiento como una recomendación
automática, habrá que cambiar el diseño de la interfaz o declarar la condición
inválida.

## Próximo paso

Preparar primero conjuntos distintos y balanceados; después ejecutar un piloto
humano pequeño registrando condición, conjunto, elección, tiempo, confianza,
explicación y si la persona detectó la incertidumbre relevante.
