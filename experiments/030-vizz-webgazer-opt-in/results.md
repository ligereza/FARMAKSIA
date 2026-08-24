# Resultado 030 — contrato del adaptador WebGazer

La auditoría estática pasa (`CONTRACT_TESTS_VALID`). Confirma que el HTML
carga únicamente la copia local de WebGazer 3.5.3 y `app.js`, que la cámara
requiere consentimiento y que el flujo expone calibración, apagado y limpieza
del modelo.

La automatización no abrió un navegador, no solicitó permiso, no inició una
cámara, no usó red y no produjo datos humanos. Por tanto, no hay resultado de
precisión, cobertura, latencia, comodidad ni eficacia que reportar.

## Kill tests aplicados

- Se rechaza una página sin checkbox de consentimiento o con inicio habilitado
  por defecto.
- Se rechaza cualquier script remoto, `fetch`, `XMLHttpRequest`, beacon,
  `localStorage` o `sessionStorage` en el adaptador.
- Se exige que el apagado llame `clearGazeListener`, `stopVideo`, `end` y
  `clearData` en un bloque de limpieza best-effort.
- Se exige que la adaptación visual permanezca bloqueada hasta nueve puntos de
  calibración y diez predicciones válidas.

La ejecución manual queda fuera de esta evidencia y debe ser una sesión
separada, consentida y revisada.
