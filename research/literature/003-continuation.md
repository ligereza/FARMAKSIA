# Literatura 003 — CODE-INE: continuación frente a scheduling

## Antecedentes conceptuales

1. **Anytime algorithms:** producir una solución utilizable en cualquier
   momento y mejorarla si queda tiempo.
2. **Optimal stopping:** decidir cuándo el valor esperado de continuar deja de
   compensar el costo.
3. **Metarazonamiento:** asignar recursos al propio proceso de pensar o buscar.
4. **Explore/exploit y bandits:** equilibrar información nueva frente a
   aprovechar una alternativa conocida.
5. **Algorithm selection y bounded rationality:** elegir procedimientos bajo
   recursos y conocimiento limitados.

## Líneas bibliográficas

- [Zilberstein, Operational Rationality through Compilation of Anytime Algorithms](https://onlinelibrary.wiley.com/doi/10.1609/aimag.v16i2.1136): relaciona perfiles de rendimiento, tiempo y asignación de recursos.
- [Lin, Kolobov, Kamar y Horvitz, Metareasoning for Planning Under Uncertainty](https://ocs.aaai.org/ocs/index.php/IJCAI/IJCAI15/paper/download/11455/10885): formula el costo de planificar y el valor de mejorar la política.
- [Bhatia et al., Tuning the Hyperparameters of Anytime Planning](https://ojs.aaai.org/index.php/ICAPS/article/view/19842): utiliza metarazonamiento y aprendizaje para decidir recursos y stopping.
- [On Explore-then-Commit Strategies](https://papers.neurips.cc/paper/6179-on-explore-then-commit-strategies.pdf): muestra que imponer una fase rígida de exploración y luego compromiso puede ser subóptimo.

## Open source relevante

- [ASlib](https://github.com/coseal/aslib_data): escenarios para selección de algoritmos.
- [SMAC3](https://github.com/automl/SMAC3): optimización, racing y evaluación multifidelidad.
- [PyXAB](https://github.com/WilliamLwj/PyXAB): bandits y optimización online.
- [Open Bandit Pipeline](https://github.com/st-tech/zr-obp): políticas y evaluación offline.

## Hipótesis para FARMAKSIA

CODE-INE solo se diferencia de scheduling si puede elegir una acción de
continuación que cambie la trayectoria del proceso: continuar, detener,
reutilizar, cambiar de rama o descansar. Un scheduler que solo reordena tareas
predeclaradas no satisface esta definición.

## Kill test

Comparar un scheduler FIFO, un priority scheduler y una política de
continuación en escenarios con dead-end, reuse credit y stopping. Si todas las
ganancias de la política se explican por reordenar la misma cola, CODE-INE se
absorbe en scheduling/metarazonamiento existente.
