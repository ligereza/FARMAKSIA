# Experimento 093 — adaptador IRIS para ordenación de representaciones

Este experimento define un contrato de investigación para transferir una
composición IRIS a FARMAKSIA. FARMAKSIA sólo recibe una representación
semántica portable; no contiene la aplicación editorial, no reimplementa su
semántica ni convierte una preferencia estética en verdad.

## Contrato

El adaptador conserva IDs de proyecto, obra, registros y contexto; distingue
`work`, `record` y `context`; preserva el orden autoral, restricciones,
preferencias, alternativas, estado (`OPTIMAL`, `FEASIBLE`, `INFEASIBLE`,
`UNKNOWN`) y procedencia. Sólo admite el resultado cuando el plan declara
verificación independiente exitosa y el orden coincide con el orden autoral.

`OPTIMAL` significa óptimo respecto del objetivo y restricciones declarados por
IRIS. No significa que FARMAKSIA haya probado calidad estética, aprendizaje o
preferencia humana.

## Reproducir

```powershell
python experiments/093-iris-representation-ordering/run_experiment.py
python experiments/093-iris-representation-ordering/run_contract_test.py
```

El runtime de la aplicación IRIS no es una dependencia de FARMAKSIA. Se incluye
una referencia portable autocontenida en [iris_reference](iris_reference/),
para que el experimento conserve el motor, CLI, servidor, pruebas, contrato y
fixtures que originaron la integración. La referencia no incluye
`node_modules/`, salidas generadas ni directorios de trabajo; FARMAKSIA sigue
siendo investigativo y no ejecuta IRIS como parte de su propio runtime.

Los fixtures `mak-*-sample.json` conservan IDs y procedencia de metadatos
observados en MAK, pero no copian medios privados. “Sintético” describe la
composición de prueba y sus medios demo, no una sustitución de los IDs de
procedencia.

## Evidencia y continuidad

- [integration-report.md](integration-report.md): progreso, alcance y resultado.
- [dependency-matrix.md](dependency-matrix.md): dependencias y límites portables.
- [provenance.json](provenance.json): manifiesto de procedencia del experimento.
- [continuation-proposal.md](continuation-proposal.md): siguiente bloque propuesto.
- [iris_reference/README.md](iris_reference/README.md): fuente portable y su
  límite de ejecución.

## Kill tests

El contrato bloquea selección inexistente, IDs de fuente ausentes, orden
autoral alterado, verificación independiente ausente y afirmaciones de
optimalidad estética. El fixture es sintético y no activa red, cámara, APIs ni
ejecución externa.
