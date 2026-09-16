import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';
import fontkit from '@pdf-lib/fontkit';

export const SCHEMA = 'iris.project/2';
export const EDITION_PROFILES = {
  dossier: { id: 'dossier', label: 'Dossier breve', maxItems: null, maxPages: 12 },
  portfolio: { id: 'portfolio', label: 'Portafolio extendido', maxItems: null, maxPages: 24 }
};

const clone = value => JSON.parse(JSON.stringify(value));
const text = value => value == null ? '' : String(value);
const hashJson = value => crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex');
const htmlEsc = (s='') => text(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function parseSourceDate(value) {
  const raw = text(value).trim(); if (!raw) return { raw, valid: false, key: null };
  if (/^\d{4}$/.test(raw)) return { raw, valid: true, precision: 'year', key: `${raw}-01-01` };
  const match = raw.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (match) { const [year, month, day] = match.slice(1).map(Number); const d = new Date(Date.UTC(year, month - 1, day)); const valid = d.getUTCFullYear() === year && d.getUTCMonth() === month - 1 && d.getUTCDate() === day; return { raw, valid, precision: 'day', key: valid ? raw : null }; }
  const d = new Date(raw); return Number.isNaN(d.getTime()) ? { raw, valid: false, precision: 'unknown', key: null } : { raw, valid: true, precision: 'instant', key: d.toISOString().slice(0,10) };
}

function profileOf(profile) { if (typeof profile === 'string') { const found = EDITION_PROFILES[profile]; if (!found) throw new Error(`Perfil desconocido: ${profile}`); return found; } return profile || EDITION_PROFILES.portfolio; }
function originId(project) { return project.origin?.originId || `origin:${text(project.source?.schema || 'unknown')}`; }

function sourceItems(input) {
  if (Array.isArray(input)) return { schema: 'array', complete: true, items: input };
  if (input && Array.isArray(input.items)) return { schema: text(input.schema || 'unknown'), complete: input.complete !== false && input.snapshotMode !== 'partial', items: input.items };
  throw new Error('El archivo de origen debe ser una lista o un objeto con items[].');
}

export function normalizeInbox(input) {
  const envelope = sourceItems(input);
  const seen = new Set(); const errors = []; const items = [];
  for (const [index, raw] of envelope.items.entries()) {
    if (!raw || typeof raw !== 'object') { errors.push(`items[${index}] no es un objeto`); continue; }
    const id = text(raw.id || raw.item_id).trim();
    if (!id) { errors.push(`items[${index}] no tiene id`); continue; }
    if (seen.has(id)) { errors.push(`ID duplicado en origen: ${id}`); continue; }
    seen.add(id);
    const contentType = text(raw.tipo_contenido || raw.content_type || 'media').trim(); const sourceTitle = text(raw.titulo || raw.title); const sourceDescription = text(raw.descripcion_original || raw.description_original || raw.description); const sourceCredits = text(raw.creditos || raw.credits);
    items.push({
      id, entityType: 'record', title: sourceTitle, description: sourceDescription, credits: sourceCredits, overrides: {},
      selected: false, status: 'revisar', manualOrder: index,
      source: {
        schema: envelope.schema, id,
        sourceId: text(raw.publicacion_id || raw.publication_id || id).trim(),
        kind: contentType, date: text(raw.fecha || raw.date).trim(), dateInfo: parseSourceDate(raw.fecha || raw.date),
        assetPath: text(raw.asset_path || raw.assetPath).trim(),
        assetAvailable: Boolean(raw.asset_available ?? raw.assetAvailable),
        raw: clone(raw), baseFields: { title: sourceTitle, description: sourceDescription, credits: sourceCredits }
      },
      tags: Array.isArray(raw.tags) ? clone(raw.tags) : [],
      mediaType: contentType === 'story' ? 'story' : contentType === 'published_media' ? 'media' : 'registro'
    });
  }
  return { schema: envelope.schema, complete: envelope.complete, items, errors };
}

export function normalizeArchiveBundle(input) {
  const archive = input?.archivo || input;
  const field = input?.campo || null;
  if (!archive || !Array.isArray(archive.piezas)) throw new Error('El archivo debe contener piezas[].');
  const positions = new Map((field?.piezas || []).filter(x => x?.id).map(x => [text(x.id), { x: x.x, y: x.y, estilo: x.estilo, tipo: x.tipo }]));
  const seen = new Set(); const errors = []; const items = [];
  for (const [index, raw] of archive.piezas.entries()) {
    const id = text(raw?.id).trim(); if (!id) { errors.push(`piezas[${index}] no tiene id`); continue; }
    if (seen.has(id)) { errors.push(`ID duplicado en archivo: ${id}`); continue; } seen.add(id);
    const kind = text(raw.clase || 'desconocido');
    const entityType = kind === 'obra' ? 'work' : kind === 'codigo' ? 'record' : 'context';
    const media = raw.medio && typeof raw.medio === 'object' ? raw.medio : {};
    const sourceTitle = text(raw.titulo), sourceDescription = text(raw.resumen), sourceCredits = text(raw.creditos || raw.credits);
    items.push({ id, entityType, title: sourceTitle, description: sourceDescription, credits: sourceCredits, overrides: {}, selected: false, status: 'revisar', manualOrder: index,
      source: { schema: text(archive.version || 'mak-archivo-v1'), id, sourceId: id, kind, date: text(raw.fecha), dateInfo: parseSourceDate(raw.fecha), assetPath: text(media.src), assetAvailable: Boolean(media.src), position: positions.get(id) || null, raw: clone(raw), baseFields: { title: sourceTitle, description: sourceDescription, credits: sourceCredits } },
      tags: Array.isArray(raw.etiquetas) ? clone(raw.etiquetas) : [], mediaType: text(media.tipo || 'registro') });
  }
  const ids = new Set(items.map(x => x.id)); const relations = [];
  for (const [index, raw] of (archive.vinculos || []).entries()) {
    const sourceId = text(raw?.de), targetId = text(raw?.a); if (!ids.has(sourceId) || !ids.has(targetId)) { errors.push(`vinculos[${index}] referencia ausente`); continue; }
    const type = text(raw.clase || 'unknown'); const relationId = text(raw.id).trim() || `${sourceId}->${targetId}:${type}:${index}`;
    relations.push({ id: relationId, sourceId, targetId, type, weight: raw.peso ?? null, scope: 'declared', raw: clone(raw) });
  }
  return { schema: text(archive.version || 'mak-archivo-v1'), complete: archive.complete !== false && archive.snapshotMode !== 'partial', items, relations, errors, meta: clone(archive.meta || {}) };
}

export function importArchiveBundle(input, existing = null) {
  const normalized = normalizeArchiveBundle(input); const prior = existing ? normalizeProject(existing) : normalizeProject({ title: 'Archivo MAK importado por IRIS' });
  const merged = mergeImportedItems(normalized.items, prior);
  const importedIds = new Set(normalized.items.map(x => x.id));
  for (const old of prior.items) if (!importedIds.has(old.id)) merged.push({ ...old, sourceState: normalized.complete ? 'missing_from_latest_source' : 'not_in_partial_snapshot' });
  const oldOrder = prior.orderIds || []; const orderIds = [...oldOrder.filter(id => merged.some(x => x.id === id)), ...merged.map(x => x.id).filter(id => !oldOrder.includes(id))];
  const relationMap = new Map((prior.relations || []).map(x => [x.id, x]));
  for (const relation of normalized.relations) relationMap.set(relation.id, relation);
  const conflicts = [...(prior.conflicts || [])];
  for (const item of merged) if (item.editorialConflict === 'source_updated' && !conflicts.some(c => c.itemId === item.id && c.status === 'open')) conflicts.push({ id: `${item.id}:${item.source.revision}`, itemId: item.id, field: 'editorial-source', fields: clone(item.sourceChanges || {}), status: 'open', previousRevision: item.source.previous?.revision || '', incomingRevision: item.source.revision });
  return withRevision({ ...prior, source: { schema: normalized.schema, importedAt: null, complete: normalized.complete, itemCount: normalized.items.length, meta: normalized.meta }, orderIds, items: orderIds.map(id => merged.find(x => x.id === id)), relations: [...relationMap.values()], conflicts, importErrors: normalized.errors, errors: normalized.errors });
}

function editorialFrom(old) {
  return {
    title: text(old.title), description: text(old.description), credits: text(old.credits),
    selected: Boolean(old.selected), status: text(old.status || 'revisar'),
    manualOrder: Number.isFinite(old.manualOrder) ? old.manualOrder : null,
    tags: Array.isArray(old.tags) ? clone(old.tags) : [], overrides: clone(old.overrides || {})
  };
}

function withRevision(project) {
  const copy = clone(project); delete copy.revision; copy.revision = hashJson(copy); return copy;
}

function mergeImportedItems(incomingItems, prior) {
  const oldById = new Map(prior.items.map(item => [item.id, item]));
  return incomingItems.map((incoming, index) => {
    const old = oldById.get(incoming.id); if (!old) return { ...incoming, manualOrder: index };
    const sourceChanged = hashJson(incoming.source.raw) !== hashJson(old.source?.raw || {}); const priorBase = old.source?.baseFields || { title: text(old.title), description: text(old.description), credits: text(old.credits) }; const oldOverrides = old.overrides || {}; const overrides = { ...oldOverrides }; const sourceChanges = {};
    for (const field of ['title','description','credits']) { const explicitlyEdited = Object.prototype.hasOwnProperty.call(oldOverrides, field) || text(old[field]) !== text(priorBase[field]); if (explicitlyEdited) { overrides[field] = text(old[field]); if (sourceChanged && text(incoming[field]) !== text(priorBase[field])) sourceChanges[field] = { previousBase: text(priorBase[field]), incomingBase: text(incoming[field]), keptEdition: text(old[field]) }; } }
    const nextEditorial = { title: Object.hasOwn(overrides,'title') ? overrides.title : incoming.title, description: Object.hasOwn(overrides,'description') ? overrides.description : incoming.description, credits: Object.hasOwn(overrides,'credits') ? overrides.credits : incoming.credits };
    const existingConflicts = (prior.conflicts || []).filter(c => c.itemId === incoming.id);
    const previousRevision = old.source?.revision || hashJson(old.source?.raw || {});
    const incomingRevision = hashJson(incoming.source.raw);
    const conflictOpen = existingConflicts.some(c => c.status === 'open');
    const conflict = Object.keys(sourceChanges).length && !conflictOpen ? { id: `${incoming.id}:${incomingRevision}`, itemId: incoming.id, field: 'editorial-source', fields: sourceChanges, status: 'open', previousRevision, incomingRevision } : null;
    const source = { ...incoming.source, revision: incomingRevision, previous: sourceChanged ? clone(old.source) : old.source?.previous };
    return { ...incoming, source, ...nextEditorial, overrides,
      selected: old.selected, status: old.status, tags: old.tags, manualOrder: old.manualOrder,
      entityType: old.entityType, conflicts: existingConflicts, ...(conflict ? { conflictStatus: 'open' } : {}), ...(Object.keys(sourceChanges).length ? { editorialConflict: 'source_updated', sourceChanges } : {}) };
  });
}

export function normalizeProject(project = {}) {
  const oldItems = Array.isArray(project.items) ? project.items : [];
  const byId = new Map(oldItems.filter(x => x && x.id).map(x => [text(x.id), x]));
  const order = Array.isArray(project.orderIds) ? project.orderIds.map(text) : oldItems.map(x => text(x.id));
  const uniqueOrder = [...new Set(order.filter(id => byId.has(id)))];
  for (const item of oldItems) if (item?.id && !uniqueOrder.includes(text(item.id))) uniqueOrder.push(text(item.id));
  const items = uniqueOrder.map((id, index) => {
    const old = byId.get(id); const editorial = editorialFrom(old);
    return { ...clone(old), ...editorial, id, manualOrder: editorial.manualOrder ?? index,
      source: clone(old.source || { id, sourceId: id, schema: 'unknown', raw: {} }),
      entityType: text(old.entityType || 'record'), mediaType: text(old.mediaType || 'registro') };
  });
  return { schemaVersion: SCHEMA, editionId: text(project.editionId || 'default'), editionProfile: text(project.editionProfile || 'portfolio'), origin: clone(project.origin || { originId: originId(project), schema: text(project.source?.schema || 'unknown') }), title: text(project.title || 'Portafolio IRIS'), subtitle: text(project.subtitle),
    curatorialQuestion: text(project.curatorialQuestion), demoNotice: text(project.demoNotice), precedence: clone(project.precedence || []),
    source: clone(project.source || { schema: 'unknown', importedAt: null }), orderIds: items.map(x => x.id),
    ordering: clone(project.ordering || { dimension: 'manual', reason: 'Orden conservado del estado editorial.' }), relations: clone(project.relations || []), conflicts: clone(project.conflicts || []), errors: clone(project.errors || project.importErrors || []), migration: project.schemaVersion === SCHEMA ? clone(project.migration || null) : { from: project.schemaVersion || 'legacy-v1', to: SCHEMA, steps: ['derive-orderIds','preserve-source-raw'] }, profiles: clone(project.profiles || {}), revision: project.revision || null, items };
}

export function importInbox(input, existing = null) {
  const normalized = normalizeInbox(input); const prior = existing ? normalizeProject(existing) : normalizeProject({ title: 'Archivo importado por IRIS' });
  const importedIds = new Set(normalized.items.map(item => item.id));
  const merged = mergeImportedItems(normalized.items, prior);
  for (const old of prior.items) if (!importedIds.has(old.id)) merged.push({ ...old, sourceState: normalized.complete ? 'missing_from_latest_source' : 'not_in_partial_snapshot' });
  const oldOrder = prior.orderIds || [];
  const orderIds = [...oldOrder.filter(id => merged.some(x => x.id === id)), ...merged.map(x => x.id).filter(id => !oldOrder.includes(id))];
  const conflicts = [...(prior.conflicts || [])];
  for (const item of merged) if (item.editorialConflict === 'source_updated' && !conflicts.some(c => c.itemId === item.id && c.status === 'open')) conflicts.push({ id: `${item.id}:${item.source.revision}`, itemId: item.id, field: 'editorial-source', fields: clone(item.sourceChanges || {}), status: 'open', previousRevision: item.source.previous?.revision || '', incomingRevision: item.source.revision });
  return withRevision({ ...prior, source: { schema: normalized.schema, importedAt: null, complete: normalized.complete, itemCount: normalized.items.length }, orderIds, items: orderIds.map(id => merged.find(x => x.id === id)), conflicts, importErrors: normalized.errors, errors: normalized.errors });
}

export function createEdition(project, editionId, options = {}) {
  const check = validateProject(project); if (!check.ok) throw new Error(check.errors.join('; '));
  const base = normalizeProject(project); const id = text(editionId).trim(); if (!id) throw new Error('editionId requerido');
  return withRevision({ ...base, editionId: id, origin: { ...clone(base.origin), originId: originId(base) }, title: text(options.title || base.title), subtitle: text(options.subtitle ?? base.subtitle), profiles: clone(options.profiles || base.profiles || {}) });
}

export function orderBy(project, dimension = 'manual') {
  const check = validateProject(project); if (!check.ok) throw new Error(check.errors.join('; ')); const normalized = normalizeProject(project); const index = new Map(normalized.orderIds.map((id, i) => [id, i]));
  if (dimension === 'manual') { normalized.ordering = { dimension, reason: 'Orden definido por la persona.' }; return normalized; }
  if (!['date','context'].includes(dimension)) throw new Error(`Dimensión no soportada: ${dimension}`);
  normalized.orderIds.sort((a, b) => {
    if (dimension === 'context') { const get = id => { const item = normalized.items.find(x => x.id === id); const raw = item?.source?.raw || {}; return text(raw.context || raw.proyecto || raw.project || raw.extra?.categoria).trim(); }; const aa = get(a), bb = get(b); if (!aa && !bb) return index.get(a)-index.get(b); if (!aa) return 1; if (!bb) return -1; return aa.localeCompare(bb) || index.get(a)-index.get(b) || a.localeCompare(b); }
    const aa = normalized.items.find(x => x.id === a)?.source?.dateInfo || parseSourceDate(normalized.items.find(x => x.id === a)?.source?.date);
    const bb = normalized.items.find(x => x.id === b)?.source?.dateInfo || parseSourceDate(normalized.items.find(x => x.id === b)?.source?.date);
    if (!aa.valid && !bb.valid) return index.get(a) - index.get(b);
    if (!aa.valid) return 1; if (!bb.valid) return -1;
    return aa.key.localeCompare(bb.key) || index.get(a) - index.get(b) || a.localeCompare(b);
  });
  normalized.ordering = { dimension: dimension, reason: dimension === 'date' ? 'Fecha de origen; fechas inválidas/desconocidas al final y desempate por orden previo.' : 'Agrupación por contexto/proyecto/categoría declarada; desconocidos al final y desempate por orden previo.' };
  return withRevision(normalized);
}

export function resolveConflict(project, itemId, decision, expectedRevision = null) {
  const current = normalizeProject(project); if (expectedRevision && current.revision !== expectedRevision) throw new Error('STALE_REVISION: el proyecto cambió desde la lectura.');
  const item = current.items.find(x => x.id === itemId); if (!item) throw new Error(`No existe item: ${itemId}`);
  const open = (current.conflicts || []).filter(c => c.itemId === itemId && c.status === 'open'); if (!open.length) throw new Error(`No hay conflicto abierto para: ${itemId}`);
  if (!['keep-edits','accept-source'].includes(decision)) throw new Error('Decisión inválida: use keep-edits o accept-source.');
  current.conflicts = current.conflicts.map(c => c.itemId === itemId && c.status === 'open' ? { ...c, status: decision === 'keep-edits' ? 'resolved_keep_edits' : 'resolved_accept_source', resolution: decision } : c);
  current.items = current.items.map(x => {
    if (x.id !== itemId) return x; if (decision === 'keep-edits') return { ...x, conflictStatus: 'resolved', editorialConflict: undefined };
    const sourceFields = {}; const base = x.source?.baseFields || {};
    for (const field of ['title','description','credits']) if (Object.prototype.hasOwnProperty.call(base, field)) sourceFields[field] = text(base[field]);
    return { ...x, ...sourceFields, conflictStatus: 'resolved', editorialConflict: undefined, sourceResolution: Object.keys(sourceFields).length ? 'source_fields_applied' : 'source_metadata_only' };
  });
  return withRevision(current);
}

export function validateProject(project) {
  const errors = []; const rawItems = Array.isArray(project?.items) ? project.items : []; const rawSeen = new Set();
  if (!project || typeof project !== 'object') errors.push('El proyecto debe ser un objeto.');
  if (!Array.isArray(project?.items)) errors.push('El proyecto debe contener items[].');
  for (const item of rawItems) { const id = text(item?.id).trim(); if (!id) errors.push('Item sin id.'); if (rawSeen.has(id)) errors.push(`ID duplicado: ${id}`); rawSeen.add(id); if (!item?.source?.id) errors.push(`Sin source.id: ${id || '(vacío)'}`); }
  const ids = rawSeen;
  if (project?.orderIds !== undefined) {
    if (!Array.isArray(project.orderIds)) errors.push('orderIds debe ser una lista.');
    else { const order = project.orderIds.map(text); if (new Set(order).size !== order.length) errors.push('orderIds contiene duplicados.'); if (order.some(id => !ids.has(id))) errors.push('orderIds contiene IDs desconocidos.'); if (order.length !== ids.size) errors.push('orderIds no cubre exactamente todos los items.'); }
  }
  for (const relation of project?.relations || []) for (const key of ['sourceId', 'targetId']) if (relation[key] && !ids.has(relation[key])) errors.push(`Relación ${key} ausente: ${relation[key]}`);
  for (const error of project?.errors || project?.importErrors || []) errors.push(`Origen: ${error}`);
  return { ok: errors.length === 0, errors, project: errors.length ? clone(project) : normalizeProject(project) };
}

export function exportPlan(project, profile = 'portfolio') {
  const check = validateProject(project); if (!check.ok) throw new Error(check.errors.join('; ')); const normalized = normalizeProject(project);
  const profileSpec = profileOf(profile); const selectedCount = normalized.items.filter(x => x.selected).length; const diagnostics = [];
  if (profileSpec.maxItems != null && selectedCount > profileSpec.maxItems) diagnostics.push({ code: 'PROFILE_MAX_ITEMS', message: `${profileSpec.label} admite ${profileSpec.maxItems} piezas; hay ${selectedCount}.` });
  const selected = new Set(normalized.items.filter(x => x.selected).map(x => x.id));
  return { schema: 'iris.export-plan/1', profile: profileSpec.id, diagnostics, editionId: normalized.editionId, originId: normalized.origin?.originId, title: normalized.title, subtitle: normalized.subtitle,
    curatorialQuestion: normalized.curatorialQuestion, ordering: clone(normalized.ordering),
    items: normalized.orderIds.filter(id => selected.has(id)).map((id, position) => { const x = normalized.items.find(item => item.id === id); return { position: position + 1, id: x.id, sourceId: x.source.sourceId || x.source.id, title: x.title, description: x.description, credits: x.credits, mediaType: x.mediaType, source: clone(x.source), tags: clone(x.tags || []) }; }) };
}

const COMPOSITION_TEMPLATES = {
  single: { maxItems: 1, label: 'una pieza' },
  split: { maxItems: 2, label: 'dos columnas' },
  stack: { maxItems: 3, label: 'secuencia vertical' }
};

function declaredPrecedence(project) {
  const explicit = Array.isArray(project.precedence) ? project.precedence : [];
  const fromRelations = (project.relations || []).filter(r => ['precedence', 'precedes', 'before'].includes(text(r.type).toLowerCase()));
  return [...explicit, ...fromRelations].map(r => ({ before: text(r.before || r.sourceId), after: text(r.after || r.targetId) })).filter(r => r.before && r.after);
}

function measureSvg(file) {
  const source = file.toString('utf8'); const viewBox = source.match(/viewBox=["']\s*[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+([\d.]+)\s*["']/i);
  const width = source.match(/\bwidth=["']([\d.]+)(?:px)?["']/i)?.[1]; const height = source.match(/\bheight=["']([\d.]+)(?:px)?["']/i)?.[1];
  const w = Number(viewBox?.[1] || width), h = Number(viewBox?.[2] || height); return Number.isFinite(w) && Number.isFinite(h) && w > 0 && h > 0 ? { width: w, height: h, aspectRatio: w / h, measuredBy: 'svg-viewBox-or-size' } : null;
}

function measureRaster(file, ext) {
  if (ext === '.png' && file.length >= 24 && file.subarray(0, 8).toString('hex') === '89504e470d0a1a0a') return { width: file.readUInt32BE(16), height: file.readUInt32BE(20), measuredBy: 'png-IHDR' };
  if (['.jpg', '.jpeg'].includes(ext) && file.length > 4 && file[0] === 0xff && file[1] === 0xd8) { let offset = 2; while (offset + 9 < file.length) { if (file[offset] !== 0xff) { offset++; continue; } const marker = file[offset + 1]; const length = file.readUInt16BE(offset + 2); if ([0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf].includes(marker)) return { width: file.readUInt16BE(offset + 7), height: file.readUInt16BE(offset + 5), measuredBy: 'jpeg-SOF' }; offset += 2 + length; } }
  return null;
}

async function measureResource(entry) {
  if (!entry || entry.status !== 'available') return { status: entry?.status || 'missing', aspectRatio: 1, measuredBy: 'unavailable-placeholder' };
  if (entry.ext === '.svg') { const measured = measureSvg(await fs.readFile(entry.resolvedPath)); if (measured) return { status: 'available', ...measured }; }
  const raster = measureRaster(await fs.readFile(entry.resolvedPath), entry.ext); if (raster) return { status: 'available', ...raster, aspectRatio: raster.width / raster.height };
  return { status: 'available', aspectRatio: 1.5, measuredBy: 'unknown-ratio-diagnostic' };
}

function compositionItem(item, resource, font, width, template) {
  const media = resource; const mediaRatio = Math.max(.25, Math.min(4, media.aspectRatio || 1)); const mediaHeight = Math.min(width * .55, width / mediaRatio * .42);
  const titleLines = wrap(item.title || `Registro ${item.id}`, font, 14, width); const descriptionLines = wrap(item.description || 'Sin descripción editorial.', font, 10, width);
  const creditLines = wrap(`Créditos: ${item.credits || 'No especificados'}`, font, 9, width); const sourceLines = wrap(`Fuente: ${item.source?.sourceId || item.source?.id || 'No indicada'} · ID: ${item.id}`, font, 8, width);
  const textHeight = titleLines.length * 19 + descriptionLines.length * 15 + creditLines.length * 13 + sourceLines.length * 12 + 18; const totalHeight = mediaHeight + textHeight;
  return { id: item.id, sourceId: item.source?.sourceId || item.source?.id, position: item.position, title: item.title, credits: item.credits, mediaType: item.mediaType, template, measurements: { width, mediaHeight, textHeight, totalHeight, mediaRatio, resourceStatus: media.status, measuredBy: media.measuredBy } };
}

function precedenceDiagnostics(orderIds, pairs) { const pos = new Map(orderIds.map((id, i) => [id, i])); return pairs.filter(pair => pos.has(pair.before) && pos.has(pair.after) && pos.get(pair.before) > pos.get(pair.after)).map(pair => ({ code: 'DECLARED_PRECEDENCE_VIOLATION', message: `${pair.before} debe preceder a ${pair.after}.`, ...pair })); }

export async function verifyComposition(sourceOrComposition, maybeComposition = null, options = {}) {
  const errors = []; const composition = maybeComposition || sourceOrComposition; const source = maybeComposition ? normalizeProject(sourceOrComposition) : null; const expectedPlan = source ? exportPlan(source, options.profile || composition.profile) : null; const selected = expectedPlan ? expectedPlan.items.map(item => item.id) : (composition.selectedIds || []); const sourceItems = expectedPlan ? new Map(expectedPlan.items.map(item => [item.id, item])) : new Map(); const assignments = (composition.pages || []).flatMap(page => page.items.map(item => ({ ...item, page }))); const assignedIds = assignments.map(item => item.id);
  if (assignedIds.length !== selected.length || new Set(assignedIds).size !== assignedIds.length || selected.some(id => !assignedIds.includes(id))) errors.push({ code: 'COMPOSITION_COVERAGE', message: 'La composición no cubre exactamente la selección.' });
  const expected = selected.join('|'); const actual = assignments.map(item => item.id).join('|'); if (expected !== actual) errors.push({ code: 'COMPOSITION_ORDER', message: 'La composición altera el orden autoral.' }); const physicalPosition = new Map(assignments.map((item, index) => [item.id, index]));
  const limits = options.constraints || (source ? { pageWidth: 595, pageHeight: 842, margin: 48, maxPages: 24 } : composition.constraints || {}); const usableHeight = Number(limits.pageHeight || 842) - Number(limits.margin || 48) * 2 - 42; const usableWidth = Number(limits.pageWidth || 595) - Number(limits.margin || 48) * 2; if ((composition.pages || []).length > Number(limits.maxPages ?? Infinity)) errors.push({ code: 'MAX_PAGES', message: 'La composición excede el máximo de páginas de la instancia.' }); const verifierDoc = await PDFDocument.create(); const verifierFont = (await embedFont(verifierDoc)).font;
  for (const page of composition.pages || []) { if (!COMPOSITION_TEMPLATES[page.template]) errors.push({ code: 'UNKNOWN_TEMPLATE', message: `Plantilla desconocida: ${page.template}.` }); if (limits.allowedTemplates && !limits.allowedTemplates.includes(page.template)) errors.push({ code: 'TEMPLATE_NOT_ALLOWED', page: page.page, message: `La plantilla ${page.template} no está permitida por la instancia.` }); if (page.items.length > (COMPOSITION_TEMPLATES[page.template]?.maxItems || 0)) errors.push({ code: 'TEMPLATE_CAPACITY', message: `La plantilla ${page.template} excede su capacidad.` }); const measuredHeight = page.template === 'split' ? Math.max(...page.items.map(item => Number(item.measurements?.totalHeight) || 0), 0) : page.items.reduce((sum, item) => sum + (Number(item.measurements?.totalHeight) || 0), 0) + Math.max(0, page.items.length - 1) * (page.template === 'stack' ? 18 : 0); if (Math.abs(Number(page.usedHeight) - measuredHeight) > .1 || page.usedHeight > usableHeight + .01) errors.push({ code: 'PAGE_HEIGHT', message: `La página ${page.page} no coincide con sus alturas medidas.` }); for (const item of page.items) { const box = item.box || {}; if (![box.x, box.y, box.width, box.height, item.measurements?.totalHeight].every(Number.isFinite)) errors.push({ code: 'NON_FINITE_GEOMETRY', itemId: item.id, message: `La geometría de ${item.id} contiene números no finitos.` }); if (box.x < limits.margin - .01 || box.y < limits.margin - .01 || box.x + box.width > Number(limits.pageWidth || 595) - limits.margin + .01 || box.y + box.height > Number(limits.pageHeight || 842) - limits.margin + .01) errors.push({ code: 'BOX_OUT_OF_BOUNDS', itemId: item.id, message: `La geometría de ${item.id} sale del área imprimible.` }); if (item.measurements?.totalHeight <= 0) errors.push({ code: 'UNMEASURED_ITEM', itemId: item.id, message: `La pieza ${item.id} no tiene altura medida.` }); if (item.measurements?.width > usableWidth + .01) errors.push({ code: 'WIDTH_OVERFLOW', itemId: item.id, message: `La pieza ${item.id} excede el ancho disponible.` }); const original = sourceItems.get(item.id); const expectedWidth = page.template === 'split' ? (usableWidth - 18) / 2 : usableWidth; if (Number.isFinite(item.measurements?.width) && Math.abs(item.measurements.width - expectedWidth) > .2) errors.push({ code: 'WIDTH_MISMATCH', itemId: item.id, message: `El ancho de ${item.id} no coincide con la plantilla.` }); if (original && item.sourceId !== original.sourceId) errors.push({ code: 'SOURCE_ID_MISMATCH', itemId: item.id, message: `La asignación ${item.id} cambió su sourceId.` }); if (original) { const textWidth = expectedWidth; const expectedTextHeight = wrap(original.title || `Registro ${original.id}`, verifierFont, 14, textWidth).length * 19 + wrap(original.description || 'Sin descripción editorial.', verifierFont, 10, textWidth).length * 15 + wrap(`Créditos: ${original.credits || 'No especificados'}`, verifierFont, 9, textWidth).length * 13 + wrap(`Fuente: ${original.sourceId || original.id || 'No indicada'} · ID: ${original.id}`, verifierFont, 8, textWidth).length * 12 + 18; if (Math.abs(Number(item.measurements.textHeight) - expectedTextHeight) > .2) errors.push({ code: 'TEXT_MEASUREMENT_MISMATCH', itemId: item.id, message: `La altura de texto de ${item.id} no coincide con la instancia original.` }); const resource = options.resourceEntries?.[item.id]; if (resource?.status === 'available') { const media = await measureResource(resource); const expectedMediaHeight = Math.min(textWidth * .55, textWidth / Math.max(.25, Math.min(4, media.aspectRatio || 1)) * .42); if (Math.abs(Number(item.measurements.mediaHeight) - expectedMediaHeight) > .2) errors.push({ code: 'MEDIA_MEASUREMENT_MISMATCH', itemId: item.id, message: `La altura de medio de ${item.id} no coincide con el recurso medido.` }); } } }
    for (let i = 0; i < page.items.length; i++) for (let j = i + 1; j < page.items.length; j++) { const a = page.items[i].box, b = page.items[j].box; const overlap = Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x); const vertical = Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y); if (overlap > .01 && vertical > .01) errors.push({ code: 'BOX_OVERLAP', page: page.page, message: `Las cajas ${page.items[i].id} y ${page.items[j].id} se superponen.` }); }
  }
  for (const pair of (limits.declaredPrecedence || [])) { const before = physicalPosition.get(pair.before); const after = physicalPosition.get(pair.after); if (before != null && after != null && before > after) errors.push({ code: 'DECLARED_PRECEDENCE_VIOLATION', ...pair, message: `${pair.before} debe preceder a ${pair.after}.` }); }
  return { ok: errors.length === 0, errors, checked: { selected: selected.length, assignments: assignedIds.length, pages: composition.pages?.length || 0 }, instanceBound: Boolean(source) };
}

export async function composeEdition(project, options = {}) {
  const composeStart = performance.now(); const check = validateProject(project); if (!check.ok) throw new Error(check.errors.join('; ')); const normalized = normalizeProject(project); const profile = profileOf(options.profile || 'portfolio'); const base = exportPlan(normalized, profile);
  const selected = base.items; const limits = { pageWidth: 595, pageHeight: 842, margin: 48, maxPages: options.maxPages ?? profile.maxPages ?? 24, requireResources: Boolean(options.requireResources), preserveOrder: options.preserveOrder !== false, allowedTemplates: options.allowedTemplates || ['single', 'split', 'stack'] };
  const mandatory = { ...limits, selectedIds: selected.map(x => x.id), orderIds: selected.map(x => x.id), completeSelection: true, declaredPrecedence: declaredPrecedence(normalized) }; const preferences = { minimizePages: true, minimizeUnusedArea: true, preserveTemplateStability: true, ...clone(options.preferences || {}) };
  const diagnostics = [...precedenceDiagnostics(selected.map(x => x.id), mandatory.declaredPrecedence)]; const resources = await resolveResources(normalized, { ...options, profile: profile.id }); const doc = await PDFDocument.create(); const embedded = await embedFont(doc); const font = embedded.font; const contentWidth = limits.pageWidth - limits.margin * 2;
  const measured = {}; for (const item of selected) { measured[item.id] = await measureResource(resources[item.id]); if (limits.requireResources && measured[item.id].status !== 'available') diagnostics.push({ code: 'MISSING_RESOURCE', itemId: item.id, message: `Medio no disponible para ${item.id}.` }); }
  const availableTemplates = limits.allowedTemplates.filter(t => COMPOSITION_TEMPLATES[t]); const deadline = options.timeLimitMs == null ? Infinity : performance.now() + Math.max(0, options.timeLimitMs); let interrupted = false; let statesExplored = 0; let transitionsExplored = 0; let peakStates = 0; const candidates = [];
  const itemLayoutCache = new Map(); const layoutOf = (item, width, template) => { const key = `${item.id}|${width}|${template}`; if (!itemLayoutCache.has(key)) itemLayoutCache.set(key, compositionItem(item, measured[item.id], font, width, template)); return itemLayoutCache.get(key); };
  const candidatePage = (start, count, template, pageNumber) => { const colWidth = template === 'split' ? (contentWidth - 18) / 2 : contentWidth; const gap = template === 'stack' ? 18 : template === 'split' ? 18 : 0; const assignments = selected.slice(start, start + count).map((item, index) => { const a = layoutOf(item, colWidth, template); const x = template === 'split' ? limits.margin + index * (colWidth + gap) : limits.margin; const usedBefore = template === 'split' ? 0 : selected.slice(start, start + index).reduce((sum, prior) => sum + layoutOf(prior, colWidth, template).measurements.totalHeight + gap, 0); const y = limits.pageHeight - limits.margin - 42 - usedBefore; return { ...a, page: pageNumber, slot: index, box: { x, y: y - a.measurements.totalHeight, width: colWidth, height: a.measurements.totalHeight } }; }); const usedHeight = template === 'split' ? Math.max(...assignments.map(a => a.measurements.totalHeight), 0) : assignments.reduce((sum, a) => sum + a.measurements.totalHeight, 0) + Math.max(0, count - 1) * gap; return usedHeight <= limits.pageHeight - limits.margin * 2 - 42 ? { page: pageNumber, template, items: assignments, usedHeight, unusedHeight: limits.pageHeight - limits.margin * 2 - 42 - usedHeight } : null; };
  const baselineStart = performance.now(); const baselinePages = []; for (const item of selected) { const page = candidatePage(selected.indexOf(item), 1, 'single', baselinePages.length + 1); if (!page) break; baselinePages.push(page); } const baseline = { algorithm: 'greedy-single', status: baselinePages.length === selected.length && baselinePages.length <= limits.maxPages ? 'FEASIBLE' : 'INFEASIBLE', pages: baselinePages.length, elapsedMs: Number((performance.now() - baselineStart).toFixed(3)) };
  const routeLimit = Math.max(3, (options.alternativeCount || 3) * 2); const states = new Map(); const keyOf = (index, previousTemplate, pages) => `${index}|${previousTemplate || '-'}|${pages}`; const routeScore = route => [route.pages.length, route.pages.reduce((s, p) => s + p.unusedHeight, 0), route.pages.filter((p, i) => i && p.template !== route.pages[i - 1].template).length]; const compareScores = (a, b) => { for (let i = 0; i < a.length; i++) { const delta = Number(a[i]) - Number(b[i]); if (Math.abs(delta) > (i === 0 || i === 2 ? 0 : 1e-6)) return delta; } return 0; }; const addRoute = (key, route) => { const list = states.get(key) || []; list.push(route); list.sort((a, b) => compareScores(routeScore(a), routeScore(b)) || a.signature.localeCompare(b.signature)); states.set(key, list.slice(0, routeLimit)); peakStates = Math.max(peakStates, states.size); };
  if (options.timeLimitMs === 0) interrupted = true; else { addRoute(keyOf(0, null, 0), { pages: [], signature: '' }); for (let index = 0; index <= selected.length && !interrupted; index++) { for (const [key, routes] of [...states.entries()]) { const [stateIndex, previousTemplate, pageCount] = key.split('|'); if (Number(stateIndex) !== index || Number(pageCount) >= limits.maxPages || index === selected.length) continue; statesExplored++; if (performance.now() > deadline) { interrupted = true; break; } for (const route of routes) for (const template of availableTemplates) { const max = Math.min(COMPOSITION_TEMPLATES[template].maxItems, selected.length - index); for (let count = max; count >= 1; count--) { transitionsExplored++; const page = candidatePage(index, count, template, Number(pageCount) + 1); if (!page) continue; const pages = [...route.pages, page]; addRoute(keyOf(index + count, template, Number(pageCount) + 1), { pages, signature: pages.map(p => `${p.template}:${p.items.map(x => x.id).join(',')}`).join('|') }); } } } } for (const [key, routes] of states) if (Number(key.split('|')[0]) === selected.length) for (const route of routes) candidates.push({ pages: route.pages, score: routeScore(route), signature: route.signature }); }
  let referenceComparison = null; if (options.referenceEnumerate && selected.length <= 10) { const reference = []; let referenceTransitions = 0; const visit = (index, pages) => { if (index === selected.length) { reference.push({ pages, score: routeScore({ pages }), signature: pages.map(p => `${p.template}:${p.items.map(x => x.id).join(',')}`).join('|') }); return; } if (pages.length >= limits.maxPages) return; for (const template of availableTemplates) { const max = Math.min(COMPOSITION_TEMPLATES[template].maxItems, selected.length - index); for (let count = max; count >= 1; count--) { referenceTransitions++; const page = candidatePage(index, count, template, pages.length + 1); if (page) visit(index + count, [...pages, page]); } } }; visit(0, []); reference.sort((a, b) => compareScores(a.score, b.score) || a.signature.localeCompare(b.signature)); referenceComparison = { algorithm: 'reference-exhaustive-enumeration', candidates: reference.length, transitions: referenceTransitions, bestObjective: reference[0]?.score || null, agreesOnBest: null }; }
  candidates.sort((a, b) => compareScores(a.score, b.score) || a.signature.localeCompare(b.signature)); const unique = []; const signatures = new Set(); for (const c of candidates) if (!signatures.has(c.signature)) { signatures.add(c.signature); unique.push(c); if (unique.length >= (options.alternativeCount || 3)) break; } if (referenceComparison) referenceComparison.agreesOnBest = !referenceComparison.bestObjective || !unique[0] || compareScores(referenceComparison.bestObjective, unique[0].score) === 0;
  let status = interrupted ? (unique.length ? 'FEASIBLE' : 'UNKNOWN') : unique.length ? 'OPTIMAL' : 'INFEASIBLE'; if (diagnostics.some(d => d.code === 'DECLARED_PRECEDENCE_VIOLATION' || d.code === 'MISSING_RESOURCE')) status = 'INFEASIBLE';
  const provisional = { schema: 'iris.composition-plan/1', status, solver: 'deterministic-dynamic-programming', rationale: 'Con orden fijo, cada transición consume un bloque consecutivo. El estado suficiente es (posición, plantilla anterior, páginas usadas); se conservan las mejores k rutas por estado con objetivo lexicográfico explícito.', profile: profile.id, editionId: normalized.editionId, originId: normalized.origin?.originId, constraints: mandatory, preferences, diagnostics, selectedIds: selected.map(x => x.id), relations: clone(normalized.relations || []), alternatives: unique.map(c => ({ pages: c.pages, objective: { pages: c.score[0], unusedHeight: c.score[1], templateChanges: c.score[2] } })), pages: unique[0]?.pages || [], objective: unique[0] ? { pages: unique[0].score[0], unusedHeight: unique[0].score[1], templateChanges: unique[0].score[2] } : null, baseline, metrics: { statesExplored, transitionsExplored, peakStates, elapsedMs: Number((performance.now() - composeStart).toFixed(3)) }, referenceComparison, resources: Object.fromEntries(Object.entries(resources).map(([id, r]) => [id, { status: r.status, sha256: r.sha256, bytes: r.bytes, ext: r.ext }])) };
  const verification = unique[0] ? await verifyComposition(normalized, provisional, { profile: profile.id, constraints: limits, resourceEntries: resources }) : { ok: true, complete: false, errors: [], checked: { selected: selected.length, assignments: 0, pages: 0 }, instanceBound: true, note: 'No hay candidato que verificar.' }; if (!verification.ok && provisional.status !== 'UNKNOWN') { provisional.status = 'INVALID_PLAN'; provisional.diagnostics.push(...verification.errors); } provisional.verification = verification; return provisional;
}

function wrap(textValue, font, size, maxWidth) {
  const words = text(textValue).split(/\s+/); const lines = []; let line = '';
  for (const word of words) { const candidate = line ? `${line} ${word}` : word; if (line && font.widthOfTextAtSize(candidate, size) > maxWidth) { lines.push(line); line = word; } else line = candidate; }
  if (line) lines.push(line); return lines.length ? lines : [''];
}

async function embedFont(doc) {
  const configured = process.env.IRIS_FONT_PATH;
  if (configured) { doc.registerFontkit(fontkit); try { const bytes = await fs.readFile(path.resolve(configured)); return { font: await doc.embedFont(bytes, { subset: true }), coverage: fontkit.create(bytes), label: configured }; } catch (error) { throw new Error(`PDF_FONT_CONFIG_ERROR: ${error.message}`); } }
  return { font: await doc.embedFont(StandardFonts.Helvetica), coverage: null, label: 'Helvetica/WinAnsi' };
}

function svgColor(value, fallback = rgb(.5,.5,.5)) { const match = text(value).trim().match(/^#([0-9a-f]{6})$/i); return match ? rgb(parseInt(match[1].slice(0,2),16)/255, parseInt(match[1].slice(2,4),16)/255, parseInt(match[1].slice(4,6),16)/255) : fallback; }
function pathForPdf(d, height) { const tokens = d.match(/[MLCQZ]|-?\d*\.?\d+(?:e[-+]?\d+)?/gi) || []; let command = '', index = 0; const out = []; const arity = { M: 2, L: 2, C: 6, Q: 4, Z: 0 }; while (index < tokens.length) { if (/^[MLCQZ]$/i.test(tokens[index])) command = tokens[index++].toUpperCase(); if (!command) break; out.push(command); const count = arity[command]; if (!count) continue; const values = tokens.slice(index, index + count).map(Number); if (values.length !== count) break; for (let i = 0; i < values.length; i += 2) { out.push(String(values[i]), String(height - values[i + 1])); } index += count; } return out.join(' '); }
async function renderSvgMedia(page, filePath, box, font) { try { const source = await fs.readFile(filePath, 'utf8'); const view = source.match(/viewBox=["']\s*[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+([\d.]+)\s*["']/i); const width = Number(view?.[1] || source.match(/\bwidth=["']([\d.]+)/i)?.[1]); const height = Number(view?.[2] || source.match(/\bheight=["']([\d.]+)/i)?.[1]); if (!(width > 0 && height > 0)) return false; const scale = Math.min(box.width / width, box.height / height); const ox = box.x + (box.width - width * scale) / 2; const oy = box.y + (box.height - height * scale) / 2; const rect = source.match(/<rect\b([^>]*)>/i)?.[1] || ''; const attr = (s, name) => s.match(new RegExp(`\\b${name}=["']([^"']+)`, 'i'))?.[1]; page.drawRectangle({ x: ox, y: oy, width: width * scale, height: height * scale, color: svgColor(attr(rect, 'fill'), rgb(.94,.94,.91)) }); for (const match of source.matchAll(/<circle\b([^>]*)>/gi)) { const a = match[1]; const cx = Number(attr(a, 'cx') || 0), cy = Number(attr(a, 'cy') || 0), r = Number(attr(a, 'r') || 0); const stroke = svgColor(attr(a, 'stroke')); const sw = Number(attr(a, 'stroke-width') || 1) * scale; page.drawEllipse({ x: ox + (cx-r) * scale, y: oy + (height-cy-r) * scale, xScale: r * scale, yScale: r * scale, borderColor: stroke, borderWidth: sw }); } for (const match of source.matchAll(/<path\b([^>]*)\bd=["']([^"']+)["'][^>]*>/gi)) { const a = match[1], d = match[2], converted = pathForPdf(d, height); if (converted) page.drawSvgPath(converted, { x: ox, y: oy, scale, borderColor: svgColor(attr(a, 'stroke')), borderWidth: Number(attr(a, 'stroke-width') || 1) * scale }); } for (const match of source.matchAll(/<text\b([^>]*)>([\s\S]*?)<\/text>/gi)) { const a = match[1], value = match[2].replace(/<[^>]+>/g, ''); const x = Number(attr(a, 'x') || 0), baseline = Number(attr(a, 'y') || 0), size = Number(attr(a, 'font-size') || 12) * scale; page.drawText(value, { x: ox + x * scale, y: oy + (height-baseline) * scale, size: Math.max(4, size), font, color: svgColor(attr(a, 'fill'), rgb(.1,.1,.1)) }); } return true; } catch { return false; } }

export async function buildPdf(project, profile = 'portfolio', options = {}) {
  if (options.composition) return buildComposedPdf(project, profile, options.composition, options.resources || {});
  const plan = exportPlan(project, profile); if (plan.diagnostics.length) throw new Error(`PROFILE_LIMIT_EXCEEDED: ${plan.diagnostics.map(x => x.message).join('; ')}`); const doc = await PDFDocument.create(); const embedded = await embedFont(doc); const font = embedded.font; const bold = font;
  const strings = [plan.title, plan.subtitle, plan.curatorialQuestion, plan.ordering.reason, ...plan.items.flatMap(x => [x.title, x.description, x.credits, x.source?.sourceId, x.id])];
  let unsupported = [...new Set([...strings.join('\n')].filter(ch => !/\s/.test(ch)).filter(ch => { const cp = ch.codePointAt(0); try { return embedded.coverage ? embedded.coverage.glyphForCodePoint(cp).id === 0 : false; } catch { return true; } }))];
  if (!embedded.coverage) { try { for (const value of strings) embedded.font.encodeText(text(value)); } catch (error) { throw new Error(`PDF_UNSUPPORTED_CHARACTERS: ${error.message}`); } }
  if (unsupported.length) throw new Error(`PDF_UNSUPPORTED_CHARACTERS: ${unsupported.slice(0,12).map(ch => `${ch}(U+${ch.codePointAt(0).toString(16)})`).join(' ')}`);
  doc.setTitle(plan.title); doc.setSubject('IRIS export plan');
  const W = 595, H = 842, margin = 48, max = W - margin * 2; let page, y, pageNo = 0;
  const newPage = () => { page = doc.addPage([W, H]); pageNo += 1; y = H - margin; page.drawText(`IRIS · ${plan.title}`, { x: margin, y, size: 18, font: bold, color: rgb(.1,.13,.12) }); y -= 28; };
  const put = (value, size = 10, f = font, color = rgb(.15,.18,.16), gap = 14) => { for (const line of wrap(value, f, size, max)) { if (y < margin + 30) { page.drawText(`Página ${pageNo}`, { x: margin, y: 20, size: 8, font, color: rgb(.4,.4,.4) }); newPage(); } page.drawText(line, { x: margin, y, size, font: f, color }); y -= gap; } };
  newPage(); put(plan.subtitle || 'Archivo a portafolios exportables', 11, font, rgb(.25,.3,.27), 17); put(`Orden: ${plan.ordering.dimension}. ${plan.ordering.reason}`, 9, font, rgb(.35,.38,.35), 16); y -= 8;
  if (!plan.items.length) put('No hay piezas seleccionadas.', 11); 
  for (const item of plan.items) { if (y < 155) { page.drawText(`Página ${pageNo}`, { x: margin, y: 20, size: 8, font }); newPage(); } put(`${String(item.position).padStart(2, '0')}  ${item.title || `Registro ${item.id}`}`, 14, bold, rgb(.16,.24,.19), 19); put(item.description || 'Sin descripción editorial.', 10, font, rgb(.2,.22,.2), 15); put(`Créditos: ${item.credits || 'No especificados'}`, 9, font, rgb(.35,.38,.35), 13); put(`Fuente: ${item.source.label || item.source.sourceId || item.source.id || 'No indicada'} · ID: ${item.id}`, 8, font, rgb(.35,.38,.35), 12); y -= 10; }
  page.drawText(`Página ${pageNo}`, { x: margin, y: 20, size: 8, font, color: rgb(.4,.4,.4) }); const profileSpec = profileOf(profile); if (profileSpec.maxPages != null && pageNo > profileSpec.maxPages) throw new Error(`PROFILE_LIMIT_EXCEEDED: ${profileSpec.label} supera ${profileSpec.maxPages} páginas.`); return Buffer.from(await doc.save());
}

async function buildComposedPdf(project, profile, composition, resourceEntries = {}) {
  const plan = exportPlan(project, profile); const doc = await PDFDocument.create(); const embedded = await embedFont(doc); const font = embedded.font; const bold = font; const W = composition.constraints.pageWidth; const H = composition.constraints.pageHeight; const margin = composition.constraints.margin;
  const strings = [plan.title, plan.subtitle, ...plan.items.flatMap(x => [x.title, x.description, x.credits, x.source?.sourceId, x.id])]; try { for (const value of strings) embedded.font.encodeText(text(value)); } catch (error) { throw new Error(`PDF_UNSUPPORTED_CHARACTERS: ${error.message}`); }
  doc.setTitle(plan.title); doc.setSubject(`IRIS composition ${composition.status}`);
  if (!composition.pages.length) { const page = doc.addPage([W, H]); page.drawText(`IRIS · ${plan.title}`, { x: margin, y: H - margin, size: 16, font: bold }); page.drawText('No hay piezas seleccionadas.', { x: margin, y: H - margin - 42, size: 11, font }); page.drawText(`IRIS · ${composition.status}`, { x: margin, y: 20, size: 7, font, color: rgb(.4,.4,.4) }); }
  for (const composedPage of composition.pages) { const page = doc.addPage([W, H]); page.drawText(`IRIS · ${plan.title}`, { x: margin, y: H - margin, size: 16, font: bold, color: rgb(.1,.13,.12) }); page.drawText(`Página ${composedPage.page} · ${composedPage.template}`, { x: margin, y: H - margin - 22, size: 8, font, color: rgb(.4,.4,.4) });
    for (const assignment of composedPage.items) { const item = plan.items.find(x => x.id === assignment.id); const box = assignment.box; const textX = box.x; let y = box.y + box.height - 14; const mediaBox = { x: box.x, y: box.y + box.height - assignment.measurements.mediaHeight, width: box.width, height: assignment.measurements.mediaHeight }; let image = null; const resource = resourceEntries[assignment.id]; let svgRendered = false; if (resource?.status === 'available' && ['.png','.jpg','.jpeg'].includes(resource.ext)) { try { const bytes = await fs.readFile(resource.resolvedPath); image = resource.ext === '.png' ? await doc.embedPng(bytes) : await doc.embedJpg(bytes); } catch {} } if (resource?.status === 'available' && resource.ext === '.svg') svgRendered = await renderSvgMedia(page, resource.resolvedPath, mediaBox, font); if (image) { const scale = Math.min(mediaBox.width / image.width, mediaBox.height / image.height); page.drawImage(image, { x: mediaBox.x + (mediaBox.width - image.width * scale) / 2, y: mediaBox.y + (mediaBox.height - image.height * scale) / 2, width: image.width * scale, height: image.height * scale }); } else if (!svgRendered) { page.drawRectangle({ ...mediaBox, borderWidth: 1, borderColor: rgb(.78,.8,.76), color: rgb(.96,.96,.93) }); page.drawText(`MEDIO · ${assignment.measurements.resourceStatus}${resource?.ext === '.svg' ? ' · SVG referencia' : ''}`, { x: textX + 6, y: mediaBox.y + mediaBox.height - 16, size: 7, font, color: rgb(.45,.48,.44) }); } y = mediaBox.y - 18;
      const put = (value, size, gap, color = rgb(.18,.2,.18), f = font) => { for (const line of wrap(value, f, size, box.width)) { page.drawText(line, { x: textX, y, size, font: f, color }); y -= gap; } };
      put(`${String(item.position).padStart(2, '0')}  ${item.title || `Registro ${item.id}`}`, 12, 16, rgb(.16,.24,.19), bold); put(item.description || 'Sin descripción editorial.', 9, 13); put(`Créditos: ${item.credits || 'No especificados'}`, 8, 11, rgb(.35,.38,.35)); put(`Fuente: ${item.source?.sourceId || item.source?.id || 'No indicada'} · ID: ${item.id}`, 7, 10, rgb(.35,.38,.35));
    } page.drawText(`IRIS · ${composition.status} · selección completa`, { x: margin, y: 20, size: 7, font, color: rgb(.4,.4,.4) }); }
  return Buffer.from(await doc.save());
}

export function buildWeb(project, profile = 'portfolio', resources = {}, composition = null) {
  const plan = exportPlan(project, profile); const items = plan.items; const pageById = composition ? Object.fromEntries(composition.pages.flatMap(p => p.items.map(a => [a.id, p.page]))) : {};
  return `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${htmlEsc(plan.title)}</title><style>body{margin:0;background:#101315;color:#eef0e8;font:16px system-ui;line-height:1.5}main{max-width:960px;margin:auto;padding:64px 24px}header{border-bottom:1px solid #48504a;padding-bottom:32px;margin-bottom:40px}.eyebrow{color:#d9b26f;text-transform:uppercase;letter-spacing:.18em;font-size:12px}.lead{color:#b8c1b7;font-size:20px;max-width:680px}.work{border-top:1px solid #48504a;padding:26px 0;display:grid;grid-template-columns:72px 1fr;gap:20px}.work img{max-width:100%;max-height:260px;object-fit:contain;display:block;margin:12px 0}.num{color:#d9b26f;font-variant-numeric:tabular-nums}.meta{color:#a6b0a5;font-size:13px}.tag{display:inline-block;border:1px solid #526458;border-radius:99px;padding:2px 8px;margin:3px 4px 0 0;font-size:12px}@media(max-width:600px){main{padding:32px 18px}.work{grid-template-columns:1fr}}</style></head><body><main><header><div class="eyebrow">IRIS · dossier portable</div><h1>${htmlEsc(plan.title||'Portafolio')}</h1><p class="lead">${htmlEsc(plan.subtitle||'')}</p><p class="meta">${items.length} piezas · selección editorial · orden ${htmlEsc(plan.ordering.dimension)}${composition ? ` · composición ${htmlEsc(composition.status)} · ${composition.pages.length} páginas` : ''}</p></header>${items.map(x=>{const r=resources[x.id]; const media=r?.status==='included' ? (x.mediaType==='video' ? `<p><a class="meta" href="${htmlEsc(r.path)}">Abrir video / referencia de medio</a></p>` : `<img src="${htmlEsc(r.path)}" alt="Medio de ${htmlEsc(x.title||x.id)}">`) : ''; return `<article class="work"><div class="num">${String(x.position).padStart(2,'0')}<br><small>P${pageById[x.id]||'—'}</small></div><div>${media}<h2>${htmlEsc(x.title||`Registro ${x.id}`)}</h2><p>${htmlEsc(x.description||'Sin descripción editorial.')}</p><p class="meta">${htmlEsc(x.credits||'Créditos no especificados')} · ${htmlEsc(x.source?.sourceId||x.source?.id||'Fuente no indicada')} · ${htmlEsc(x.mediaType||'registro')} · ${htmlEsc(x.id)}</p><div>${(x.tags||[]).map(t=>`<span class="tag">${htmlEsc(t)}</span>`).join('')}</div></div></article>`;}).join('')}</main></body></html>`;
}

export function buildFicha(project, profile = 'portfolio', composition = null) {
  const plan = exportPlan(project, profile); const fields=[['Título',plan.title],['Bajada',plan.subtitle],['Pregunta curatorial',plan.curatorialQuestion],['Edición',plan.editionId],['Perfil',plan.profile],['Piezas seleccionadas',plan.items.length],['Composición',composition ? `${composition.status}; ${composition.pages.length} páginas; ${composition.alternatives.length} alternativas` : 'No calculada'],['Orden',`${plan.ordering.dimension}: ${plan.ordering.reason}`],['Cobertura','La ficha resume la selección; el plan JSON conserva IDs, fuentes, medios y textos completos.']];
  return `<!doctype html><html lang="es"><meta charset="utf-8"><title>Ficha · ${htmlEsc(plan.title)}</title><style>body{font:15px system-ui;max-width:780px;margin:60px auto;padding:0 24px;color:#202620}h1{font-size:38px;margin-bottom:40px}dl{display:grid;grid-template-columns:190px 1fr;border-top:1px solid #bbb}dt,dd{margin:0;padding:14px 0;border-bottom:1px solid #ddd}dt{font-weight:700;color:#596559}dd{white-space:pre-wrap}.note{margin-top:40px;padding:18px;background:#f2efe7}</style><h1>${htmlEsc(plan.title||'Ficha de proyecto')}</h1><dl>${fields.map(([k,v])=>`<dt>${htmlEsc(k)}</dt><dd>${htmlEsc(v??'')}</dd>`).join('')}</dl><div class="note"><strong>Nota de procedencia.</strong> Esta ficha y el HTML se derivan del mismo plan de exportación que el PDF. Las relaciones exploratorias no se convierten en atribuciones.</div></html>`;
}

export function publicPlan(project, profile = 'portfolio', resources = {}, composition = null) {
  const plan = exportPlan(project, profile); return { schema: 'iris.public-plan/1', profile: plan.profile, editionId: plan.editionId, originId: plan.originId, title: plan.title, subtitle: plan.subtitle, curatorialQuestion: plan.curatorialQuestion, ordering: clone(plan.ordering), diagnostics: clone(plan.diagnostics), composition: composition ? { schema: composition.schema, status: composition.status, solver: composition.solver, constraints: clone(composition.constraints), preferences: clone(composition.preferences), diagnostics: clone(composition.diagnostics), selectedIds: clone(composition.selectedIds), relations: (composition.relations || []).map(r => ({ id: r.id, sourceId: r.sourceId, targetId: r.targetId, type: r.type, weight: r.weight, scope: r.scope })), alternatives: clone(composition.alternatives), objective: clone(composition.objective), metrics: clone(composition.metrics), verification: clone(composition.verification), pages: clone(composition.pages) } : null, items: plan.items.map(item => ({ position: item.position, id: item.id, sourceId: item.sourceId, title: item.title, description: item.description, credits: item.credits, mediaType: item.mediaType, tags: clone(item.tags), source: { id: item.source.id, sourceId: item.source.sourceId, kind: item.source.kind, date: item.source.date, assetAvailable: item.source.assetAvailable }, resource: resources[item.id] || null })) };
}

function insideRoot(candidate, roots) { return roots.some(root => { const r = path.resolve(root); const c = path.resolve(candidate); return c === r || c.startsWith(`${r}${path.sep}`); }); }

export async function resolveResources(project, options = {}) {
  const roots = (options.roots || []).map(root => path.resolve(root)); const resourceMap = options.resourceMap || {}; const plan = exportPlan(project, options.profile || 'portfolio'); const entries = {};
  for (const item of plan.items) {
    const requested = resourceMap[item.id] || item.source?.assetPath; if (!requested) { entries[item.id] = { status: 'missing', reason: 'no_asset_reference' }; continue; }
    const candidate = path.resolve(requested); const resolved = path.isAbsolute(requested) ? candidate : roots.map(root => path.resolve(root, requested)).find(file => insideRoot(file, roots)) || candidate;
    if (!roots.length || !insideRoot(resolved, roots)) { entries[item.id] = { status: 'blocked', reason: 'outside_authorized_roots' }; continue; }
    try { const stat = await fs.stat(resolved); if (!stat.isFile()) throw new Error('not_file'); const bytes = await fs.readFile(resolved); const digest = crypto.createHash('sha256').update(bytes).digest('hex'); const ext = path.extname(resolved).toLowerCase() || '.bin'; entries[item.id] = { status: 'available', sourceKind: item.mediaType, bytes: bytes.length, sha256: digest, ext, resolvedPath: resolved }; }
    catch { entries[item.id] = { status: 'missing', reason: 'file_not_found' }; }
  }
  return entries;
}

export async function writePortablePackage(project, packageDir, options = {}) {
  const profile = options.profile || 'portfolio'; const check = validateProject(project); if (!check.ok) throw new Error(check.errors.join('; ')); const normalized = normalizeProject(project); const resources = await resolveResources(normalized, { ...options, profile }); const missing = Object.entries(resources).filter(([, entry]) => entry.status !== 'available'); if (options.strictResources && missing.length) throw new Error(`RESOURCE_DIAGNOSTICS: ${missing.map(([id, entry]) => `${id}:${entry.reason}`).join(', ')}`); const composition = await composeEdition(normalized, { ...options, profile, requireResources: options.strictResources });
  const publicResources = {}; for (const [id, entry] of Object.entries(resources)) publicResources[id] = entry.status === 'available' ? { status: 'included', path: `media/${id.replace(/[^a-z0-9_-]+/gi,'-')}-${entry.sha256.slice(0,12)}${entry.ext}`, sha256: entry.sha256, bytes: entry.bytes } : { status: entry.status, reason: entry.reason };
  if (['INFEASIBLE', 'INVALID_PLAN', 'UNKNOWN'].includes(composition.status) || !composition.verification.ok && composition.status !== 'FEASIBLE') throw new Error(`COMPOSITION_${composition.status}: no se puede empaquetar una composición no materializable.`); const publicData = publicPlan(normalized, profile, publicResources, composition); const finalDir = path.resolve(packageDir); await fs.mkdir(path.dirname(finalDir), { recursive: true }); const stage = await fs.mkdtemp(path.join(path.dirname(finalDir), '.iris-package-')); try {
    await fs.mkdir(path.join(stage, 'media')); for (const [id, entry] of Object.entries(resources)) if (entry.status === 'available') await fs.copyFile(entry.resolvedPath, path.join(stage, publicResources[id].path));
    await fs.writeFile(path.join(stage, 'portfolio.pdf'), await buildPdf(normalized, profile, { composition, resources })); await fs.writeFile(path.join(stage, 'portfolio.html'), buildWeb(normalized, profile, publicResources, composition), 'utf8'); await fs.writeFile(path.join(stage, 'ficha.html'), buildFicha(normalized, profile, composition), 'utf8'); await fs.writeFile(path.join(stage, 'plan.json'), JSON.stringify(publicData, null, 2), 'utf8'); await fs.writeFile(path.join(stage, 'manifest.json'), JSON.stringify({ schema: 'iris.portable-manifest/1', complete: composition.status === 'OPTIMAL', editionId: normalized.editionId, originId: normalized.origin?.originId, profile, composition: { status: composition.status, solver: composition.solver, alternatives: composition.alternatives.length }, resources: publicResources, limitations: [...missing.map(([id, entry]) => ({ id, status: entry.status, reason: entry.reason })), ...(composition.status === 'FEASIBLE' ? [{ code: 'COMPOSITION_NOT_PROVEN_OPTIMAL', message: 'La composición es factible pero fue interrumpida antes de probar optimalidad.' }] : []), ...composition.diagnostics] }, null, 2), 'utf8'); await fs.rename(stage, finalDir); return { packageDir: finalDir, files: ['portfolio.pdf','portfolio.html','ficha.html','plan.json','manifest.json',...Object.values(publicResources).filter(x => x.status === 'included').map(x => x.path)], diagnostics: missing };
  } catch (error) { await fs.rm(stage, { recursive: true, force: true }).catch(() => {}); throw error; }
}

export async function writeExports(project, outputDir, options = {}) {
  const check = validateProject(project); if (!check.ok) throw new Error(check.errors.join('; ')); const normalized = normalizeProject(project); const profile = options.profile || 'portfolio'; const plan = exportPlan(normalized, profile); if (plan.diagnostics.length) throw new Error(`PROFILE_LIMIT_EXCEEDED: ${plan.diagnostics.map(x => x.message).join('; ')}`); const resources = await resolveResources(normalized, { ...options, profile }); let composition = options.compose === false ? null : await composeEdition(normalized, { ...options, profile }); if (options.compositionOverride) { const trusted = await composeEdition(normalized, { ...options, profile, timeLimitMs: undefined }); const verification = await verifyComposition(normalized, options.compositionOverride, { profile, constraints: trusted.constraints, resourceEntries: resources }); if (!verification.ok) throw new Error(`INVALID_COMPOSITION_OVERRIDE: ${verification.errors.map(x => x.message).join('; ')}`); composition = { ...options.compositionOverride, status: 'FEASIBLE', verification, selectedAlternative: options.selectedAlternative ?? null }; } if (composition?.status === 'INFEASIBLE' || composition?.status === 'INVALID_PLAN' || composition?.status === 'UNKNOWN') throw new Error(`COMPOSITION_${composition.status}: no se puede exportar una composición no materializable.`); await fs.mkdir(outputDir, { recursive: true });
  const slug = text(normalized.title || 'iris-portafolio').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'iris-portafolio';
  if (composition && ['INFEASIBLE', 'INVALID_PLAN', 'UNKNOWN'].includes(composition.status)) throw new Error(`COMPOSITION_${composition.status}: no se puede exportar una composición no materializable.`); const base = path.join(outputDir, slug); const pdf = await buildPdf(normalized, profile, { composition, resources });
  await fs.writeFile(`${base}.pdf`, pdf); await fs.writeFile(`${base}.json`, JSON.stringify({ ...normalized, exportPlan: plan, composition }, null, 2), 'utf8'); await fs.writeFile(`${base}.html`, buildWeb(normalized, profile, {}, composition), 'utf8'); await fs.writeFile(`${base}-ficha.html`, buildFicha(normalized, profile, composition), 'utf8');
  return { base, plan, composition, files: [`${base}.pdf`, `${base}.json`, `${base}.html`, `${base}-ficha.html`] };
}
