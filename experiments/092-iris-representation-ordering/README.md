# Experimento 092 — adaptador IRIS para ordenación de representaciones

Este experimento integra IRIS como módulo explícito de ordenación/edición de
representaciones dentro de FARMAKSIA. IRIS conserva el motor de composición,
la CLI, el servidor, el cliente y su verificador independiente. FARMAKSIA
recibe una representación semántica portable; no reimplementa la semántica de
IRIS ni convierte una preferencia estética en verdad.

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

La carpeta `iris_reference` conserva el motor y superficies exportables de
IRIS, junto con su fixture y documentación. No incluye `node_modules`,
salidas generadas ni rutas locales. Para repetir sus pruebas en la referencia:

```powershell
npm ci --prefix experiments/092-iris-representation-ordering/iris_reference
npm run check --prefix experiments/092-iris-representation-ordering/iris_reference
npm test --prefix experiments/092-iris-representation-ordering/iris_reference
npm run smoke --prefix experiments/092-iris-representation-ordering/iris_reference
```

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

