# Resultados del experimento 088

## Evidencia obtenida

Ejecutado sin abrir aplicaciones externas:

```text
.\.venv\Scripts\python.exe experiments\088-vizz-state-replay-preflight\run_contract_test.py
VIZZ_088_REPLAY_CONTRACT=PASS
```

La reproducción de la fixture produjo dos estados `VALID` con plan `ACTIVE`.
El duplicado de secuencia produjo `SEQUENCE_NOT_MONOTONIC`; el estado con baja
confianza produjo `CONFIDENCE_TOO_LOW`; el registro atrasado produjo
`STATE_STALE`. Los tres quedaron en plan `NEUTRAL`, con parallax cero y el
contenido crítico sin alterar.

La suite global terminó con:

```text
PASS contract test FARMAKSIA VIZZ state replay 088
PASS replay fixture FARMAKSIA VIZZ state 088
PASS provenance 088
SUITE_VALID
```

## Qué demuestra

La frontera temporal es explícita: un estado viejo no se conserva como si
fuera actual y una secuencia repetida no puede reactivar el último efecto.
El replay permite probar esta propiedad antes de conectar OSC, captura de
ventana o TouchDesigner.

## Qué no demuestra

No demuestra precisión de eye tracking, profundidad métrica, rendimiento GPU,
latencia del transporte, comportamiento de una ventana real ni comodidad
perceptual. Tampoco prueba todavía el bootstrap dentro de TouchDesigner.

## Siguiente paso

Ejecutar una sola prueba manual autorizada del bootstrap 087 con estado
synthetic/manual. Si falla, corregir sólo el error reproducible observado; si
pasa, elegir el transporte de imagen según la licencia y las capacidades
reales de la instalación.
