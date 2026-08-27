# Resultados 068 — sobre CloudEvents

**Fecha de ejecución:** 2026-08-27  
**Estado:** `CLOUDEVENTS_ENVELOPE_VERIFIED`

## Evidencia obtenida

- 4 entregas recibidas;
- 3 eventos únicos;
- 1 entrega repetida detectada por `source + id`;
- el orden de llegada fue distinto del orden temporal;
- el orden canónico reconstruido fue `ev-mr-open`, `ev-pipeline-fail`,
  `ev-mr-comment`;
- identidad, `subject`, versión, observación y raíz de procedencia llegaron al
  contrato interno de FARMAKSIA;
- los sobres originales quedaron retenidos para auditoría;
- los 8 kill tests bloquearon versiones incompletas, identidades despegadas,
  extensiones sin namespace, duplicados con contenido distinto y política de
  red habilitada.

## Interpretación

CloudEvents sirve como formato de transporte para FARMAKSIA. No reemplaza el
replay, la procedencia de claims, los conflictos, `UNKNOWN` ni el verificador
independiente.

## Seguridad y alcance

No hubo red, escritura externa, datos humanos, cámara ni ejecución externa. El
resultado no demuestra integración productiva, firmas, broker, schema registry,
exactly-once ni compatibilidad con una API real.

## Siguiente decisión

No añadir otra infraestructura. El siguiente trabajo autorizado es conectar
un primer adapter sintético a este sobre y verificar que conserva los mismos
resultados de los contratos 065–067.
