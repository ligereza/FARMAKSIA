# Experimento 066 — replay temporal de evidencia

## Pregunta

¿Puede una capa reconstruir el estado de una fuente sin hacer que el orden de
llegada sea la verdad, conservando correcciones, retractaciones, conflictos y
desconocidos?

## Método

El fixture usa un ledger sintético GitLab–Mattermost de sólo lectura. Cada
evento conserva `source_version`, `valid_time`, `observed_at`, `root_id` y
procedencia. El replay:

1. deduplica por `event_id` sin sumar evidencia repetida;
2. conserva todas las entregas únicas en el historial;
3. aplica retractaciones después de reunir el ledger completo;
4. usa la versión de fuente para formar la proyección;
5. expresa dos valores distintos en la misma versión como `CONFLICT`;
6. expresa falta de autoridad temporal como `UNKNOWN`;
7. compara varias permutaciones y exige la misma proyección.

## Resultado que se busca

Una merge request pasa de abierta a fusionada; un pipeline corregido pasa de
fallido a exitoso, pero el evento fallido permanece como `RETRACTED`; un
deployment con dos valores de la misma versión permanece en `CONFLICT`; una
observación sin versión ni tiempo válido queda en `UNKNOWN`.

## Reproducir

```powershell
python experiments/066-farmaxia-temporal-evidence-replay/run_experiment.py
python experiments/066-farmaxia-temporal-evidence-replay/run_contract_test.py
python experiments/066-farmaxia-temporal-evidence-replay/run_kill_test.py
```

## Límite

Esto es un replay batch determinista, no un motor distribuido ni una prueba de
consenso. Todavía no resuelve watermarks, ventanas de eventos en vivo,
particiones, firmas, reintentos transaccionales ni cambios concurrentes reales.
