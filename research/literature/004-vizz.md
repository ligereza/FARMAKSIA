# Literatura 004 — VIZZ: representación y decisión humana

## Antecedentes conceptuales

1. visual analytics;
2. external representations y external cognition;
3. sensemaking interactivo;
4. visualización científica con incertidumbre;
5. mixed-initiative interaction.

## Líneas bibliográficas

- [Fisher, Visual Analytics as a Translational Cognitive Science](https://onlinelibrary.wiley.com/doi/10.1111/j.1756-8765.2011.01148.x): conecta representaciones visuales, razonamiento analítico e incertidumbre.
- [Munzner, A Nested Model for Visualization Design and Validation](https://vispubs.com/?paper=10.1109%2FTVCG.2009.111): separa dominio/tarea, abstracción de datos, encoding/interaction y algoritmos; un error temprano puede invalidar una vista final.
- [Heer y Shneiderman, Interactive Dynamics for Visual Analysis](https://idl.cs.washington.edu/files/2012-InteractiveDynamics-CACM.pdf): trata la visualización como un proceso iterativo de operaciones y juicio humano.
- [The Human is the Loop: New Directions for Visual Analytics](https://www.pnnl.gov/publications/human-loop-new-directions-visual-analytics): formula la participación humana como parte del razonamiento, no como una aprobación posterior.
- [Horvitz, Mixed-Initiative Interaction](https://www.microsoft.com/en-us/research/publication/mixed-initiative-interaction/): proporciona una referencia para distribuir decisiones entre persona y sistema.

## Herramientas open source candidatas

- [Vega-Lite](https://github.com/vega/vega-lite): encoding declarativo y vistas reproducibles.
- [Cytoscape.js](https://github.com/cytoscape/cytoscape.js): modelo y renderer de grafos interactivos.
- [ParaView](https://github.com/Kitware/ParaView): visualización y análisis científico.
- [BORA](https://github.com/kit-ipe/bora): displays personalizados con control humano en tiempo real.

## Decisión para el piloto

No adoptar todavía una biblioteca de visualización. El primer piloto usará
HTML/SVG/JavaScript estándar para separar el efecto de la representación del
efecto de un framework.

VIZZ solo puede sobrevivir si cambia una decisión o una capacidad de
exploración humana medible. Una vista con más colores, más datos o mejor estética
no basta.
