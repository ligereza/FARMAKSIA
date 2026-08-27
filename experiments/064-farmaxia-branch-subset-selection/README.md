# Experimento 064 — selección de subset de ramas

## Pregunta

¿Cómo elegir pocas ramas visibles sin tratar cuatro alternativas como una ley
cognitiva ni convertir la primera interacción en un ranking de autoridad?

## Método

El selector mantiene `plan-full` como ancla y añade ramas mediante una función
de cobertura marginal ponderada por necesidad semántica menos costo de display:

```text
objective(S) = coverage(S) - display_cost_penalty × display_cost(S)
```

Se detiene cuando no queda presupuesto, se alcanza el máximo visible o la
ganancia marginal no supera el umbral. Las ramas descartadas permanecen
recuperables. MMR se calcula únicamente como diagnóstico de redundancia, no como
orden final ni como predicción de “mejor rama”.

El candidato sólo puede participar si conserva el contrato de consultas críticas
de 063.

## Reproducir

```powershell
python experiments/064-farmaxia-branch-subset-selection/run_experiment.py
python experiments/064-farmaxia-branch-subset-selection/run_contract_test.py
python experiments/064-farmaxia-branch-subset-selection/run_kill_test.py
```

Con el fixture actual se seleccionan `full`, `map`, `sequence` y `oracle` con un
costo total 5.6; `analogy`, `focus` y la rama redundante quedan disponibles.

## Límite

Los pesos, costos y necesidades son sintéticos. El algoritmo demuestra una
política auditable de selección, no el número óptimo de ramas para una persona ni
una medida de carga cognitiva. Eso exige evaluación humana con tareas y orden
contrabalanceados.
