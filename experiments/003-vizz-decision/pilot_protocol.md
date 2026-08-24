# Piloto humano 003 — VIZZ

## Propósito

Medir si la representación modifica la decisión humana cuando la información
computacional es constante. Este es un piloto de instrumentación, no una
afirmación estadística sobre una población ni una evaluación del valor artístico.

## Advertencia metodológica vigente

La versión actual repite un único estado en las tres condiciones. Su orden
aleatorio no elimina el aprendizaje por exposición; por eso no debe usarse
para afirmar causalmente que VIZZ supera la vista estática. La
[auditoría metodológica](design-audit.md) exige conjuntos de prueba distintos
y balanceados antes de recoger datos interpretables.

## Procedimiento

1. Abrir `pilot.html` localmente.
2. Introducir un código anónimo de participante.
3. Usar un orden aleatorio generado por el piloto.
4. Completar las tres condiciones: tabla, vista estática y VIZZ candidata.
5. En cada condición elegir una acción, indicar confianza de 0 a 100, explicar
   el motivo y marcar si se detectó la incertidumbre relevante.
6. Descargar el JSON al terminar.

Antes de iniciar, la persona debe usar un código que no sea su nombre, correo
ni otro identificador directo. Puede abandonar la tarea sin descargar datos.
La decisión y la explicación pertenecen a la persona; el instrumento no debe
interpretarlas como una recomendación automática.

El piloto corregido admite teclado: se puede recorrer la interfaz con Tab,
activar las tarjetas VIZZ con Enter o Espacio y observar el foco visible. Si
algún control no resulta operable o legible, se debe detener la sesión y
registrar la incidencia separadamente de los resultados.

El piloto no envía datos a internet ni solicita nombre, correo u otra identidad.
El archivo descargado queda bajo control de la persona que ejecuta la prueba.
No se deben incorporar archivos humanos al repositorio sin autorización
explícita y una revisión de identificabilidad.

## Datos registrados

- código anónimo;
- semilla y orden de condiciones;
- condición;
- elección;
- duración;
- confianza;
- explicación;
- detección de incertidumbre;
- firma del estado mostrado.

## Regla de análisis

La regla de referencia es la función analítica declarada en
`decision-state.json`. Se reportarán por separado:

- exactitud respecto de esa regla;
- tiempo;
- calibración entre confianza y exactitud;
- detección de incertidumbre;
- cambios de decisión;
- calidad de la explicación;
- discrepancias justificadas por la persona.

## Kill test

VIZZ se elimina como operador independiente si el piloto no muestra una mejora
reproducible frente a la vista estática en la métrica definida, o si la mejora
desaparece al igualar la información. Una mejora puramente estética no cuenta.
