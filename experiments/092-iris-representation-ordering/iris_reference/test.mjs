import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import { PDFDocument } from 'pdf-lib';
import * as pdfjs from 'pdfjs-dist/legacy/build/pdf.mjs';
import { buildPdf, composeEdition, createEdition, exportPlan, importArchiveBundle, importInbox, orderBy, parseSourceDate, resolveConflict, validateProject, verifyComposition, writeExports, writePortablePackage } from './engine.mjs';

const demo=JSON.parse(await fs.readFile('demo-project.json','utf8'));
const sample=JSON.parse(await fs.readFile('fixtures/mak-inbox-sample.json','utf8'));
const imported=importInbox(sample);
assert.equal(imported.source.schema,'faro-portfolio-inbox-v1');
assert.equal(imported.items.length,4);
assert.equal(new Set(imported.items.map(x=>x.id)).size,4);
assert.equal(imported.items[0].source.raw.tipo_contenido,'story');
assert.equal(imported.items[0].source.assetPath,'/portfolio-media/stories/202607/17950615887015728.mp4');

const curated=JSON.parse(JSON.stringify(imported));
curated.title='Ñandú — edición larga';
curated.items[0].selected=true; curated.items[0].title='Registro de prueba'; curated.items[0].description='Texto largo '.repeat(500); curated.items[0].credits='Crédito con ñ y á';
curated.items[1].selected=true; curated.items[1].title='Segundo registro';
const plan=exportPlan(curated); assert.deepEqual(plan.items.map(x=>x.id),[imported.items[0].id,imported.items[1].id]);
assert.equal(plan.items[0].description.length,6000);
assert.deepEqual(exportPlan(curated),exportPlan(curated),'same input produces same plan');
assert.equal(orderBy(curated,'date').orderIds.at(-1),imported.items[0].id,'date ordering puts later date last');

const changedSource={...sample,items:sample.items.slice(0,3).map(x=>({...x,asset_available:false,extra_field:'preserved unknown',...(x.id===curated.items[0].id?{descripcion_original:'Fuente actualizada'}:{})}))};
const merged=importInbox(changedSource,curated);
assert.equal(merged.items.find(x=>x.id===imported.items[0].id).selected,true,'source update preserves selection');
assert.equal(merged.items.find(x=>x.id===imported.items[0].id).title,'Registro de prueba','source update preserves editorial title');
assert.equal(merged.items.find(x=>x.id===imported.items[0].id).source.assetAvailable,false);
assert.equal(merged.items.find(x=>x.id===imported.items[3].id).sourceState,'missing_from_latest_source','removed source item retained as missing');
assert.equal(merged.items.find(x=>x.id===imported.items[0].id).editorialConflict,'source_updated');

const duplicate=importInbox({schema:'faro-portfolio-inbox-v1',items:[{id:'x'},{id:'x'}]});
assert.match(duplicate.errors[0],/ID duplicado/);
const invalid=validateProject({...curated,relations:[{sourceId:curated.items[0].id,targetId:'missing'}]});
assert.equal(invalid.ok,false); assert.match(invalid.errors[0],/ausente/);
const duplicateProject=validateProject({...curated,items:[...curated.items,{...curated.items[0]}]});
assert.equal(duplicateProject.ok,false); assert.match(duplicateProject.errors.join(' '),/ID duplicado/);
const badOrder=validateProject({...curated,orderIds:['missing',curated.items[0].id,curated.items[0].id]});
assert.equal(badOrder.ok,false); assert.match(badOrder.errors.join(' '),/orderIds/);
const importedDuplicate=importInbox({schema:'faro-portfolio-inbox-v1',items:[{id:'x'},{id:'x'}]});
assert.equal(validateProject(importedDuplicate).ok,false,'import errors cannot be normalized away');

const pdf=await buildPdf(curated); assert.equal(pdf.subarray(0,5).toString('ascii'),'%PDF-');
const loaded=await PDFDocument.load(pdf); assert.ok(loaded.getPageCount()>=1,'parse PDF');
await fs.writeFile('work/regression-unicode-long.pdf',pdf);
await assert.rejects(() => buildPdf({...curated,title:'漢字 Ω'}),/PDF_UNSUPPORTED_CHARACTERS/);

const archive=JSON.parse(await fs.readFile('fixtures/mak-archive-sample.json','utf8'));
const archiveProject=importArchiveBundle(archive);
assert.equal(archiveProject.items[0].entityType,'work');
assert.equal(archiveProject.relations[0].type,'etiqueta');
assert.equal(validateProject(archiveProject).ok,true);
const parallel=importArchiveBundle({...archive,vinculos:[...archive.vinculos,{de:'campo-motor-diagnostico',a:'cenefa-dossier',peso:0.5,clase:'manual'}]});
assert.equal(parallel.relations.length,2,'parallel typed relations are not collapsed');
assert.notEqual(parallel.relations[0].id,parallel.relations[1].id);
const updatedRelation=importArchiveBundle({...archive,vinculos:[{de:'campo-motor-diagnostico',a:'cenefa-dossier',peso:0.9,clase:'etiqueta'}]},archiveProject);
assert.equal(updatedRelation.relations.find(x=>x.type==='etiqueta').weight,0.9,'typed relation updates without collapsing identity');
assert.equal(parseSourceDate('2026-02-31').valid,false);
assert.equal(parseSourceDate('2026').precision,'year');

const dossier=createEdition(archiveProject,'dossier',{title:'Dossier de archivo'}); const extended=createEdition(archiveProject,'extended',{title:'Portafolio extendido'});
dossier.items[0].selected=true; dossier.items[0].title='Lectura dossier'; extended.items[1].selected=true; extended.items[1].title='Lectura extendida';
assert.equal(dossier.origin.originId,extended.origin.originId,'editions share origin identity'); assert.notEqual(dossier.editionId,extended.editionId); assert.equal(extended.items[0].selected,false,'editions have independent editorial state');
const changedArchive={...archive,piezas:archive.piezas.map(x=>x.id==='vola'?({...x,titulo:'VOLÁ actualizado'}):x)};
const archiveMerged=importArchiveBundle(changedArchive,dossier); assert.equal(archiveMerged.conflicts.filter(c=>c.status==='open').length,1,'archive source changes open a conflict');
const kept=resolveConflict(archiveMerged,'vola','keep-edits'); assert.equal(kept.items.find(x=>x.id==='vola').title,'Lectura dossier');
const accepted=resolveConflict(archiveMerged,'vola','accept-source'); assert.equal(accepted.items.find(x=>x.id==='vola').title,'VOLÁ actualizado');

const tooMany={...dossier,items:[...dossier.items,...Array.from({length:6},(_,i)=>({...dossier.items[0],id:`extra-${i}`,source:{id:`extra-${i}`,sourceId:`extra-${i}`,raw:{}}}))],orderIds:[...dossier.orderIds,...Array.from({length:6},(_,i)=>`extra-${i}`)]};
assert.equal(exportPlan(tooMany,'dossier').diagnostics.length,0,'dossier accepts a page-bounded selection');
const impossible = await composeEdition(tooMany,{profile:'dossier',maxPages:1,allowedTemplates:['single']});
assert.equal(impossible.status,'INFEASIBLE');
await assert.rejects(() => writeExports(tooMany,'work/profile-fail',{profile:'dossier',maxPages:1,allowedTemplates:['single']}),/COMPOSITION_INFEASIBLE/);

const generated = importInbox({items:Array.from({length:10},(_,i)=>({id:`r${i}`}))}); generated.items.forEach(x=>{x.selected=true;x.title='A';x.description='B';});
const generated12 = await composeEdition(generated,{maxPages:12,timeLimitMs:2000}); const generated5 = await composeEdition(generated,{maxPages:5,timeLimitMs:2000}); const generatedSingle = await composeEdition(generated,{maxPages:12,allowedTemplates:['single'],timeLimitMs:2000});
assert.equal(generated12.status,'OPTIMAL'); assert.equal(generated5.status,'OPTIMAL'); assert.equal(generated12.pages.length,5,'numeric objective finds the measured five-page optimum'); assert.equal(generated5.pages.length,5,'maxPages=5 remains feasible at the same optimum'); assert.equal(generatedSingle.pages.length,10,'single-template constraint is respected'); assert.ok(generated5.pages.length <= generated12.pages.length);
const forged=JSON.parse(JSON.stringify(generated5)); forged.constraints.maxPages=0; forged.pages[0].items[1].box={...forged.pages[0].items[0].box}; assert.equal((await verifyComposition(generated,forged,{profile:'portfolio',constraints:{...generated5.constraints,maxPages:0}})).ok,false,'instance-bound verifier rejects forged limit and overlap');

const composed = await composeEdition(archiveProject,{profile:'portfolio',allowedTemplates:['single','split','stack'],alternativeCount:3});
assert.equal(composed.status,'OPTIMAL'); assert.equal(composed.selectedIds.length,0);
const composedSelected = createEdition(archiveProject,'composition',{title:'Composición'}); composedSelected.items.forEach(x => x.selected=true);
const composition = await composeEdition(composedSelected,{profile:'portfolio',alternativeCount:3,referenceEnumerate:true});
assert.equal(composition.status,'OPTIMAL'); assert.equal(composition.pages.flatMap(p=>p.items).length,3); assert.ok(composition.alternatives.length >= 2,'returns multiple deterministic alternatives'); assert.ok(composition.metrics.transitionsExplored > 0); assert.equal(composition.verification.ok,true); assert.equal(composition.referenceComparison.agreesOnBest,true);
const brokenComposition=JSON.parse(JSON.stringify(composition)); brokenComposition.pages[0].items[0].box.x=-1; assert.equal((await verifyComposition(composedSelected,brokenComposition,{profile:'portfolio',constraints:composition.constraints})).ok,false,'independent verifier rejects invalid geometry');
const forgedMeasurements=JSON.parse(JSON.stringify(composition)); forgedMeasurements.pages[0].items[0].measurements.textHeight+=7; assert.equal((await verifyComposition(composedSelected,forgedMeasurements,{profile:'portfolio',constraints:composition.constraints})).ok,false,'instance-bound verifier rejects forged text measurement');
const chosenAlternative={...composition,pages:composition.alternatives[1].pages,objective:composition.alternatives[1].objective}; const altExport=await writeExports(composedSelected,'work/alternative-export',{compositionOverride:chosenAlternative,selectedAlternative:1}); assert.equal(altExport.composition.status,'FEASIBLE'); assert.equal(altExport.composition.verification.ok,true);
const directMediaProject=createEdition(archiveProject,'direct-media',{title:'Exportación directa'}); directMediaProject.items[0].selected=true; const directMedia=await writeExports(directMediaProject,'work/direct-media-export',{roots:['fixtures'],resourceMap:{vola:'media/synthetic-poster.svg'}}); const directPdf=await pdfjs.getDocument({data:new Uint8Array(await fs.readFile(`${directMedia.base}.pdf`))}).promise; const directText=(await (await directPdf.getPage(1)).getTextContent()).items.map(x=>x.str).join(' '); assert.match(directText,/IRIS · POSTER SINTÉTICO/,'direct export embeds resolved SVG media');
const unknown = await composeEdition(composedSelected,{profile:'portfolio',timeLimitMs:0}); assert.equal(unknown.status,'UNKNOWN');
await assert.rejects(() => writeExports(composedSelected,'work/timeout-export',{timeLimitMs:0}),/COMPOSITION_UNKNOWN/);
const relationConflict = createEdition(archiveProject,'precedence'); relationConflict.items.forEach(x=>x.selected=true); relationConflict.precedence=[{before:'cenefa-dossier',after:'vola'}];
assert.equal((await composeEdition(relationConflict,{profile:'portfolio'})).status,'INFEASIBLE');

const changed=importInbox({...sample,items:sample.items.map(x=>x.id===curated.items[0].id?({...x,asset_available:false,unknown_field:'kept',descripcion_original:'Actualización de fuente'}):x)},curated);
assert.equal(changed.conflicts.filter(c=>c.status==='open').length,1);
assert.equal(changed.items.find(x=>x.id===curated.items[0].id).source.raw.unknown_field,'kept');
const repeated=importInbox({...sample,items:sample.items.map(x=>x.id===curated.items[0].id?({...x,asset_available:false}):x)},changed);
assert.equal(repeated.conflicts.filter(c=>c.status==='open').length,1,'open conflict remains stable on repeated import');
const partial=importInbox({schema:'faro-portfolio-inbox-v1',snapshotMode:'partial',items:[sample.items[0]]},curated);
assert.equal(partial.items.length,curated.items.length,'partial snapshot does not infer deletions');
assert.equal(partial.items.find(x=>x.id===curated.items[1].id).sourceState,'not_in_partial_snapshot');
const resolved=resolveConflict(changed,curated.items[0].id,'keep-edits');
assert.equal(resolved.conflicts.find(c=>c.itemId===curated.items[0].id).status,'resolved_keep_edits');
assert.throws(() => resolveConflict(changed,curated.items[0].id,'keep-edits', 'stale'),/STALE_REVISION/);

const packageResult=await writeExports(curated,'work/regression-package',{compose:false});
assert.equal(packageResult.files.length,4,'headless package contains PDF, JSON, HTML and ficha');
for (const file of packageResult.files) await fs.access(file);
const packageHtml=await fs.readFile(`${packageResult.base}.html`,'utf8'); const packageFicha=await fs.readFile(`${packageResult.base}-ficha.html`,'utf8');
assert.match(packageHtml,/Registro de prueba/); assert.match(packageFicha,/Ñandú/);

const portableDir='work/portable-regression'; await fs.rm(portableDir,{recursive:true,force:true}); const portableProject=createEdition(archiveProject,'portable',{title:'Paquete portátil'}); portableProject.items[0].selected=true;
const portable=await writePortablePackage(portableProject,portableDir,{roots:['fixtures'],resourceMap:{vola:'media/synthetic-poster.svg'},strictResources:true});
assert.ok(portable.files.some(x=>x.startsWith('media/'))); const manifest=JSON.parse(await fs.readFile(`${portableDir}/manifest.json`,'utf8')); const publicPlan=JSON.parse(await fs.readFile(`${portableDir}/plan.json`,'utf8')); assert.equal(manifest.complete,true); assert.equal(publicPlan.items[0].source.raw,undefined); assert.equal(publicPlan.composition.relations[0].raw,undefined); await fs.access(`${portableDir}/portfolio.pdf`); await fs.access(`${portableDir}/portfolio.html`); await fs.access(`${portableDir}/ficha.html`);
assert.match(await fs.readFile(`${portableDir}/portfolio.html`,'utf8'),/media\/vola-/);
const extracted=await pdfjs.getDocument({data:new Uint8Array(await fs.readFile(`${portableDir}/portfolio.pdf`))}).promise; const extractedText=(await (await extracted.getPage(1)).getTextContent()).items.map(x=>x.str).join(' '); assert.match(extractedText,/VOLÁ/,'independent PDF.js extraction sees composed text'); assert.match(extractedText,/IRIS · POSTER SINTÉTICO/,'SVG media is materialized as vector content in PDF');
const rasterPath='work/synthetic-1x1.png'; await fs.writeFile(rasterPath,Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=','base64')); const rasterProject=createEdition(archiveProject,'raster',{title:'Raster real'}); rasterProject.items[0].selected=true; const rasterDir='work/raster-package'; await fs.rm(rasterDir,{recursive:true,force:true}); const rasterPackage=await writePortablePackage(rasterProject,rasterDir,{roots:['work'],resourceMap:{vola:'synthetic-1x1.png'},strictResources:true}); const rasterPdf=await fs.readFile(`${rasterDir}/portfolio.pdf`); assert.match(rasterPdf.toString('latin1'),/XObject/,'PDF embeds supported raster resource'); assert.ok(rasterPackage.files.some(x=>x.endsWith('.png')));
await fs.rm('work/portable-missing',{recursive:true,force:true}); const missingProject=createEdition(archiveProject,'missing',{title:'Paquete incompleto'}); missingProject.items[0].selected=true; await assert.rejects(() => writePortablePackage(missingProject,'work/portable-missing',{roots:['work'],strictResources:true}),/RESOURCE_DIAGNOSTICS/);

console.log('IRIS regression checks passed: origen real, dos ediciones, conflictos, perfiles, relaciones paralelas, fechas, Unicode/texto largo, paquete portable y PDF.');
