# Decisión 005 — CODE-INE sobrevive una frontera operacional

Fecha: 2026-08-23

## Evidencia

Se compararon FIFO y priority —ambos restringidos a una cola fija— contra una
política que pudo elegir continuar, reutilizar, cambiar de rama o detenerse.

Resultados de utilidad media:

- FIFO: `0.4475`;
- priority: `0.5700`;
- continuation-candidate: `0.6425`.

La candidata solo coincidió con los baselines en `deep-path`, donde continuar
era correcto. En `dead-end` cambió de rama; en `reuse-credit` combinó
reutilización y cambio; en `stop-now` no consumió presupuesto.

## Decisión

CODE-INE sobrevive provisionalmente como una frontera operacional respecto de
un scheduler de orden fijo. La definición requiere estado del proceso, acciones
semánticas, costo, valor esperado y posibilidad de modificar la trayectoria.

Esto no demuestra una teoría nueva. La literatura de metarazonamiento, optimal
stopping, anytime algorithms y algorithm selection sigue siendo el mejor
análogo existente.

## Kill test siguiente

Agregar un scheduler dinámico capaz de crear o activar `switch_B`, y un
controlador de valor de computación. Si reproducen las mismas decisiones y
utilidad, CODE-INE se fusiona con metarazonamiento existente.

## Estado de adopción

El experimento usa únicamente Python estándar y el validador común de
procedencia. No se adopta todavía ASlib, SMAC3 ni un framework de bandits: el
fixture es pequeño y la hipótesis necesita una comparación conceptual antes de
escalar.
