# Experimento 070 — adapter documental OpenEMR–Nextcloud

## Objetivo

Demostrar que el mismo núcleo CloudEvents, evidencia, procedencia, permisos y
verificación funciona con otra pareja de superficies: una fuente institucional
documental sintética y una carpeta de Nextcloud.

## Método

El fixture contiene sólo registros sintéticos. El adapter reutiliza
`research/tools/cloudevents_contract.py`, transforma los eventos a claims
documentales y verifica la fuente OpenEMR sintética antes de proponer una
acción de organización en Nextcloud. También repite el procesamiento con tres
órdenes de llegada y exige la misma secuencia canónica.

```text
OpenEMR sintético → CloudEvents común → adapter documental → Nextcloud dry-run
                                      ↘ verificador independiente
```

No se reutiliza una integración GitLab disfrazada: cambia la superficie, los
tipos de entidad y la acción, pero el núcleo de identidad, tiempo, procedencia,
`UNKNOWN`/bloqueo y seguridad permanece compartido.

## Analogía

El 069 probó que una carta puede viajar entre dos oficinas técnicas. Este 070
prueba que el mismo sobre sirve para una carpeta institucional: cambia el tipo
de documento, no las reglas para saber quién lo envió ni si está respaldado.

## Resultado esperado

```text
DOCUMENTAL_CLOUDEVENTS_ADAPTER_VERIFIED
OpenEMR: 4 entregas → 3 eventos únicos → 1 duplicado
Nextcloud: propuesta DRY_RUN_ONLY con verificación independiente
```

## Reproducir

```powershell
python experiments/070-farmaxia-openemr-nextcloud-adapter/run_experiment.py
python experiments/070-farmaxia-openemr-nextcloud-adapter/run_contract_test.py
python experiments/070-farmaxia-openemr-nextcloud-adapter/run_kill_test.py
```

## Límite

No se contactan OpenEMR ni Nextcloud reales, no se usan datos clínicos, no se
publican documentos y no se prueba compatibilidad con sus APIs, autenticación,
firmas, schema registry ni transacciones externas.
