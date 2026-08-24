# Literatura 001 — representación frente a reformulación

Esta lista no afirma novedad. Sirve para ubicar la frontera experimental y
evitar que KETAMINE o X-ANA-X vuelvan a nombrar teorías ya establecidas.

## Reformulación y cambio del espacio del problema

- [Eugene Fink, Automatic representation changes in problem solving](https://www.cs.cmu.edu/~eugene/research/abstract/phd-thesis.html). Estudia el espacio de representaciones posibles, los cambiadores de representación y la reutilización de nuevas descripciones.
- [Fuentetaja et al., Meta-Search Through the Space of Representations and Heuristics](https://ojs.aaai.org/index.php/AAAI/article/view/12091). Busca conjuntamente representación y heurística según cada problema.
- [Holte y Choueiry, Abstraction and reformulation in artificial intelligence](https://doi.org/10.1098/rstb.2003.1317). Distingue abstracción y reformulación como operaciones complementarias sobre representaciones.
- [Reformulation techniques for automated planning: a systematic review](https://www.cambridge.org/core/journals/knowledge-engineering-review/article/reformulation-techniques-for-automated-planning-a-systematic-review/E212DBCBDA3179FC41BFAD86A8E4332F). Muestra que reformular una tarea para cambiar el costo o el espacio de búsqueda tiene una tradición extensa.

## Transformación con preservación declarada

- [A Formal Semantics of the GraalVM Intermediate Representation](https://arxiv.org/abs/2107.01815). Formaliza transformaciones de una representación intermedia y propiedades que deben preservarse.
- [RVSDG: An Intermediate Representation for Optimizing Compilers](https://arxiv.org/abs/1912.05036). Relaciona estructura de la representación con optimización, tamaño, tiempo de compilación y sobrecarga.
- [Semantics of Database Transformations](https://www.pure.ed.ac.uk/ws/portalfiles/portal/16518115/Semantics_of_database_transformations.pdf). Trata corrección, preservación de información y transformaciones entre modelos de datos.
- [The Information Bottleneck Method](https://arxiv.org/abs/physics/0004057). Formula la búsqueda de representaciones compactas que retengan información relevante para una variable objetivo.

## Sistemas de órdenes y abstracción

- [Abstract interpretation and application to logic programs](https://www.di.ens.fr/~cousot/COUSOTpapers/JLP92.shtml). Proporciona una base para hablar de abstracción, pérdida de información y relaciones ordenadas entre representaciones.
- [Partial representations of orderings](https://arxiv.org/abs/2401.13383). Es relevante para la hipótesis de que una representación puede conservar solo el orden necesario para una tarea.

## Proyectos open source para contrastar

- [LLVM/MLIR](https://github.com/llvm/llvm-project): transformaciones e intermediate representations.
- [Apache Arrow](https://github.com/apache/arrow): intercambio columnar e interoperabilidad.
- [DuckDB](https://github.com/duckdb/duckdb): medir consultas y costos de materialización cuando el experimento lo requiera.
- [OpenUSD](https://github.com/PixarAnimationStudios/OpenUSD): composición, streaming y working sets de escenas.
- [OpenImageIO](https://github.com/AcademySoftwareFoundation/OpenImageIO): inspección, conversión y caching de imágenes.

## Lectura crítica para FARMAKSIA

La literatura ya cubre tanto la transformación de representación como el
cambio de espacio del problema. La diferencia útil para FARMAKSIA debe ser
operacional:

1. KETAMINE debe preservar una consulta o capacidad declarada y explicitar su
   residuo.
2. X-ANA-X debe cambiar el conjunto de variables, observables, estados o
   preguntas disponibles.
3. La adición de datos sin variación o sin nuevas preguntas no cuenta como
   reformulación.
4. Una vista que solo conserva una respuesta precalculada no es equivalente a
   conservar la estructura que permite recomputarla.
