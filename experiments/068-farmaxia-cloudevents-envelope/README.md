# Experimento 068 — sobre CloudEvents sin infraestructura

## Pregunta

¿Podemos usar un formato consolidado para transportar eventos sin perder la
identidad, la procedencia y el contrato interno de FARMAKSIA?

## Método

El fixture reutiliza el escenario sintético GitLab–Mattermost de los contratos
065–067, pero expresa sus eventos dentro de un sobre CloudEvents 1.0. Se
prueba que:

- `source + id` identifica el evento y una entrega repetida no suma evidencia;
- el orden de llegada puede ser distinto del orden temporal;
- `data` conserva el evento que FARMAKSIA necesita interpretar;
- extensiones namespaced conservan entidad, versión, observación y raíz de
  procedencia;
- un `subject` o identidad que ya no corresponde queda bloqueado;
- el sobre original permanece disponible para auditoría.

## Analogía

CloudEvents es el sobre común. FARMAKSIA sigue siendo el sistema que lee la
carta, comprueba a qué proyecto pertenece y decide si lo que dice está
respaldado. Cambiar el sobre no cambia la verdad del contenido.

## Reproducir

```powershell
python experiments/068-farmaxia-cloudevents-envelope/run_experiment.py
python experiments/068-farmaxia-cloudevents-envelope/run_contract_test.py
python experiments/068-farmaxia-cloudevents-envelope/run_kill_test.py
```

## Resultado esperado

```text
CLOUDEVENTS_ENVELOPE_VERIFIED
raw=4, unique=3, duplicate=1
canonical_order=ev-mr-open → ev-pipeline-fail → ev-mr-comment
```

## Límite

Es una validación local y sintética. No implementa broker, red, firma,
schema registry, exactly-once, autenticación ni interoperabilidad productiva.
CloudEvents normaliza el transporte; no verifica que una afirmación sea
verdadera. El replay, los conflictos, `UNKNOWN` y el verificador de FARMAKSIA
siguen siendo necesarios.
