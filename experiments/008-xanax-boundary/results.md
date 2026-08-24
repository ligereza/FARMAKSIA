# Resultados 008 — frontera de X-ANA-X

Fecha: 2026-08-23

## Rutas observadas

| Ruta | Entradas | Pregunta/observable | Representación | Resultado |
|---|---|---|---|---|
| `baseline-static` | SVG | intersección estática | fuente | `left-region` |
| `K_table-static` | SVG | misma intersección estática | tabla geométrica | `left-region` |
| `X_query-area` | SVG | umbral de área | fuente | `left-region`, `right-region` |
| `X_external-temporal` | SVG + eventos | intersección activa en `t=0.25` | fuente aumentada | `left-region` |
| `X_without-external` | SVG | intersección activa en `t=0.25` | fuente | no disponible |
| `K_after_X-temporal` | SVG + eventos | misma pregunta temporal | tabla temporal | `left-region` |
| `K_encoded-temporal` | SVG + eventos | misma pregunta temporal | índice temporal | `left-region` |

## Falsación

La consulta temporal no está disponible con SVG solo; requiere `events.json`.
Esto apoya que la dimensión temporal no debe atribuirse a una conversión pura
de representación. La tabla y el índice temporales pueden devolver la misma
respuesta, pero ambos contienen o dependen de la entrada externa.

El cambio de pregunta a área (`X_query-area`) sí altera el observable sin
añadir datos. Sin embargo, esa operación también es compatible con la idea
conocida de reformulación de consultas; el resultado no prueba novedad por sí
solo.

Las rutas que devuelven `left-region` tienen firmas de contrato distintas. La
respuesta observable, por sí sola, no identifica el operador: hay que conservar
entradas, pregunta, observable, representación y autoridad.

## Decisión provisional

X-ANA-X sobrevive solo como contrato explícito de cambio de espacio de
preguntas/observables/entradas. La frontera con KETAMINE no está en que el
resultado cambie, sino en qué datos y pregunta fueron declarados antes de la
transformación. No se demuestra una teoría nueva frente a reformulación,
state augmentation o materialización temporal conocidas.

El kill test de “X crea tiempo sin entrada temporal” pasa: sin eventos el
observable queda desconocido. El kill test de novedad conceptual queda abierto
hasta probar un caso creativo donde la reformulación no sea reducible a una
consulta conocida y el residuo/autoridad cambien de forma necesaria.
