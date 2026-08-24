# Decisión 016 — diseño VIZZ contrabalanceado aprobado para piloto

Fecha: 2026-08-23

## Evidencia

El experimento 009 genera y verifica tres conjuntos de estímulos distintos y
tres rotaciones de asignación. Cada sesión registra condición, conjunto, orden,
firma del conjunto, confianza, duración, explicación y detección de
incertidumbre. La verificación confirma `BALANCED_PILOT_VALID`; el análisis sin
exportación confirma `NO_HUMAN_DATA`.

## Decisión

La versión 0.2 reemplaza a la versión 0.1 como instrumento candidato para
recoger datos humanos. El diseño elimina la confusión obvia por repetir un
único estado, pero no demuestra todavía un efecto de VIZZ.

No se permite combinar datos de las versiones 0.1 y 0.2 en un mismo análisis.

## Condiciones de interpretación

- comprobar que la asignación de conjuntos quede balanceada entre personas;
- incluir conjunto y orden en cualquier análisis;
- conservar autoridad humana y explicaciones sin reinterpretarlas como valor
  artístico;
- detener la recolección si aparece un fallo de paridad, accesibilidad o
  identificabilidad.

El siguiente resultado válido requiere al menos una exportación humana real y
una revisión de datos antes de calcular métricas agregadas.
