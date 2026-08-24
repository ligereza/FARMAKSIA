# Investigación 011 — condiciones de display, filtros y corrección visual

Fecha: 2026-08-24

## Qué puede afirmarse

La pantalla puede cambiar parámetros de representación —luminancia,
contraste, escala, espaciado, densidad visual y composición cromática— sin
que esos cambios constituyan por sí mismos una corrección óptica ni una
medición de confort.

El National Eye Institute describe que el uso prolongado de computador puede
asociarse a fatiga y que el ojo seco puede dificultar leer o usar un computador,
pero esto no equivale a afirmar daño retinal por el monitor:

- https://www.nei.nih.gov/sites/default/files/2019-06/NEI_Healthy-Vision_booklet_WEB_508%20%281%29.pdf
- https://www.nei.nih.gov/sites/default/files/health-pdfs/factsaboutdryeye.pdf

## Filtros azules y lentes

La evidencia no permite tratar “bloquear azul” como una intervención universal.
Un ensayo doble ciego de 120 usuarios no encontró diferencias entre lentes
blue-blocking y lentes transparentes en síntomas o CFF después de una tarea de
computador:

- https://pubmed.ncbi.nlm.nih.gov/33587901/

Otro ensayo más pequeño encontró señales favorables para lentes de mayor
bloqueo, lo que deja una literatura mixta y dependiente del diseño:

- https://pubmed.ncbi.nlm.nih.gov/28118668/

VIZZ no debe prometer que un filtro visual evita fatiga ni recomendar cambiar
una receta. Una pantalla normal tampoco aplica automáticamente la prescripción
de miopía, astigmatismo o presbicia. La distancia de trabajo puede justificar
una evaluación óptica específica; un ensayo cruzado en personas présbitas
encontró diferencias entre progresivos generales y específicos para computador,
pero eso es una intervención óptica humana, no un CSS terapéutico:

- https://pubmed.ncbi.nlm.nih.gov/30339644/

## Noche y componente melanópico

La luz vespertina de un display puede afectar melatonina, latencia de sueño y
alerta, y la irradiancia melanópica no se reduce a “hacer la pantalla más
amarilla”. Un estudio controló luminancia y variación melanópica en condiciones
de display nocturno:

- https://pubmed.ncbi.nlm.nih.gov/36854795/

Esto justifica registrar una condición `night` como parámetro de exposición y
controlar horario/luminancia en un futuro protocolo. No autoriza inferir
melatonina, pupila, fatiga, ansiedad, intoxicación o estado farmacológico desde
el perfil elegido por una interfaz.

## Consecuencia para VIZZ

El prototipo puede verificar tres propiedades computacionales:

1. cambiar la condición de display no muta los eventos ni sus hashes;
2. el foco puede conservar una consulta declarada aunque pierda contexto
   anterior, y debe declarar ese residuo;
3. un campo agregado o un foco sin ancla debe devolver `unavailable`.

El experimento 025 implementa esas propiedades con fixtures locales. No
adopta sensores, lentes, corpus humano ni una afirmación clínica.
