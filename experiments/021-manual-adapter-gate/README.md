# Experimento 021 — compuerta del adaptador manual VIZZ

Fecha: 2026-08-24

## Pregunta

¿Puede prepararse un adaptador manual local que requiera consentimiento
explícito, valide solo eventos abstractos y no cree una sesión durante el
desarrollo o el dry-run?

## Contrato operativo

- Sin `--consent`, el proceso se bloquea antes de parsear eventos y no escribe.
- Con `--consent`, solo se acepta el envelope VIZZ `task_events_only`.
- `--dry-run` valida pero nunca escribe.
- Las salidas existentes no se sobreescriben y el directorio padre debe existir.
- No hay captura automática: el adaptador recibe eventos JSON abstractos
  entregados deliberadamente por el usuario.

La herramienta queda preparada, pero este experimento no la ejecuta para crear
una sesión real. Los tests usan temporales efímeros y fixtures sintéticos.

## Kill tests

- Consentimiento ausente: `ADAPTER_BLOCKED` y cero archivo de salida.
- Campo crudo: rechazo por el validador VIZZ.
- Archivo de salida existente: rechazo sin sobreescritura.
- Dry-run: validación exitosa con `output_not_written=true`.

Ejecutar:

```text
python experiments/021-manual-adapter-gate/run_experiment.py
python experiments/021-manual-adapter-gate/run_kill_test.py
```
