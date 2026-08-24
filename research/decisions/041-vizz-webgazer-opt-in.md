# Decisión 041 — VIZZ incorpora un adaptador WebGazer local y opt-in

Fecha: 2026-08-24

## Evidencia nueva

El experimento 030 implementa una página ejecutable que carga WebGazer.js
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
demuestra integración y controles, no precisión ni utilidad perceptual.

## Decisión

VIZZ **adopta experimentalmente** WebGazer 3.5.3 solo en el sandbox local del
experimento 030. No se adopta como runtime de producto ni como instrumento
clínico. La dependencia queda sujeta a GPL-3.0-or-later y a la advertencia de
que la maintenance oficial terminó; cualquier distribución con otra licencia
requiere revisión legal independiente.

La adaptación permitida por ahora es un marcador visual después de nueve
puntos de calibración y diez predicciones válidas. No cambia contenido según
una supuesta atención, no infiere estados humanos o farmacológicos y no
aplica recetas de lentes, modo nocturno o pupila mediante CSS.

## Kill tests y límites

- Sin checkbox de consentimiento, el botón de inicio permanece deshabilitado y
  el adaptador no llama `begin()`.
- Sin nueve objetivos, el estado de adaptación permanece bloqueado.
- Al detener se limpian listener, vídeo, loop y modelo local; la limpieza es
  best-effort porque la página puede cerrarse abruptamente.
- Cualquier precisión, latencia, cobertura, efecto en confort, sueño o
  comprensión queda desconocida hasta un protocolo humano separado.
- No se ejecutan pruebas bajo intoxicación ni se usa una medición ocular como
  proxy de neurotransmisores, ansiedad o CODE-INE.

## Próxima compuerta

Solo si el operador lo solicita y aprueba una sesión explícita se puede medir
error contra una referencia, latencia extremo a extremo y retención. Esa
sesión debe usar datos mínimos, no contenido personal, una vía de abortar y un
registro separado del corpus vacío por diseño.
