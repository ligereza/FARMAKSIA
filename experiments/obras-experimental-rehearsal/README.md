# Obras Experimentales: ensayo integral

Este experimento conecta una envolvente sonora sintética documentada con XIO,
PhaseChaser y MOSAIK en modo `dry-run`. El fixture no es una captura física ni
una prueba de hardware.

## Ejecucion local

Desde `C:\IA\FARMAXIA`:

```powershell
python .\experiments\obras-experimental-rehearsal\run_rehearsal.py `
  --output .\artifacts\obras-experimental-rehearsal\run-output
```

La ejecucion usa `C:\IA\XIO` y `C:\IA\VJ` por defecto. Se pueden cambiar con
`--xio-root` y `--mosaik-root` sin instalar paquetes ni abrir puertos.

## Recorrido

1. XIO lee `fixture-synthetic-audio.json`, extrae pulsos por umbral y crea
   eventos con secuencia, timestamp, timecode y procedencia.
2. XIO conserva la entrega duplicada y fuera de orden en su auditoria, y
   representa la perdida temporal como `audio.gap`.
3. PhaseChaser genera fase, angulo, intensidad y pulso para N luminarias BLE
   virtuales. El ensayo se reinicia despues de la secuencia 2 y comprueba que
   la reanudacion coincide con la ejecucion continua.
4. MOSAIK valida la cinta semantica y produce propuestas `proposal_only` y
   cues de timeline compatibles con un flujo Resolume. No abre Resolume.
5. XIO genera frames `xio:predictive-semantic-lighting-frame:0.1`,
   calcula el presupuesto DMX directo frente al paquete semántico XSL1 y
   verifica su CRC.
6. MOSAIK/VJ proyecta el mismo frame a intenciones OSC para Resolume y acciones
   declarativas del WebAPI de Avolites Titan. Ningún destino es contactado.
7. El HTML local permite recorrer la señal y la escena con un slider o Play.

## Limites

- No se emite Art-Net, OSC, sACN ni BLE.
- No se controla una luminaria fisica ni un showfile.
- La cinta tiene `calibration_status=not_calibrated`.
- El paquete XSL1 es lossless para la escena semántica y no para 80 valores DMX
  arbitrarios independientes; requiere un decoder profile y orden de fixtures.
- Las propuestas Titan requieren que una persona resuelva playback, patch y
  permisos del show antes de cualquier ejecución.
- El fixture sintetico demuestra el contrato y el replay, no una medicion
  acustica, latencia de red o respuesta optica real.
