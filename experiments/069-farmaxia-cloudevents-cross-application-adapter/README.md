# Experimento 069 — adapter CloudEvents entre aplicaciones

## Objetivo

Comprobar que el sobre estándar del experimento 068 puede alimentar el puente
GitLab–Mattermost del 065 sin perder identidad, procedencia ni controles de
seguridad.

## Método

El adapter lee el fixture CloudEvents local, traduce `data` y las extensiones
namespaced al contrato interno y reutiliza el compilador 065. No copia su
lógica: lo llama como una pieza ya verificada.

```text
CloudEvents 068 → adapter → contrato FARMAKSIA → puente 065 → Mattermost dry-run
```

## Analogía

El 068 comprobó que el sobre está bien cerrado. El 069 comprueba que una
persona puede sacar la carta del sobre y entregarla en otra oficina sin
cambiar el destinatario ni inventar el contenido.

## Resultado esperado

```text
CROSS_APPLICATION_CLOUDEVENTS_ADAPTER_VERIFIED
CloudEvents: 4 entregas → 3 eventos únicos → 1 duplicado
puente GitLab–Mattermost: verificado en DRY_RUN_ONLY
```

## Reproducir

```powershell
python experiments/069-farmaxia-cloudevents-cross-application-adapter/run_experiment.py
python experiments/069-farmaxia-cloudevents-cross-application-adapter/run_contract_test.py
python experiments/069-farmaxia-cloudevents-cross-application-adapter/run_kill_test.py
```

## Límite

Es un adapter local y sintético. No contacta GitLab ni Mattermost, no publica
mensajes, no ejecuta escrituras y no prueba compatibilidad con sus APIs reales.
Tampoco convierte CloudEvents en verdad: el verificador y los contratos
065–067 siguen siendo necesarios.
