# Resultado 030 — contrato del adaptador WebGazer

La auditoría estática pasa (`CONTRACT_TESTS_VALID`). Confirma que el HTML
carga únicamente la copia local de WebGazer 3.5.3, sus assets locales de
MediaPipe Face Mesh y `app.js`, que la cámara requiere consentimiento, que solo
se permiten recursos del mismo origen y que el flujo expone calibración,
apagado y limpieza del modelo.

La automatización no abrió un navegador, no solicitó permiso, no inició una
cámara, no contactó un origen externo y no produjo datos humanos. Por tanto,
no hay resultado de precisión, cobertura, latencia, comodidad ni eficacia que
reportar.

## Kill tests aplicados

- Se rechaza una página sin checkbox de consentimiento o con inicio habilitado
  por defecto.
- Se rechaza cualquier script remoto, origen CSP externo, `XMLHttpRequest`,
  beacon, `localStorage` o `sessionStorage` en el adaptador; el `fetch` de
  recursos solo puede dirigirse al mismo origen.
- Se permite `unsafe-eval` y `wasm-unsafe-eval` solo porque los assets locales
  de MediaPipe/Emscripten usan `Function()` y WebAssembly; no se permiten
  orígenes remotos.
- Se exige que el contenedor de preview oculto no intercepte clics de los
  objetivos de calibración.
- Se exige la presencia local de los assets MediaPipe Face Mesh usados por el
  tracker por defecto; no basta con que exista `webgazer.js`.
- Se exige que el apagado llame `clearGazeListener`, `stopVideo`, `end` y
  `clearData` en un bloque de limpieza best-effort.
- Se exige que la adaptación visual permanezca bloqueada hasta nueve puntos de
  calibración y diez predicciones válidas.

La ejecución manual queda fuera de esta evidencia y debe ser una sesión
separada, consentida y revisada.
