# Relacion de commits publicados

El demostrador se implemento por responsabilidad de repositorio:

- XIO: `7d9a407` — `feat: add deterministic rehearsal signal normalization`
  — rama publicada `codex/obras-experimental-rehearsal-xio-root`.
- MOSAIK/VJ: `58a3db8` — `feat: stage PhaseChaser rehearsal proposals safely`
  — rama publicada `codex/obras-experimental-rehearsal-mosaik-root`.
- FARMAXIA: `55bc250` — `feat: add Obras end-to-end rehearsal runner`
  — rama publicada `codex/obras-experimental-rehearsal-farmaxia-root`.
- FARMAXIA: `448c325` — `docs: publish Obras rehearsal evidence package`
  — contiene el paquete ejecutable y la salida de ejemplo.

El servidor remoto ofrecio URLs de creacion de PR para las tres ramas, pero no
exigio proteccion que obligara a abrirlos durante esta ejecucion. Las ramas
quedan listas para revision:

- https://github.com/ligereza/XIO/pull/new/codex/obras-experimental-rehearsal-xio-root
- https://github.com/ligereza/mosaik/pull/new/codex/obras-experimental-rehearsal-mosaik-root
- https://github.com/ligereza/FARMAKSIA/pull/new/codex/obras-experimental-rehearsal-farmaxia-root

## Limitaciones reales

- La senal de entrada es un fixture sintetico de envolvente; no se uso audio
  fisico autorizado.
- No hay calibracion optica, BLE, Art-Net, sACN, OSC externo ni Resolume
  abierto. Las cues son propuestas de timeline.
- Los timestamps y timecodes son deterministas del fixture, no relojes de
  hardware ni una medida de latencia.
- PhaseChaser demuestra la coordinacion matematica para N luminarias, no la
  respuesta de N luminarias reales.
