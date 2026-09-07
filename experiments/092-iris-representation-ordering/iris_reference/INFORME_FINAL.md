# Informe de verificación · IRIS

La verificación queda ligada a la instancia original: recalcula alturas de texto y medios, valida el ancho exigido por la plantilla y rechaza mediciones o geometrías falsificadas antes de exportar.

## Resultado

Circuito funcional local: importar contrato real de inbox o archivo → crear ediciones independientes → seleccionar → ordenar → editar → reimportar sin pisar decisiones → resolver conflictos → componer con restricciones medibles → exportar perfiles y paquete portable desde un plan común, sin depender del navegador.

## Evidencia ejecutada

- `npm run check`: correcto para servidor, cliente, motor y CLI.
- `npm test`: correcto para contrato real, IDs, reimportación, conflictos, orden, texto largo/Unicode y parseo PDF.
- `npm run smoke`: correcto en servidor aislado; verifica página estática, exportación de cuatro salidas, URLs `/outputs/...`, recuperación de un PDF y rechazo `413` para payloads mayores de 10 MB.
- `GET /api/contract-sample`: contrato local `faro-portfolio-inbox-v1`, cuatro registros de muestra; la muestra remota observada tenía 7.044 registros y hash registrado en el manifiesto.
- `GET /api/archive-sample` / `POST /api/import-archive`: adaptador local de `mak-archivo-v1`, tres obras y un vínculo tipado; `archivo.json` remoto observado con 2.034 piezas/5.812 vínculos y `campo.json` con 219 piezas.
- `POST /api/import`, `POST /api/validate` y `POST /api/export`: correctos con la muestra real de metadatos; exportó dos registros seleccionados con sus IDs y `sourceId`.
- `POST /api/resolve` y CLI `resolve`: resolución `keep-edits`/`accept-source` con revisión esperada; una revisión obsoleta se rechaza.
- CLI sin navegador: importación, validación y paquete completo PDF/JSON/HTML/ficha ejecutados.
- Dos ediciones del mismo origen: `dossier` y `extended` comparten `originId` pero mantienen selecciones/títulos independientes.
- Perfiles declarativos: `dossier` rechaza más de 6 piezas; `portfolio` no impone ese límite. El orden `context` sólo usa campos declarados de proyecto/contexto/categoría.
- Paquete portable: `portfolio.pdf`, `portfolio.html`, `ficha.html`, `plan.json`, `manifest.json` y medios sintéticos con hash; se copió a otra carpeta y mantuvo rutas relativas, sin `source.raw` en el plan público.
- Composición: `composeEdition` usa programación dinámica de orden fijo con estado `(posición, plantilla anterior, páginas usadas)`; preserva selección/orden humano, mide wrapping y proporción declarada del medio, conserva relaciones y produce alternativas por firma de ruta. El enumerador exhaustivo queda disponible como referencia acotada y `verifyComposition` valida el resultado independientemente. Distingue `OPTIMAL`, `FEASIBLE`, `INFEASIBLE` y `UNKNOWN` por límite de tiempo.
- PDF cargado por `pdf-lib` para validación estructural y por el lector PDF del navegador: 1 página, texto visible, orden y fuentes legibles. No había `pdftotext`/`qpdf`/`pypdf` disponible en el entorno; no se presenta `pdf-lib` como extractor independiente de su propio generador.
- El HTML generado no contiene rutas `C:\` ni `file://`.
- La interfaz muestra enlaces directos a las salidas exportadas y los invalida al modificar selección, orden, perfil, alternativa o contenido editorial.

## Artefactos de demostración

La demo usa un corpus sintético explícito. Incluye una pieza sin media, un video con enlace y un contexto que permanece fuera de la selección para comprobar que un registro no se convierte silenciosamente en obra.

## Comparación antes/después

Antes, `server.mjs` generaba PDF con objetos manuales, eliminaba diacríticos, truncaba cada línea a 110 caracteres y mezclaba offsets calculados con representaciones binarias. Además, API/CLI validaban después de una normalización reparadora y el CLI sólo producía PDF/JSON; archivo y inbox no compartían conflictos. Después, `engine.mjs` valida el input original, conserva diagnósticos, distingue origen/edición, usa `pdf-lib` + `fontkit`, wrapping por ancho de fuente, perfiles, recursos con hash, composición declarativa y un plan compartido que produce los cuatro formatos; las regresiones cubren merge, dos ediciones, conflictos efectivos, fechas, relaciones paralelas, texto largo, Unicode, referencias, alternativas, precedencia incompatible, estados de búsqueda y paquete portable.

## Limitación conocida

El motor no copia medios del Hub por defecto: conserva `asset_path`/`medio.src` y disponibilidad como procedencia. El resolvedor portable acepta raíces autorizadas y mapas explícitos; PNG/JPG se miden por sus cabeceras y se incrustan en PDF, y el subconjunto SVG usado por la demo se materializa como vector (rectángulo, círculos y texto), con placeholder explícito si el SVG no es compatible. La demostración usa un poster SVG sintético y una prueba PNG 1×1; marca cualquier faltante. Las muestras reales fueron verificadas sólo como metadatos locales; no se hizo despliegue remoto ni se modificó MAK. El PDF usa Helvetica Base-14 por defecto (licencia estándar) o una fuente indicada explícitamente por `IRIS_FONT_PATH`; no depende silenciosamente de `C:/Windows/Fonts`.
