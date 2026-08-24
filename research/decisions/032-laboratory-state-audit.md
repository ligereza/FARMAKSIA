# Decisión 032 — estado consolidado del laboratorio

Fecha: 2026-08-24

## Auditoría

La auditoría reproducible del estado confirma:

- VIZZ tiene exposición perceptual, contrato de sesión, puente CODE-INE,
  adaptador manual y control de secuencia larga; no hay datos humanos;
- CODE-INE queda como descriptor de transición e interoperabilidad, no como
  operador ni explicación farmacológica;
- X-ANA-X está archivado como hipótesis independiente después de dos controles
  negativos de novedad y conserva solo su protocolo documental;
- KETAMINE aparece explícitamente en cuarentena y no tiene frente activo;
- el manifiesto de corpus permanece `empty_by_design`;
- la suite integra los experimentos actuales y sus manifiestos de procedencia.

La herramienta `research/tools/audit_lab_state.py` devuelve `LAB_STATE_VALID`.
La suite completa mantiene los límites de datos humanos, captura cruda,
dispositivos y red.

## Desconocidos que permanecen

No se sabe si una persona puede emitir eventos abstractos sin interrumpir su
tarea, si la transición `c04 → c07` corresponde a repetición subjetiva, si una
representación VIZZ mejora confort o comprensión, ni si la captura manual
tiene valor práctico. Esos desconocidos no se convierten en resultados.

## Siguiente compuerta

El adaptador manual solo puede pasar de dry-run a una sesión si el usuario lo
inicia deliberadamente con consentimiento explícito. Hasta entonces, el loop
continúa con auditorías y fixtures sintéticos, manteniendo KETAMINE en
cuarentena.
