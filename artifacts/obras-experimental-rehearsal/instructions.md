# Obras Experimentales: demostrador integral

## Unico comando

Desde PowerShell:

```powershell
Set-Location C:\IA\FARMAXIA\artifacts\obras-experimental-rehearsal
powershell -ExecutionPolicy Bypass -File .\run_demo.ps1
```

El comando ejecuta el fixture sintetico en modo `dry-run` y deja la evidencia
en `run-output`. Para probar otro numero de luminarias virtuales:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_demo.ps1 -Fixtures 8
```

Abre manualmente `run-output\visualization.html` en un navegador local. La
visualizacion incluye el timeline de eventos XIO, el hueco de audio, la
coordinacion PhaseChaser y las cues que MOSAIK propone para un flujo Resolume.

## Artefactos

- `signal-events.jsonl`: eventos canonicos XIO con procedencia, secuencia,
  timestamp y timecode.
- `timeline-normalized.json`: recorrido normalizado y checkpoints.
- `phase-states.jsonl`: angulo, fase, intensidad y pulso por luminaria.
- `mosaik-proposals.json`: propuesta reversible `proposal_only`.
- `mosaik-replay-fixture.json` y `mosaik-replay-report.json`: entrada y
  resultado de replay MOSAIK.
- `resolume-cues.json`: representacion de timeline compatible con Resolume,
  sin escribir un showfile.
- `safety-summary.json`: acciones bloqueadas y escenarios comprobados.
- `visualization.html`: evidencia visual autocontenida, sin red ni assets
  externos.

El audio de entrada es `fixture-synthetic-audio.json` en el experimento
FARMAXIA. Esta es una demostracion de contrato y replay; no es evidencia de
una prueba fisica, una medicion acustica, una latencia de red ni una respuesta
optica real.
