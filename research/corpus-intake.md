# Contrato de ingreso de corpus creativo

Fecha: 2026-08-23

Este documento prepara el paso desde el fixture SVG mínimo hacia evidencia
representativa. No inventa un corpus ni descarga obras sin autoridad. Una
entrada solo se incorpora cuando se conoce su procedencia y se permite su uso
experimental.

La evaluación inicial de fuentes está en
[literatura 005](literature/005-corpus-sources.md); no debe confundirse
software open source con licencia de cada obra o asset.

## Registro mínimo por obra

- identificador anónimo de la obra y fuente;
- formato original: SVG, PNG, PSD, BLEND, USD, EXR, MP4, DXV, JSON, base de
  datos, grafo, embedding u otro;
- licencia, permiso o autoridad de uso;
- tamaño, resolución, duración, número de capas/nodos/entidades y dependencias;
- pregunta declarada que debe responderse;
- representaciones candidatas y sus invariantes;
- residuo esperado: estilo, geometría, orden, temporalidad, metadata,
  reversibilidad o contexto;
- costo de lectura, conversión, almacenamiento, cálculo y reconstrucción;
- hashes, comandos, versión de herramientas y resultado verificable.

## Muestra mínima deseada

Cuando existan fuentes autorizadas, se buscará al menos una entrada de cada
familia relevante:

1. vector con capas, estilos y geometría no trivial;
2. raster con resolución y metadata;
3. escena o grafo con jerarquía y dependencias;
4. secuencia temporal audiovisual o de estados;
5. datos estructurados asociados a la obra.

La muestra no se considerará representativa por cubrir cinco extensiones. Debe
contener consultas reales y casos donde una transformación pierda algo que
importe a una decisión creativa.

## Orden de trabajo

1. registrar fuente y autoridad;
2. congelar una copia o referencia reproducible;
3. declarar una consulta antes de transformar;
4. ejecutar baseline y una sola transformación;
5. medir capacidad, costo, residuo y reversibilidad;
6. aplicar kill test;
7. decidir si una herramienta se adopta, se difiere o se reemplaza.

## Estado

El repositorio contiene por ahora fixtures sintéticos y no debe presentarlos
como corpus creativo real. El siguiente ingreso válido requiere una obra o
conjunto de obras autorizado por la persona responsable, o una fuente pública
con licencia compatible que pueda citarse y conservarse con procedencia.
