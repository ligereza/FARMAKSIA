# Decisión 041 — VIZZ retira el adaptador WebGazer local y opt-in

Fecha: 2026-08-24

## Registro histórico

El experimento 030 implementó una página ejecutable que cargaba WebGazer.js
3.5.3 desde `vendor/` y sus assets MediaPipe Face Mesh desde
`mediapipe/face_mesh/`, solicita cámara solo después de una acción de
consentimiento, ofrece nueve objetivos de calibración y dibuja un marcador con
predicciones recibidas en memoria. El test estático pasa y confirma que el
adaptador no contiene CDN, beacons, almacenamiento web ni una ruta de
exportación. La CSP solo permite `fetch` al mismo origen para que WebGazer
pueda cargar recursos internos desde `localhost`; el tráfico externo sigue
bloqueado.

La automatización no abrió navegador, no solicitó permiso, no encendió cámara,
no utilizó un origen externo y no generó datos humanos. Por eso esta decisión
demuestra integración y controles, no precisión ni utilidad perceptual. La CSP
permite `unsafe-eval` y `wasm-unsafe-eval` únicamente para el runtime local de
MediaPipe/Emscripten, que usa `Function()` y WebAssembly durante su arranque.
Los orígenes externos continúan bloqueados.

## Decisión de retiro

VIZZ **retira** WebGazer 3.5.3 del estado activo. El experimento 030 y sus
bundles ya no se distribuyen ni se integran en la suite. La investigación se
conserva para explicar qué se probó y por qué no se convirtió en runtime de
producto. La dependencia estaba sujeta a GPL-3.0-or-later y a la advertencia
de que la maintenance oficial terminó; cualquier recuperación futura requiere
una nueva decisión técnica y revisión legal independiente.

No queda una adaptación WebGazer activa. El núcleo VIZZ vigente debe mantener
separadas la geometría calibrada, los detectores y cualquier modelo futuro;
no se infieren estados humanos o farmacológicos ni se aplican recetas de
lentes, modo nocturno o pupila mediante CSS.

## Kill tests y límites

- Los controles de consentimiento, nueve objetivos y apagado fueron límites
  del sandbox histórico; ya no existen como runtime activo.
- La evidencia estática de aquel sandbox no equivale a una validación de
  permisos, hardware o navegador.
- Cualquier precisión, latencia, cobertura, efecto en confort, sueño o
  comprensión queda desconocida hasta un protocolo humano separado.
- No se ejecutan pruebas bajo intoxicación ni se usa una medición ocular como
  proxy de neurotransmisores, ansiedad o CODE-INE.

## Estado actual

No hay una próxima sesión WebGazer prevista. Si alguna vez se reabre la línea,
debe tratarse como una nueva evaluación, con dependencia y licencia revisadas,
datos mínimos, una vía de abortar y un registro separado del corpus vacío por
diseño.
