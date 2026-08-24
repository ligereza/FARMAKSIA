# Literatura 002 — procedencia, autoridad y derivación

## W3C PROV

[PROV Model Primer](https://www.w3.org/TR/prov-primer/) organiza la
procedencia alrededor de entidades, actividades y agentes. También distingue
uso, generación, derivación, responsabilidad y tiempo. Esto encaja con el
problema de FARMAKSIA: no basta saber que existe una representación; hay que
saber de dónde vino, qué actividad la produjo y quién autorizó una hipótesis.

[PROV-O](https://www.w3.org/TR/prov-o/) ofrece las relaciones `used`,
`wasGeneratedBy`, `wasDerivedFrom` y asociación con agentes. [PROV-DM](https://www.w3.org/TR/2012/CR-prov-dm-20121211/Overview.html)
separa el modelo de procedencia de cualquier aplicación concreta y permite
extensiones de dominio.

Un punto especialmente importante para FARMAKSIA es que PROV trata los
eventos como transiciones y distingue entidades de actividades. Esto evita
confundir “la geometría temporal existe como dato” con “el sistema descubrió
una nueva dimensión”.

## RO-Crate

[RO-Crate](https://www.researchobject.org/ro-crate/specification.html) ofrece
un empaquetado orientado a objetos de investigación, archivos, contexto y
procedencia. Es potencialmente útil cuando FARMAKSIA necesite transportar un
experimento completo, pero todavía sería demasiado amplio para el SVG mínimo.

## OpenLineage

[OpenLineage](https://github.com/OpenLineage/OpenLineage) define eventos de
lineage para runs, jobs y datasets, extensibles mediante facets. Su
[especificación](https://github.com/OpenLineage/OpenLineage/blob/main/spec/OpenLineage.md)
es relevante para registrar ejecuciones de herramientas, pero su unidad de
organización es una ejecución de datos, no una obra, hipótesis o decisión
humana. Debe evaluarse como interoperabilidad futura, no adoptarse ahora como
modelo conceptual principal.

## Decisión de investigación

Adoptar un manifiesto local pequeño, inspirado en las clases y relaciones
centrales de PROV, sin afirmar que sea una serialización PROV completa. Debe
registrar:

- entidades de entrada y derivadas;
- actividades que las usan y generan;
- agentes humanos y de software;
- autoridad de cada dato o hipótesis;
- consulta preservada;
- residuo y desconocidos;
- hashes de archivos locales.

La adopción será válida solo si el manifiesto puede detectar una referencia
rota o un archivo cambiado y si aclara cuándo una transformación recibió una
entrada adicional.
