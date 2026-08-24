# Decisión 024 — VIZZ adopta primero el envelope local, no eye tracking

Fecha: 2026-08-24

## Evidencia

La documentación primaria consultada confirma tres perfiles distintos:

- WebGazer 3.5.3 figura como funcional y ejecuta la inferencia en el
  navegador, con permiso de webcam, pero su repositorio declara que el
  mantenimiento oficial terminó el 24 de febrero de 2026;
- Pupil Core sigue siendo una plataforma abierta y de desarrollo comunitario,
  con hardware dedicado, dependencias nativas y API en red;
- PsychoPy 2026.1.0 ofrece Builder, Coder y PsychoJS para tareas temporizadas,
  pero introduce una infraestructura de experimento que aún no está exigida
  por la frontera computacional de VIZZ.

El experimento 015 demuestra una compuerta más pequeña: captura desactivada
produce cero eventos; el opt-in acepta tres eventos abstractos; un payload con
`text` es rechazado. El runner no inicia dispositivos ni usa red.

## Decisión

Se adopta provisionalmente el validador Python estándar y el envelope de
eventos de tarea como primera herramienta VIZZ. Es una adopción de contrato,
no una adopción de sensor.

WebGazer queda como candidato experimental posterior, condicionado a permiso
explícito, calibración visible, procesamiento local, kill test de latencia y
una métrica de error de mirada. Pupil Core queda reservado para una hipótesis
que requiera pupila o gaze con hardware. PsychoPy se incorpora solo cuando una
tarea humana concreta necesite su temporización o registro.

## Kill tests

La decisión queda invalidada si el adaptador local captura contenido fuera del
alcance, si el estado desactivado emite eventos, si el opt-in permite datos
crudos o si una futura integración introduce red/dispositivos sin declararlo.

No se incorporan herramientas externas al runtime ni se crean datos humanos.
KETAMINE permanece en cuarentena.

## Próximo objetivo

Ejecutar, solo con consentimiento explícito y sin contenido personal, una
sesión manual mínima que emita eventos abstractos y verificar si el contrato
014 puede calcularse con ellos. No habilitar webcam ni eye tracking en ese
paso.
