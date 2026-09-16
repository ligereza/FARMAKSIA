# IRIS · archivo a portafolios exportables

Editor local para convertir una selección curatorial en tres salidas coordinadas: dossier PDF, portafolio web portable y ficha de proyecto. El estado editable conserva IDs estables, fuente/procedencia, texto, créditos, medio y orden manual.

## Ejecutar

Requiere Node.js 18 o superior. Usa `pdf-lib` y `@pdf-lib/fontkit` para producir PDF medible y validar cobertura tipográfica.

```powershell
npm start
# abrir http://localhost:4173
```

En la interfaz:

1. Carga la demo o importa un JSON con el mismo esquema.
2. Pulsa una pieza para incluirla/excluirla; selecciona una pieza para editarla en el inspector.
3. Usa las flechas para ensayar el orden. “Fecha” es una lectura temporal de la selección y no reemplaza el orden manual.
4. Guarda el JSON para recuperar decisiones y pulsa “Exportar salidas”; la interfaz muestra enlaces directos a PDF, JSON, HTML y ficha.

Los archivos generados aparecen en `outputs/`. La demo es sintética y está rotulada como tal: no representa obras reales ni autoría del artista.

## Motor sin navegador

El circuito también se ejecuta por CLI:

```powershell
node iris-cli.mjs import --source fixtures/mak-inbox-sample.json --out work/mak-sample-project.json
node iris-cli.mjs validate --state work/mak-sample-project.json
node iris-cli.mjs export --state work/mak-sample-project.json --out outputs/mak-sample --dimension date
node iris-cli.mjs edition --state work/mak-sample-project.json --id dossier --title "Dossier breve" --out work/dossier.json
node iris-cli.mjs compose --state work/dossier.json --profile dossier --out work/dossier-composition.json
node iris-cli.mjs package --state outputs/archivo-mak-muestra-verificada.json --out outputs/paquete-mak-muestra --root fixtures --resource-map fixtures/resource-map.json --strict-resources
```

`fixtures/mak-inbox-sample.json` es una copia local de cuatro metadatos del contrato real `faro-portfolio-inbox-v1`; no incluye medios. `fixtures/mak-archive-sample.json` cubre además el contrato de archivo `mak-archivo-v1`, con piezas y vínculos tipados. El importador conserva el registro crudo en `source.raw`, distingue `work`/`record`/`context` cuando el origen lo declara y no convierte automáticamente un registro en obra. `createEdition` permite varias ediciones del mismo origen; una reimportación actualiza sólo el origen, conserva selección, orden y texto autoral, y marca conflictos hasta una resolución explícita.

## Esquema mínimo

Consulta `demo-project.json` y `engine.mjs`. Cada elemento necesita un `id` estable y puede incluir `source.id`, `source.sourceId`, `title`, `description`, `credits`, `mediaType`, `date`, `tags`, `selected` y `status`. Un registro de proceso o contexto puede conservarse en el archivo sin ser seleccionado como obra. El plan común `iris.export-plan/1` alimenta PDF, HTML, ficha y JSON. `composeEdition` agrega un plan `iris.composition-plan/1` con restricciones duras, preferencias, mediciones, asignaciones de página/posición/espaciado, alternativas y estados `OPTIMAL`, `FEASIBLE`, `INFEASIBLE` o `UNKNOWN`.

## Verificación rápida

```powershell
npm run check
npm test
npm run smoke
Invoke-WebRequest http://localhost:4173/api/demo
$p = Get-Content -Raw demo-project.json
Invoke-WebRequest http://localhost:4173/api/export -Method Post -ContentType 'application/json' -Body $p
```

`npm run smoke` levanta el servidor en un puerto libre y comprueba la página estática, las cuatro salidas, sus URLs de revisión y el rechazo de payloads JSON mayores de 10 MB.

El PDF usa fuentes estándar o una TTF indicada explícitamente; no elimina tildes ni resume texto. HTML, ficha y JSON mantienen los caracteres originales. El web exportado no referencia rutas absolutas ni necesita el servidor para abrirse.

La validación estructural se hace cargando el resultado con `pdf-lib` y la revisión de contenido se hace en el lector PDF del navegador. Por defecto se usa Helvetica Base-14; una fuente TTF se embebe sólo cuando se indica explícitamente con `IRIS_FONT_PATH`. Si un carácter no tiene cobertura, la exportación falla con `PDF_UNSUPPORTED_CHARACTERS` y no produce un paquete engañoso.
