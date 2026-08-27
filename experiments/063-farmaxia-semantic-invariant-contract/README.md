# Experimento 063 — SemanticInvariantContract

## Pregunta

¿Las distintas ramas de `RepresentationSpace` conservan las respuestas
semánticas críticas de una misma fuente, aunque cambien orden, analogía,
densidad o geometría visual?

## Método

El fixture define una fuente `G`, seis consultas críticas y cuatro vistas que
corresponden a las ramas de 062. Cada consulta se ejecuta contra la fuente y
contra cada vista. La comparación es relativa al contrato de consultas; no se
pretende demostrar isomorfismo visual ni conservar toda la información posible.

Se verifican cuatro invariantes adicionales:

- referencias estables para entidades y relaciones;
- tipo y extremos de relaciones críticas;
- `UNKNOWN` no se transforma en `FACT` sin evidencia;
- cada relación o claim visible conserva procedencia.

## Reproducir

```powershell
python experiments/063-farmaxia-semantic-invariant-contract/run_experiment.py
python experiments/063-farmaxia-semantic-invariant-contract/run_contract_test.py
python experiments/063-farmaxia-semantic-invariant-contract/run_kill_test.py
```

El resultado esperado es `query_preservation_rate=1.0`,
`semantic_hallucination_rate=0.0`, `unknown_escalation_rate=0.0` y
`provenance_completeness=1.0`.

## Límite

La prueba demuestra preservación computable en un corpus sintético pequeño. No
demuestra que las vistas sean comprensibles, útiles o preferibles para una
persona. `round_trip_loss` queda `null` porque este fixture no es editable; las
leyes de lenses pertenecen a una futura rama editable.
