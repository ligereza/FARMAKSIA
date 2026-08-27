# Experimento 071 — adapter CODE-INE para patches

## Objetivo

Auditar una tercera superficie, distinta de documentos institucionales:
eventos de un cambio de código hacia un workspace de editor.

## Método

El fixture es sintético. CODE-INE reutiliza el mismo
`research/tools/cloudevents_contract.py` que los casos 068–070 y añade sólo la
semántica que el código necesita: archivo destino, hash base, check
independiente, precondición de revisión y prohibición de ejecutar el patch.

```text
code-host sintético → CloudEvents común → CODE-INE → editor preview/dry-run
                                      ↘ oracle del patch
```

También repite el procesamiento con tres órdenes de llegada. La secuencia
canónica debe ser la misma aunque el evento de check llegue antes o después.

## Analogía

El mismo sistema de sobres sirve para transportar un cambio de código, pero la
carta tiene una regla nueva: antes de mostrar un patch hay que comprobar que
apunta al archivo correcto y parte del hash correcto. No se ejecuta el código
para “ver si funciona”.

## Resultado esperado

```text
CODEINE_CLOUDEVENTS_ADAPTER_VERIFIED
4 entregas → 3 eventos únicos → 1 duplicado
patch: preview DRY_RUN_ONLY, sin ejecución
```

## Reproducir

```powershell
python experiments/071-farmaxia-codeine-patch-adapter/run_experiment.py
python experiments/071-farmaxia-codeine-patch-adapter/run_contract_test.py
python experiments/071-farmaxia-codeine-patch-adapter/run_kill_test.py
```

## Límite

No se descarga ni ejecuta código, no se contacta un repositorio, no se escribe
en un workspace real y no se prueba compilación, seguridad del patch ni
compatibilidad con APIs de Git. El oracle sólo verifica el contrato sintético.
