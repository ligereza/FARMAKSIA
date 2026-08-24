# Decisión 038 — VIZZ no habilita gaze-contingent sin compuerta de calidad

Fecha: 2026-08-24

## Evidencia

El experimento 028 aplicó diez perfiles iniciales y luego añadió un control de
pose inestable; la matriz final tiene once perfiles y conserva la transición
base `c04 → c07`.

| Estado | Casos |
|---|---:|
| `available` | 1 |
| `blocked` | 3 |
| `unavailable` | 5 |
| `rejected` | 2 |

Solo un fixture pasó simultáneamente consentimiento, procesamiento local,
transporte sin red, calibración, error, latencia, cobertura y estabilidad de
pose. Los kill tests impidieron que cualquier otro perfil habilitara la bandera
de adaptación.

## Herramientas

WebGazer.js 3.5.3 queda como `candidate_only`: ofrece inferencia en navegador
con webcam y consentimiento, pero su mantenimiento oficial terminó. Pupil Core
queda `deferred_hardware_and_network_api`: su software es abierto y activo,
pero requiere hardware y la ruta API de tiempo real usa red. Ninguno se instala
ni se adopta en el runtime de FARMAXIA.

## Decisión

VIZZ adopta únicamente el contrato de compuerta y su salida fail-closed. La
bandera `adaptation_allowed` solo significa que un adaptador sintético pasó
criterios declarados; no significa que un sensor sea preciso, que una persona
esté mirando un lugar, ni que una pantalla adaptada mejore comprensión,
confort, sueño o salud ocular.

Los límites de 100 ms, 100 px y cobertura 1.0 son límites del fixture. No son
umbrales fisiológicos, clínicos ni recomendaciones de compra. La receta de
lentes tampoco se traduce a CSS o a una modificación automática de display.

## Siguiente compuerta

Solo una futura sesión explícitamente consentida podría evaluar un adaptador
real, con calibración visible, métrica de error, latencia de extremo a extremo,
retención mínima y botón de apagado. Antes de ella no se habilita webcam,
headset, red, parpadeo, pupillometría ni captura de contenido personal.
