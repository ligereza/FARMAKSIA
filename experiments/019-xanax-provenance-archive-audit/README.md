# Experimento 019 — auditoría final de novedad X-ANA-X

Fecha: 2026-08-24

## Pregunta

¿Una analogía de cadena de custodia produce una decisión adicional frente a la
validación directa de procedencia ya implementada en
`research/tools/validate_provenance.py`?

## Diseño

El control directo ejecuta el validador sobre cuatro casos mínimos: manifiesto
válido, hash roto, referencia desconocida y archivo ausente. La ruta X-ANA-X
mapea `objeto → entidad`, `sello → sha256`, `entrega → referencia` y predice
qué casos deben detenerse.

La comparación solo considera ganancia si la ruta analógica produce un estado
o una decisión que la validación directa no produce. Las entradas temporales se
crean en un directorio efímero durante la ejecución; no son corpus ni datos
humanos.

## Kill test final

Si los cuatro estados directos y analógicos coinciden, la analogía no demuestra
una capacidad nueva en este dominio. Si el validador acepta hash roto,
referencia desconocida o archivo ausente, la frontera de procedencia queda
rota y el experimento falla.

No se usan red, participantes, intoxicación, modelos generativos ni corpus
arbitrarios.

Ejecutar:

```text
python experiments/019-xanax-provenance-archive-audit/run_experiment.py
python experiments/019-xanax-provenance-archive-audit/run_kill_test.py
```
