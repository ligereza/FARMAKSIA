# Investigación 008 — VIZZ como representación adaptada a la percepción

Fecha: 2026-08-23

## Pregunta

¿Puede una pantalla cambiar su representación según tarea, mirada, luminancia,
fatiga, corrección visual y duración de observación sin convertirse en una
auditoría genérica de UX?

## Efectos documentados de pantallas

La fatiga visual digital es multifactorial. Incluye sequedad, ardor, visión
borrosa o fluctuante, cefalea, fotofobia y molestias de cuello/hombros. Los
mecanismos más consistentes son menor frecuencia y completitud del parpadeo,
demanda de visión cercana, acomodación/vergencia, contraste, reflejos,
luminancia ambiental y carga cognitiva:

- https://pubmed.ncbi.nlm.nih.gov/39308959/
- https://pubmed.ncbi.nlm.nih.gov/37062428/
- https://www.nei.nih.gov/eye-health-information/eye-conditions-and-diseases/dry-eye

La luz de una pantalla a niveles normales no debe describirse automáticamente
como daño retinal. La evidencia y la Academia Americana de Oftalmología no
recomiendan gafas especiales de ordenador por protección ocular. El problema
no es que el “azul” sea una toxina visual, sino que el espectro, la intensidad,
el horario y el contexto pueden alterar sueño, alerta y confort.

## Receta de lentes y pantalla

Una pantalla común no corrige por sí sola una miopía, hipermetropía,
astigmatismo o presbicia. Sí puede adaptar la representación: tamaño angular,
distancia de trabajo, espaciado, contraste, nitidez aparente y densidad de
información. La corrección óptica debe ser evaluada para la distancia real de
trabajo; la evidencia sobre “computer glasses” es específica y de calidad
mixta:

- https://pubmed.ncbi.nlm.nih.gov/29633784/
- https://pubmed.ncbi.nlm.nih.gov/37062428/

En displays cercanos, VR y AR, sí existe investigación de renderizado
consciente de la receta y de displays varifocales. Esto no equivale a que un
monitor normal pueda reemplazar unos lentes:

- https://discovery.ucl.ac.uk/id/eprint/10170855/
- https://research.nvidia.com/labs/amri/publication/wu2020prescription/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC2879326/

## Mirada y adaptación

La fóvea no tiene la misma resolución que la periferia. Los displays
gaze-contingent pueden mantener detalle en el área de mirada y degradar o
reorganizar la periferia; en gráficos también reducen costo de renderizado.
Esto es una base informática real para VIZZ, pero tiene riesgos de latencia,
errores de calibración, privacidad y adaptación indeseada:

- https://journals.sagepub.com/doi/pdf/10.1518/hfes.45.2.307.27235
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5338519/
- https://journals.sagepub.com/doi/pdf/10.1177/21695067231192631

Para el caso de un pequeño recuadro útil, las transformaciones a probar son:

- reflow hacia la zona de mirada;
- reducción temporal de contraste y densidad fuera de la zona de interés;
- ampliación de contexto solo alrededor del objetivo;
- congelación o sustitución de regiones periféricas que no aportan a la tarea;
- aparición de información periférica solo cuando su valor de acción supera un
  umbral.

No debe eliminarse toda la periferia por defecto: puede contener señales de
orientación, cambio de estado o peligro.

## Color, contraste y noche

El contraste de luminancia es más defendible que asignar significado solo a
colores. WCAG 2.2 usa una razón mínima de 4.5:1 para texto normal, pero esto es
un umbral de accesibilidad, no una receta universal de confort:

- https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum

En lectura degradada, menor contraste y mayor desenfoque alteran fijaciones,
regresiones y velocidad de lectura:

- https://pubmed.ncbi.nlm.nih.gov/36069942/

De noche, la luminancia y el componente melanópico importan. Estudios de
display vespertino muestran supresión de melatonina, mayor latencia de sueño y
desplazamiento circadiano con mayor irradiancia melanópica; bajar solo el azul
no garantiza un efecto uniforme:

- https://pubmed.ncbi.nlm.nih.gov/36854795/
- https://pubmed.ncbi.nlm.nih.gov/25535358/
- https://pubmed.ncbi.nlm.nih.gov/37192881/

La pupila se dilata en oscuridad y responde sobre todo a luminancia, aunque
también cambia con atención y esfuerzo. Por eso cualquier experimento de VIZZ
debe registrar o controlar la luz ambiental antes de interpretar pupila como
carga cognitiva:

- https://pubmed.ncbi.nlm.nih.gov/24243473/
- https://pubmed.ncbi.nlm.nih.gov/30723454/

## Herramientas candidatas

| Herramienta | Uso posible | Decisión inicial |
|---|---|---|
| SVG/Canvas/GLSL | prototipos de representación, color, movimiento y espacio | adoptar primero, bajo costo |
| WebGazer.js | mirada aproximada con webcam y procesamiento local | evaluar; mantenimiento oficial terminado en 2026 |
| Pupil Core | pupila y mirada con hardware dedicado | candidato de investigación, costo alto |
| PsychoPy/PsychoJS | estímulos, temporización y registro experimental | adoptar cuando exista un contraste perceptual concreto |
| OpenCV/MediaPipe | visión auxiliar y calibración | no introducir antes de necesitarla |

Fuentes: https://github.com/brownhci/WebGazer,
https://github.com/pupil-labs/pupil y https://psychopy.org/.

## Hipótesis inicial de VIZZ

Una representación adaptada a la zona de mirada y a la condición luminosa puede
reducir información irrelevante y mantener comprensión de la tarea, pero puede
perder contexto periférico y aumentar la sensación de control del sistema.

El primer experimento no necesita participantes: una misma traza de proceso se
renderizará en texto, panel fijo, timeline, campo gaze-contingent simulado y
movimiento. Se medirán área de información, contraste, densidad, latencia,
transiciones, contexto perdido y una tarea de decisión reproducible. Después,
y solo después, se evaluará mirada real.
