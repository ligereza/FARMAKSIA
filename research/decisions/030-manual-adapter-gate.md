# Decisión 030 — el adaptador manual queda preparado, no activado

Fecha: 2026-08-24

## Evidencia

El experimento 021 verificó que el adaptador local:

- bloquea la ausencia de `--consent` antes de crear salida;
- acepta tres eventos abstractos bajo `task_events_only`;
- ejecuta dry-run sin escribir archivos;
- rechaza payloads crudos y protege salidas existentes.

El runner no inició dispositivos, red ni sesión real.

## Decisión

Se adopta el adaptador como herramienta preparada para una futura acción manual
explícita. No se ejecuta automáticamente y no se habilita webcam, eye tracking,
captura de pantalla, teclado o audio. La herramienta solo registra eventos que
el usuario entregue deliberadamente.

## Límites

La compuerta técnica no equivale a consentimiento ético completo ni demuestra
que el registro sea cómodo, seguro o útil. Una futura sesión requeriría una
decisión explícita del usuario y seguiría sin permitir inferencias de ansiedad,
neurotransmisores, intoxicación o eficacia visual.

## Próximo objetivo

Mantener el adaptador en dry-run hasta que exista una acción explícita para una
sesión manual. Si se realiza, validar primero una secuencia corta y comprobar
si VIZZ y CODE-INE conservan sus límites sin inventar estados.
