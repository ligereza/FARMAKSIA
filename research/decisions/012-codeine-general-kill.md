# Decisión 012 — CODE-INE no demuestra operador independiente

Fecha: 2026-08-23

## Evidencia

El experimento 007 comparó una política CODE-INE amplia con un evaluador
restringido de valor de computación que recibió los mismos datos: ganancia,
costo, reutilización, opción futura, riesgo irreversible y autoridad humana.

La conducta coincidió en `5/6` escenarios. El único desacuerdo apareció cuando
CODE-INE añadió un bono explícito de `0.02` a la reutilización verificada; el
control tenía un empate exacto y conservó la primera acción.

## Decisión

La hipótesis de que CODE-INE integra esas dimensiones de una forma que exige un
operador nuevo no sobrevive el kill test. El comportamiento observado puede
expresarse como metarazonamiento/valor de computación con restricciones y
preferencias parametrizadas.

CODE-INE queda eliminado como operador independiente. El nombre puede quedar
como vocabulario de una política o preferencia de continuación, pero no se
implementará como módulo ni API.

## Alcance y residuo

Esto no demuestra que toda política adaptativa sea reducible en cualquier
dominio. Quedan fuera aprendizaje online, no estacionariedad y preferencias
humanas difíciles de convertir en utilidad. Si se investigan, deberán formular
un control más fuerte y una propiedad que no sea solo un umbral, bono o
desempate.
