# VIZZ 037 — auditoría de representación dual

Este auditor revisa si los artefactos de calibración y validación contienen a
la vez features legacy y resúmenes eye-centric completos. No reconstruye
landmarks que no fueron guardados y no transforma una feature legacy en falsa
evidencia eye-centric. No abre cámara ni escribe vídeo.

```powershell
.\.venv\Scripts\python.exe experiments/037-vizz-dual-representation-audit/audit_dual.py `
  --calibration .\.vizz-calibration.json `
  --validation .\.vizz-validation-smoke.json `
  --output .\.vizz-dual-audit.json
```

La salida `UNKNOWN_NOT_IDENTIFIABLE` para los artefactos antiguos es el
resultado esperado: fueron capturados antes de que el tracker persistiera la
nueva representación. La próxima validación generada con el runtime actualizado
quedará lista para una comparación agrupada sin tocar el mapper legacy.
