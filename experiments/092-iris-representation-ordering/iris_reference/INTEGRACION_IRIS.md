# Nota de integración

Esta carpeta es una implementación local y portable del frente IRIS. No modifica los repositorios fuente ni el Hub de MAK.

## Qué reutiliza del modelo conceptual

- separación entre registro, obra, contexto y fuente;
- IDs estables y procedencia explícita;
- selección humana reversible;
- exportaciones derivadas de un estado único;
- incertidumbre y material ausente visibles en vez de inventar contenido.

## Qué aporta

- editor local usable en Windows con dependencias explícitas (`pdf-lib` y `@pdf-lib/fontkit`);
- importación y guardado del proyecto JSON;
- orden manual más una lectura temporal;
- edición de título, descripción, créditos y estado editorial;
- dossier PDF, HTML portable y ficha coordinados;
- corpus demo sintético con imagen ausente, video enlazado y contexto no seleccionado.
- `engine.mjs` y `iris-cli.mjs`: importación/normalización del contrato `faro-portfolio-inbox-v1`, merge conservador, validación, orden por fecha y plan común de exportación.
- Adaptador `mak-archivo-v1`: conserva piezas, clases `obra`/`codigo`/otras, vínculos tipados y la referencia al campo espacial cuando existe.
- Conflictos durables: `keep-edits`/`accept-source`, revisión esperada y escritura atómica del estado desde CLI.
- `fixtures/mak-inbox-sample.json`: cuatro metadatos observados de MAK, sin copiar medios; `fixtures/mak-inbox-sample.manifest.json` registra procedencia y hash observado.
- perfiles `dossier`/`portfolio`, `createEdition` para ediciones independientes y `writePortablePackage` para paquete con manifest y recursos hasheados.
- `composeEdition` para distribuir la selección bloqueada en páginas y plantillas discretas, con medición tipográfica/media, restricciones obligatorias, preferencias exploratorias, precedencia declarada, alternativas y estados verificables.
- Para integrar en el proyecto original: conservar `iris.project/2` como instancia, llamar `composeEdition` después de la selección editorial, exigir `verification.ok` antes de renderizar y pasar el mismo plan a PDF/HTML. Mantener el enumerador sólo como comparación de corpus pequeño; ampliar el estado o introducir solver general únicamente ante restricciones no locales.
- `resolveResources` sólo busca bajo raíces autorizadas; el plan público omite `source.raw` y el manifest informa completitud, hashes y faltantes.

## Puente hacia MAK

El adaptador local traduce muestras del inbox y del archivo al esquema `iris.project/2` sin copiar medios. En el inbox, la correspondencia es `source.id` ← identificador de registro, `source.sourceId` ← `publicacion_id`, `id` ← identificador estable y `source.assetPath`/`assetAvailable` ← referencia de medio. En archivo, `entityType` conserva la clase de pieza y `relations` conserva `de`, `a`, peso y clase. `source.raw` conserva campos no soportados. Las hipótesis de relación deben entrar como campos separados y nunca como crédito o atribución.

## Pendientes deliberadamente abiertos

- permisos y política de publicación del corpus real;
- resolución de miniaturas/medios reales del Hub;
- integración con contratos vigentes de MAK;
- validación con el artista sobre campos curatoriales y textos públicos.

No se presenta la demo como evidencia de obras terminadas ni de adopción por terceros.
