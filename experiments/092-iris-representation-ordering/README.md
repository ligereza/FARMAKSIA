# Experimento 092 — adaptador IRIS para ordenación de representaciones

Este experimento define el contrato explícito entre IRIS y FARMAKSIA. IRIS
privado conserva el motor de composición, sus superficies y su verificador
independiente. FARMAKSIA sólo recibe una representación semántica portable; no
reimplementa la semántica de IRIS ni convierte una preferencia estética en
verdad.

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
python experiments/092-iris-representation-ordering/run_experiment.py
python experiments/092-iris-representation-ordering/run_contract_test.py
```

El motor y las superficies de IRIS no se copian al archivo público. La
referencia privada se verifica en su propio repositorio; aquí sólo queda el
contrato, un fixture sintético y el adaptador que permite replay offline.

## Evidencia y continuidad

- [integration-report.md](integration-report.md): progreso, alcance y resultado.
- [dependency-matrix.md](dependency-matrix.md): dependencias y límites portables.
- [provenance.json](provenance.json): manifiesto de procedencia del experimento.
- [continuation-proposal.md](continuation-proposal.md): siguiente bloque propuesto.

## Kill tests

El contrato bloquea selección inexistente, IDs de fuente ausentes, orden
autoral alterado, verificación independiente ausente y afirmaciones de
optimalidad estética. El fixture es sintético y no activa red, cámara, APIs ni
ejecución externa.
