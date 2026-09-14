# FARMAKSIA: frontera de investigación

FARMAKSIA es un laboratorio autónomo de investigación. Su contenido activo
debe ser documentos, literatura, noticias, datos, hipótesis, protocolos,
resultados, procedencia y kill tests.

No es el runtime de escritorio, no es un plugin, no es un transporte móvil y
no debe recibir implementación específica de Adobe, Resolume u otro host.

## Cómo sale el trabajo

- Una hipótesis o evidencia que necesita asistencia se porta a
  X-ANA-X/PUPILA.
- Una hipótesis o evidencia que necesita integración de escritorio se porta a
  X-ANA-X/LUCIDA.
- Un contrato que afecta a ambas superficies se porta primero a
  X-ANA-X/main.
- XIO permanece como fuente futura de señales y transporte, no como
  dependencia implícita.

## Estado de los últimos experimentos

- 090 contiene evidencia mixta de una representación compartida, propuestas
  de asistencia y una frontera de renderizado. Es fuente de investigación;
  sus consumidores viven en PUPILA y LUCIDA.
- 091 registra una aceptación offline de la frontera LUCIDA. Su resultado es
  evidencia, no un runtime de FARMAKSIA.
- 092 registra la decisión de frontera de renderizado. La decisión operativa
  pertenece a LUCIDA; FARMAKSIA conserva la observación y su procedencia.

Las carpetas de experimentos existentes no se eliminan: son el registro
reproducible del laboratorio. No se debe agregar allí nueva lógica de
producto. Si un agente adopta un resultado, debe registrar el commit de
origen, el destino, la prueba ejecutada y lo que sigue sin verificarse.
