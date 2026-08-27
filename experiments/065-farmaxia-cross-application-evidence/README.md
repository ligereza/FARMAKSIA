# Experimento 065 — evidencia entre aplicaciones

## Pregunta

¿Puede una capa adaptativa unir dos superficies existentes sin copiar una
aplicación dentro de la otra, perder la identidad de sus entidades o declarar
éxito porque una representación lo afirma?

## Par elegido

El fixture representa un flujo GitLab–Mattermost: GitLab es la fuente de verdad
para una merge request y su pipeline; Mattermost es la superficie destino para
una notificación contextual. No se contactan servidores reales y no se usan
datos humanos.

## Qué demuestra

- deduplicación por `event_id` sin perder el registro de entregas;
- orden canónico de eventos recibidos fuera de orden;
- identidad calificada por instancia, proyecto, tipo e ID;
- claims de representación con referencias a la fuente;
- propuesta de acción con precondiciones, confirmación y `dry_run`;
- verificación independiente contra el estado sintético de GitLab;
- bloqueo ante identidad incompleta, conflicto, permiso ausente, versión vieja,
  pérdida de procedencia o éxito no observado.

El experimento no demuestra interoperabilidad productiva, comprensión humana ni
que Mattermost pueda operar GitLab sin configuración institucional. Demuestra un
contrato mínimo para que el siguiente adaptador no sea un chatbot que resume,
sino un compilador auditable de representación.

## Reproducir

```powershell
python experiments/065-farmaxia-cross-application-evidence/run_experiment.py
python experiments/065-farmaxia-cross-application-evidence/run_contract_test.py
python experiments/065-farmaxia-cross-application-evidence/run_kill_test.py
```

La salida positiva esperada es `CROSS_APPLICATION_EVIDENCE_VERIFIED`. La acción
queda en `DRY_RUN_ONLY`; ningún mensaje se publica ni se ejecuta una escritura.
