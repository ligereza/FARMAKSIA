# Resultados 070 — adapter documental OpenEMR–Nextcloud

**Fecha de ejecución:** 2026-08-27  
**Estado:** `DOCUMENTAL_CLOUDEVENTS_ADAPTER_VERIFIED`

## Evidencia obtenida

- una segunda superficie institucional usó el mismo núcleo
  `research/tools/cloudevents_contract.py`;
- 4 entregas OpenEMR sintéticas se redujeron a 3 eventos únicos y 1 duplicado;
- el orden canónico se reconstruyó como `ev-patient-context`,
  `ev-care-plan-published`, `ev-document-ready`;
- los claims documentales conservaron referencias a las entidades fuente;
- la propuesta para organizar el documento en Nextcloud permaneció en
  `DRY_RUN_ONLY` y requirió confirmación;
- la fuente sintética, el estado del plan, el documento y el permiso de destino
  pasaron verificación independiente;
- los 8 kill tests bloquearon evento faltante, superficie equivocada,
  procedencia ausente, escritura externa, permiso ausente, precondición vieja,
  snapshot alterado y política de datos humanos.

## Interpretación

El cambio de dominio —de GitLab–Mattermost a OpenEMR–Nextcloud— no obligó a
crear otro validador de eventos. Cambiaron las entidades, claims y acción; las
reglas de identidad, procedencia, deduplicación y seguridad permanecieron en
el núcleo común.

## Seguridad y alcance

No hubo red, escritura externa, datos clínicos, cámara ni ejecución externa. El
resultado no demuestra compatibilidad con las APIs reales, autenticación,
firmas, schema registry, transacciones ni aprobación clínica.

## Siguiente objetivo

Auditar si el mismo núcleo puede soportar una superficie no institucional y no
documental —por ejemplo código o media— sin añadir abstracciones prematuras.
Sólo se hará si la auditoría encuentra una diferencia semántica real.
