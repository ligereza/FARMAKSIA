# VIZZ 054 — auditor offline de calidad naturalista

Este experimento compara dos trazas ya capturadas por VIZZ, por ejemplo con
lentes y sin lentes, sin volver a abrir la cámara y sin escribir sobre la
pantalla. Resume calidad, cobertura de rayos binoculares, desacuerdo entre
ojos, distancia interocular aparente, actividad agregada de teclado y región
del cursor según el layout lógico de Windows.

## Uso

```powershell
.\.venv\Scripts\python.exe experiments/054-vizz-naturalistic-quality-audit/quality_audit.py `
  --with-glasses .\.vizz-binocular-quality.jsonl `
  --without-glasses .\.vizz-binocular-quality-without-glasses.jsonl `
  --output .\.vizz-quality-audit.json
```

El auditor no interpreta el cursor como ground truth de mirada. Tampoco
cuenta parpadeos: sólo indica si el esquema contiene un campo de parpadeo
explícito. Las sesiones naturalistas sirven para medir estabilidad, no para
calibrar gaze a monitor ni atribuir causalidad a los lentes.

## Límites

- La condición visual está confundida con sesión, postura, distancia y tarea.
- La región del cursor no identifica el monitor que la persona está mirando.
- Un rayo relativo no es todavía una distancia métrica ni una pose 3-D.
- La salida no contiene vídeo, texto, teclas ni contenido de pantalla.
