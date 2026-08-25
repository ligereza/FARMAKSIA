# VIZZ 036 — contrato de captura dual

Este experimento comprueba que el tracker y la ventana estable conservan dos
representaciones en paralelo:

```text
legacy features ───────────────► mapper actual (sin cambios)
eye-centric + distancia + roll ─► auditoría y próximo M1
```

El frontend eye-centric no modifica todavía las coordenadas del overlay. La
captura persiste sus resúmenes robustos para poder comparar sesiones futuras sin
repetir el experimento sólo para cambiar el modelo.

La prueba usa nubes sintéticas, no abre la cámara, no guarda vídeo y no crea
datos humanos. Ejecutar desde la raíz:

```powershell
.\.venv\Scripts\python.exe experiments/036-vizz-eye-centric-capture-contract/run_experiment.py
```

El resultado esperado es `EYE_CENTRIC_CAPTURE_VALID`.
