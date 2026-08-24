# Baseline 00 — estado inicial

Fecha: 2026-08-23

## Estado del repositorio

El repositorio comienza sin arquitectura de software ni dependencias de
ejecución. El punto de partida contiene únicamente la licencia del proyecto.
Esto permite investigar y seleccionar herramientas antes de heredar decisiones
estructurales.

## Resultado de la primera revisión conceptual

### CODE-INE

Tiene antecedentes fuertes en optimal stopping, algoritmos anytime,
metarazonamiento y bandits. Solo justifica un operador propio si incorpora el
estado material de un proceso creativo, reutilización, abandono, cambio de
representación e intervención humana.

### X-ANA-X

Tiene antecedentes fuertes en reformulación automática, abstracción, cambio de
coordenadas, state augmentation y representación alternativa de problemas.
Su frontera provisional es modificar variables, observables o el espacio de
búsqueda, no solamente codificar de otra forma el mismo objeto.

### KETAMINE

No tiene todavía una base conceptual propia. La búsqueda inicial encuentra una
familia extensa de equivalentes parciales: intermediate representations,
materialized views, índices, cachés, transformaciones semánticas y formatos de
intercambio. Su supervivencia depende de exigir una consulta declarada,
invariantes, costo de conversión y residuo explícito.

### VIZZ

Tiene antecedentes fuertes en visual analytics, external cognition,
visualización científica e interacción humano-computador. Solo se diferencia
de una visualización común si mejora una decisión humana medible.

## Herramientas candidatas iniciales

| Candidato | Función de investigación | Riesgo a controlar |
|---|---|---|
| OpenImageIO | inspección y conversión de imágenes | convertir formatos sin una pregunta explícita |
| SVG + parser geométrico | conservar paths y consultas geométricas | confundir representación con problema |
| Apache Arrow | comparar estructuras tabulares e intercambio | optimizar memoria antes de medir el workload |
| DuckDB | consultas pequeñas y reproducibles | introducir una base de datos antes de necesitarla |
| NetworkX o Cytoscape.js | grafo de paths y relaciones | asumir que un grafo explica causalidad |
| Vega-Lite | vistas declarativas comparables | llamar VIZZ a cualquier gráfico |
| OpenUSD | comprobar working sets y composición 3D | adoptar un ecosistema demasiado grande temprano |

## Decisión inicial

No instalar todo el catálogo. El primer experimento debe usar la menor cantidad
de herramientas que permita comparar una consulta preservada con una consulta
reformulada. Las herramientas de visualización se incorporarán después de que
la diferencia X-ANA-X/KETAMINE esté definida.

## Próxima evidencia requerida

1. Una consulta geométrica que pueda verificarse en todas las representaciones.
2. Una transformación que cambie solo la codificación.
3. Una transformación que añada o elimine una variable relevante.
4. Una tabla de costos y pérdidas, sin reducirla inicialmente a un único número.
5. Un kill test que pueda obligar a fusionar X-ANA-X y KETAMINE.
