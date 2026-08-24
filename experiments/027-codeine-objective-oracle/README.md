# Experimento 027 — score declarado versus oracle objetivo CODE-INE

## Pregunta

¿Puede CODE-INE distinguir un objetivo verificado de un score auto-declarado,
un oracle contradictorio, un oracle ausente o un oracle inválido?

## Diseño

Se reutiliza la sesión sintética VIZZ 022 y su transición base `c04 → c07`.
Cada perfil añade dos artefactos separados:

- `objective_scores`: score declarado por el proceso;
- `oracle`: resultado booleano de una aceptación o prueba sintética externa al
  score.

La comparación produce:

- `verified`: score y oracle completo coinciden en `stable`, `regressed` o
  `recovered`;
- `declared_only`: existe score, pero no oracle;
- `conflict`: ambos existen, pero discrepan;
- `unavailable`: oracle ausente o incompleto;
- `rejected`: score/oracle mal formado.

“Externo” significa separado en este fixture; no significa independiente de
todo sesgo ni equivale a evidencia humana.

## Kill tests

- Los artefactos de objetivo no pueden cambiar la transición base `c04 → c07`.
- Un score sin oracle no puede aparecer como `verified`.
- Un conflicto no puede producir un drift verificado.
- Un oracle incompleto debe quedar `unavailable`.
- Un valor que no sea booleano debe ser rechazado.
- No se emiten inferencias humanas, farmacológicas o neuroquímicas.

Ejecutar:

```text
python experiments/027-codeine-objective-oracle/run_experiment.py
python experiments/027-codeine-objective-oracle/run_kill_test.py
```
