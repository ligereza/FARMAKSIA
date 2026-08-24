# Experimento 008 — frontera de X-ANA-X

## Pregunta

¿Puede distinguirse X-ANA-X de una simple reformulación de consulta o de una
transformación KETAMINE cuando varias rutas producen la misma respuesta?

## Factores

El arnés separa cuatro factores que no deben colapsarse:

- conjunto de entradas: SVG solo o SVG más `events.json`;
- pregunta: intersección espacial, área o estado temporal;
- observable: relación estática o relación activa en `t = 0.25`;
- representación: fuente, tabla geométrica, estado temporal o índice
  materializado.

## Rutas

- baseline y `K_table` conservan la pregunta espacial;
- `X_query_area` cambia la consulta sin añadir datos;
- `X_external_temporal` incorpora eventos y cambia el observable;
- `K_after_X` materializa el resultado temporal después de X;
- `X_without_external` intenta responder sin la entrada temporal;
- `K_encoded_temporal` produce la misma respuesta temporal usando una
  representación que ya contiene la entrada externa.

## Kill tests

- Si el temporal responde sin `events.json`, la incorporación externa no es
  necesaria y la frontera X se debilita.
- Si una KETAMINE pura sobre SVG responde la consulta temporal, X se absorbe en
  conversión.
- Si las rutas con la misma respuesta también tienen el mismo contrato de
  entradas, pregunta, observable y autoridad, la distinción no es identificable
  y los nombres deben fusionarse.

El experimento no afirma que toda reformulación de consulta sea una teoría
nueva. Mide cuándo el cambio de espacio es solo un cambio de pregunta conocido
y cuándo depende de una entrada/observable adicional con procedencia.
