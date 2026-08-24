# Decisión 010 — composición condicional de X-ANA-X y KETAMINE

Fecha: 2026-08-23

## Evidencia

El experimento 005 aplica cuatro órdenes sobre el mismo SVG y el mismo
registro temporal. El arnés y su procedencia validan con Python estándar.

- `X_after_K_graph` no puede responder: el grafo lossy eliminó coordenadas.
- `K_graph_after_X` sí puede responder, porque X-ANA-X calculó el observable
  antes de que KETAMINE materializara las relaciones.
- `X_after_K_table` y `K_table_after_X` son equivalentes para este fixture y
  esta consulta, porque la tabla conserva la geometría requerida.

## Decisión

X-ANA-X y KETAMINE siguen siendo contratos distinguibles, pero su composición
no tiene una ley universal de conmutatividad. La capacidad resultante depende
de los invariantes retenidos por la representación, las precondiciones del
observable, el residuo y el orden de aplicación.

No se autoriza fusionarlos por nombre ni implementar una API todavía. Tampoco
se autoriza afirmar que siempre no conmutan: el par tabular ofrece un
contraejemplo controlado.

## Falsación parcial

Queda debilitada la hipótesis de que ambos nombres bastan para predecir el
resultado de una composición. También queda debilitada la hipótesis inversa de
que cualquier cambio de representación destruye una reformulación posterior.

## Próximo kill test

Repetir el experimento con una familia de representaciones que varíe de forma
controlada los invariantes retenidos: geometría completa, bounding boxes,
relaciones precalculadas y grafo con coordenadas. Medir capacidad de consulta,
residuo y costo. Si el resultado se explica completamente por conversión,
vistas o índices conocidos, KETAMINE no conserva una diferencia conceptual.

## Residuo

La frontera ahora es medible, pero el fixture es diminuto y no prueba
generalización a un corpus creativo. La dimensión temporal sigue dependiendo de
una fuente externa con procedencia; no debe atribuirse a la representación por
sí sola.
