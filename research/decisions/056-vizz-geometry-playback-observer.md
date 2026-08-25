# ADR-056 — VIZZ: cerrar geometría antes del runtime visual

## Estado

Aceptada como implementación experimental. Los contratos 046, 047 y 048 están
verificados; el runtime real todavía no se cambia.

## Qué se implementó

El plan derivado del research se convirtió en tres capas aisladas:

```text
046  GazeObservation + planos físicos → GazeState o UNKNOWN
047  GazeState sintético → política visual de playback
048  GazeState + contexto → traza pasiva mínima
```

### 046 — geometría

La mirada parte del punto medio de ambos ojos y se intersecta con cada plano de
monitor. La salida contiene monitor, `uv`, distancia, confianza, incertidumbre,
radio seguro y motivo de `UNKNOWN`. Se verifican dos monitores, monitor
inclinado, traslación de cabeza con objetivo mundial fijo, layout obsoleto,
ojo perdido, baja confianza y ambigüedad.

### 047 — playback

Se comparan cuatro políticas: pantalla completa, baseline estático limpio,
adaptación protegida y control de fallo sin protección. La política protegida
reduce detalle de baja prioridad y mantiene señales periféricas. El HTML es
local y manual; no mira la cámara ni modifica otras ventanas.

### 048 — observación pasiva

Se conserva sólo timestamp, estado de gaze, monitor, `uv`, incertidumbre,
fijación, conteo de teclado y posición del mouse como contexto. No se conserva
texto, identidad de teclas, vídeo, título de ventana ni contenido de pantalla.

## Decisión de integración

El runtime 033 no puede sustituir todavía su mapper legacy por 046: su tracker
actual produce proxies en espacio de imagen, pero no entrega aún centros
oculares y rayo en coordenadas mundiales con intrínsecos/extrínsecos del
monitor. Convertir esos proxies directamente en `GazeState` violaría el
contrato geométrico.

Por ello, la siguiente integración debe ser un adaptador explícito que sólo
acepte:

```text
ambos centros oculares en mundo
pose/cámara válida
vector de mirada en mundo
layout versionado de monitores
```

Mientras falte cualquiera, debe producir `UNKNOWN` y mantener el contenido
estático. El mapper legacy puede seguir funcionando como diagnóstico separado,
pero no debe alimentar la política VIZZ nueva.

## Evidencia y límites

Los contratos sintéticos pasaron sin cámara, GPU, red o datos humanos. Esto
demuestra coherencia computacional, no precisión de webcam, reducción de fatiga,
comodidad ni mejora de una tarea. La evidencia científica sobre periferia,
crowding y latencia justifica conservar alertas y medir el sistema extremo a
extremo; no fija radios universales.

## Siguiente trabajo

1. Crear el adaptador `GazeSample → GazeObservation` con estado cerrado:
   `missing_world_geometry` mientras no haya geometría calibrada.
2. Ejecutarlo sobre frames sintéticos y luego sobre una sesión consentida sin
   mutar pantalla.
3. Medir latencia, cobertura de monitor, `UNKNOWN` y estabilidad de pose.
4. Sólo después habilitar el playback conectado al tracker y preparar el A/B
   por lectura, código, navegación y monitorización.

## Kill tests

- El adaptador no puede producir una coordenada física desde `sample.features`
  legacy solamente.
- Mover cámara, DPI, resolución o monitor debe invalidar el layout versionado.
- El playback conectado debe conservar alertas periféricas y tener fallback
  estático.
- Cualquier artefacto temporal o deterioro de tarea detiene la transformación.
