import fs from 'node:fs/promises';
import path from 'node:path';
import { composeEdition, createEdition, importArchiveBundle, importInbox, normalizeProject, orderBy, resolveConflict, validateProject, writeExports, writePortablePackage } from './engine.mjs';

const args = process.argv.slice(2); const command = args[0];
const value = name => { const i=args.indexOf(name); return i>=0 ? args[i+1] : null; };
const required = name => value(name) || (()=>{ throw new Error(`Falta ${name}`); })();
const atomicWrite = async (file, content) => { const temp = `${file}.tmp-${process.pid}`; await fs.writeFile(temp, content, 'utf8'); await fs.rename(temp, file); };
if (!['import','export','validate','resolve','edition','package','compose'].includes(command)) { console.error('Uso: node iris-cli.mjs import|export|validate|resolve|edition|package|compose ...'); process.exit(2); }
try {
  if (command === 'import') {
    const source = JSON.parse(await fs.readFile(required('--source'),'utf8')); const existingPath=value('--existing'); const existing=existingPath?JSON.parse(await fs.readFile(existingPath,'utf8')):null; const project=source.piezas?importArchiveBundle(source,existing):importInbox(source,existing); await atomicWrite(required('--out'),JSON.stringify(project,null,2)); console.log(JSON.stringify({ok:true,items:project.items.length,errors:project.importErrors||[]}));
  } else if (command === 'validate') {
    const result=validateProject(JSON.parse(await fs.readFile(required('--state'),'utf8'))); console.log(JSON.stringify(result,null,2)); if(!result.ok)process.exit(1);
  } else if (command === 'resolve') {
    const file=required('--state'); const current=JSON.parse(await fs.readFile(file,'utf8')); const project=resolveConflict(current,required('--id'),required('--decision'),value('--expected-revision')); await atomicWrite(file,JSON.stringify(project,null,2)); console.log(JSON.stringify({ok:true,revision:project.revision}));
  } else if (command === 'edition') {
    const input=JSON.parse(await fs.readFile(required('--state'),'utf8')); const edition=createEdition(input,required('--id'),{title:value('--title')}); await atomicWrite(required('--out'),JSON.stringify(edition,null,2)); console.log(JSON.stringify({ok:true,editionId:edition.editionId,originId:edition.origin.originId}));
  } else if (command === 'package') {
    const input=JSON.parse(await fs.readFile(required('--state'),'utf8')); const resourceMapPath=value('--resource-map'); const resourceMap=resourceMapPath?JSON.parse(await fs.readFile(resourceMapPath,'utf8')):{}; const options={profile:value('--profile')||'portfolio',roots:value('--root')?[path.resolve(value('--root'))]:[],resourceMap,strictResources:args.includes('--strict-resources')}; const result=await writePortablePackage(input,path.resolve(required('--out')),options); console.log(JSON.stringify({ok:true,packageDir:result.packageDir,files:result.files,diagnostics:result.diagnostics}));
  } else if (command === 'compose') {
    const input=JSON.parse(await fs.readFile(required('--state'),'utf8')); const options={profile:value('--profile')||'portfolio',maxPages:value('--max-pages')?Number(value('--max-pages')):undefined,allowedTemplates:value('--templates')?value('--templates').split(',').filter(Boolean):undefined,timeLimitMs:value('--time-limit-ms')?Number(value('--time-limit-ms')):undefined,alternativeCount:value('--alternatives')?Number(value('--alternatives')):3}; const result=await composeEdition(input,options); const output=JSON.stringify(result,null,2); if(value('--out')) await atomicWrite(path.resolve(value('--out')),output); else console.log(output);
  } else {
    const input=JSON.parse(await fs.readFile(required('--state'),'utf8')); const ordered=value('--dimension')?orderBy(input,value('--dimension')):input; const out=await writeExports(ordered,path.resolve(required('--out')),{profile:value('--profile')||'portfolio'}); await atomicWrite(path.join(path.dirname(out.base),path.basename(out.base)+'-plan.json'),JSON.stringify(out.plan,null,2)); console.log(JSON.stringify({ok:true,files:out.files,plan:out.plan.items.length}));
  }
} catch (error) { console.error(error.message); process.exit(1); }
