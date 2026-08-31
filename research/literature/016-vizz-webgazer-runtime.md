# Investigación 016 — runtime WebGazer para VIZZ (retirado)

Fecha: 2026-08-24

## Fuente informática primaria

La integración histórica evaluó WebGazer.js 3.5.3, fijado desde el proyecto
oficial. El bundle y los assets del experimento 030 fueron retirados del árbol
activo; se conserva este registro para no confundir una evaluación pasada con
una dependencia vigente:

- [Repositorio y README oficial](https://github.com/brownhci/WebGazer)
- [API de control oficial](https://github.com/brownhci/WebGazer/wiki/Top-Level-API)
- [Release 3.5.3](https://github.com/brownhci/WebGazer/releases/tag/3.5.3)
- [Paquete npm 3.5.3](https://www.npmjs.com/package/webgazer/v/3.5.3)

El README del proyecto describe inferencia en cliente con webcam,
auto-calibración por interacción y consentimiento del usuario. El paquete
declara `GPL-3.0-or-later` y la release 3.5.3 comunica que es la última release
planificada, con maintenance oficial terminada y soporte comunitario posible.
En el sandbox histórico, la licencia y el texto GPLv3 se archivaron junto al
bundle para que el runtime no dependiera de un CDN. WebGazer 3.5.3 declara por defecto
`faceMeshSolutionPath: "./mediapipe/face_mesh"`; esos assets se incorporan
desde `@mediapipe/face_mesh` 0.4.1633559619 con licencia Apache-2.0. El
navegador debe poder resolver los recursos
internos mediante el mismo origen local; por ello la CSP de 030 permite
`connect-src 'self'` y bloquea orígenes externos. Los bundles Emscripten de
MediaPipe usan `Function()` para crear constructores y `WebAssembly` para el
tracker, por lo que el sandbox declara `unsafe-eval` y `wasm-unsafe-eval` en
`script-src`; esta es una excepción localizada del prototipo, no una política
para producción.

## API evaluada por el adaptador histórico

El experimento 030 configuró `saveDataAcrossSessions(false)`, `ridge`, listener
de predicción y una presentación sin preview de vídeo. Después del opt-in
llama `begin()`. Cada objetivo de calibración registra un punto con
`recordScreenPosition()`. El apagado llama `clearGazeListener()`, `pause()` si
está disponible, `stopVideo()`, `end()` y `clearData()`.

La separación entre `end()` y `stopVideo()` es deliberada: el bundle 3.5.3
expone ambos controles y el contrato de FARMAXIA exige liberar la pista de
vídeo además de terminar el loop de predicción. `clearData()` se ejecuta para
evitar que la calibración sobreviva a la sesión. El test automático verifica la
presencia de estas operaciones, pero no puede probar permisos, hardware ni el
comportamiento de un navegador sin abrir uno.

## Evidencia científica que sigue abierta

La literatura 014 ya registra que calibración, pupil-size artifact y latencia
de extremo a extremo deben medirse separadamente. Añadir un runtime real no
convierte una predicción de webcam en medida de atención, fatiga, ansiedad,
intoxicación o neurotransmisores. Tampoco autoriza a traducir una receta óptica
o la condición nocturna a CSS sin una especificación óptica y evaluación
humana separadas.

## Resultado de la evaluación

WebGazer queda retirado del estado activo y no es dependencia de VIZZ. Pupil
Core continúa diferido por hardware y API de red. La evidencia del sandbox
demostró integración y controles estáticos, pero no precisión ni utilidad
perceptual; no se fabrican datos para cerrar esa brecha.
