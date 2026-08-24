# Decisión 036 — CODE-INE solo clasifica deriva con objetivo declarado

Fecha: 2026-08-24

## Evidencia

El experimento 026 mantuvo la transición base `c04 → c07` en todos los
perfiles. Una segunda capa produjo:

| Evidencia de objetivo | Clasificación |
|---|---|
| ausente | `unavailable` |
| completa y estable | `stable` |
| completa con descenso | `regressed` |
| completa con descenso y recuperación | `recovered` |
| incompleta | `unavailable` |
| fuera de `[0, 1]` | `rejected` |

La literatura 012 conecta comprensión de código y dificultad con tareas y
medidas humanas específicas, no con un neurotransmisor deducible de logs.

## Decisión

CODE-INE se conserva como descriptor de dos capas:

1. actividad → mejora → repetición, con el envelope mínimo;
2. relación con objetivo, solo si existe una señal completa, acotada y
   declarada.

La segunda capa no convierte `objective_score` en verdad: es una relación
computable sobre un fixture o una fuente de objetivo que todavía debe
verificarse. Sin esa fuente, el sistema debe devolver `unavailable`; no debe
inventar deriva, sedación, ansiedad, codeína ni neurotransmisores.

## Próxima compuerta

Antes de una sesión humana habría que definir un criterio de aceptación
independiente, quién lo verifica y cómo se registra sin texto personal ni
captura cruda. El adaptador VIZZ permanece opt-in y no se activa
automáticamente.
