# Investigación 014 — calidad de mirada y herramientas VIZZ

Fecha: 2026-08-24

## Herramientas open source candidatas

La documentación primaria actual distingue dos rutas, ninguna adoptada por el
runtime de FARMAXIA:

| Proyecto | Entrada y ejecución | Licencia/estado | Límite operacional |
|---|---|---|---|
| [WebGazer.js](https://github.com/brownhci/WebGazer) 3.5.3 | webcam, navegador, inferencia en cliente, auto-calibración | GPL-3.0; el repositorio también contiene una opción LGPLv3; mantenimiento oficial terminado el 2026-02-24 | requiere permiso de webcam, calibración visible y un adaptador local mantenible |
| [Pupil Core](https://github.com/pupil-labs/pupil) | headset dedicado, software Python/C++, captura local; API de tiempo real sobre red | LGPL-3.0 para el código del proyecto, con componentes GPL reportados; desarrollo comunitario activo | hardware, instalación nativa y transporte de red en la integración API |

WebGazer afirma que el vídeo no tiene que enviarse a un servidor y que solo
puede ejecutarse con consentimiento de webcam. Eso reduce la superficie de
captura, pero no demuestra precisión suficiente para cambiar una pantalla ni
compensa el fin del mantenimiento oficial. Pupil Core ofrece una ruta más
controlable para hardware, pero su API de integración añade dependencias,
permisos y red local que no son necesarias para el contrato mínimo actual.

## Evidencia científica relevante

La latencia de una pantalla gaze-contingent es una suma de muestreo,
estimación, filtrado, transmisión y actualización de display. Por ello debe
medirse de extremo a extremo; no basta con declarar la frecuencia del sensor:

- [Direct measurement of the system latency of gaze-contingent displays](https://pmc.ncbi.nlm.nih.gov/articles/PMC4077667/)

La calibración tampoco es una garantía aislada de exactitud. Un estudio reciente
describe cómo el pupil-size artifact puede introducir error durante calibración
y validación, y advierte que repetir calibraciones hasta alcanzar un número no
necesariamente mejora la calidad real:

- [Eye tracker calibration: How well can humans refixate a target?](https://pmc.ncbi.nlm.nih.gov/articles/PMC11659352/)

En el componente ocular, una investigación cruzada con 24 estudiantes observó
menos parpadeos durante tareas de lectura que durante conversación o caminar,
pero no encontró asociación entre esas medidas y síntomas o signos de la
superficie ocular. Esto impide usar gaze o parpadeo como proxy automático de
fatiga, ansiedad o neuroquímica:

- [Blink Rate Measured In Situ...](https://pubmed.ncbi.nlm.nih.gov/36763349/)

La revisión Cochrane sobre lentes filtrantes azules concluye que probablemente
producen poco o ningún efecto en fatiga visual a corto plazo frente a lentes
transparentes, con evidencia incierta para sueño y otros resultados. VIZZ no
debe aplicar una receta óptica ni prometer protección clínica desde CSS:

- [Blue-light filtering spectacle lenses...](https://pubmed.ncbi.nlm.nih.gov/37593770/)

## Consecuencia para FARMAXIA

El experimento 028 no inicia webcam, headset, red ni participantes. Solo prueba
una política computacional sobre metadatos sintéticos de un adaptador:

1. consentimiento explícito;
2. procesamiento local y transporte permitido;
3. calibración declarada, error dentro del límite del fixture;
4. latencia declarada dentro del límite del fixture;
5. cobertura completa y estabilidad de la pose;
6. herramienta y procedencia conocidas.

Si una condición falla, VIZZ no habilita adaptación gaze-contingent y devuelve
`blocked`, `unavailable` o `rejected`. Los límites numéricos son criterios del
fixture y no umbrales fisiológicos, clínicos ni recomendaciones de hardware.
