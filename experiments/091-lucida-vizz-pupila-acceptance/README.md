# Experiment 091 - LUCIDA VIZZ/PUPILA acceptance

This offline check consumes the redacted states produced by experiment 090 and
routes them through an explicitly selected LUCIDA Python checkout. It proves a
real boundary between the existing VIZZ/PUPILA logic and the new host-neutral
engine without importing an implicit local package.

The check does not open a camera, window, network socket or host application.
It does not persist frames, keyboard text, documents, credentials or raw
payloads. It does not infer attention, learning, gaze accuracy or medical
state.

Run from the FARMAXIA root:

```powershell
.\.venv\Scripts\python.exe experiments\091-lucida-vizz-pupila-acceptance\run_acceptance.py --lucida-root C:\IA\LUCIDA_ENGINE
```

The selected checkout must contain `lucida/engine/domain_adapters.py`. The
report includes the resolved package path, explicit route ids, state revision,
render item count and side-effect flags. A path outside the requested checkout
fails before the acceptance result is produced.

This is an integration acceptance check, not a live runtime. The source
repositories still own transport, capture and host behavior.
