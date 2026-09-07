import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { composeEdition, exportPlan, importArchiveBundle, importInbox, normalizeProject, resolveConflict, validateProject, writeExports } from './engine.mjs';

const root = path.dirname(fileURLToPath(import.meta.url)); const outputs = path.join(root, 'outputs'); const demo = path.join(root, 'demo-project.json'); const sample = path.join(root, 'fixtures', 'mak-inbox-sample.json'); const archiveSample = path.join(root, 'fixtures', 'mak-archive-sample.json'); const port = Number(process.env.IRIS_PORT || 4173);
const mime = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.pdf':'application/pdf','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp'};
async function send(res,status,type,body){res.writeHead(status,{'Content-Type':type,'Cache-Control':'no-store'});res.end(body)}
const MAX_JSON_BYTES = 10 * 1024 * 1024;
async function readJson(req){let raw='';for await(const chunk of req){raw+=chunk;if(Buffer.byteLength(raw,'utf8')>MAX_JSON_BYTES){const error=new Error('El JSON supera el límite de 10 MB');error.statusCode=413;throw error;}}try{return JSON.parse(raw)}catch{throw new Error('JSON inválido')}}
const errorStatus=(error,fallback)=>error?.statusCode||fallback;
async function handler(req,res){
  const url=new URL(req.url,'http://localhost');
  if(req.method==='GET' && url.pathname==='/api/demo') return send(res,200,mime['.json'],await fs.readFile(demo,'utf8'));
  if(req.method==='GET' && url.pathname==='/api/contract-sample') return send(res,200,mime['.json'],await fs.readFile(sample,'utf8'));
  if(req.method==='GET' && url.pathname==='/api/archive-sample') return send(res,200,mime['.json'],await fs.readFile(archiveSample,'utf8'));
  if(req.method==='POST' && url.pathname==='/api/import') { try { const body=await readJson(req); const project=importInbox(body.source || body, body.existing || null); return send(res,200,mime['.json'],JSON.stringify(project)); } catch(e) { return send(res,errorStatus(e,400),mime['.json'],JSON.stringify({ok:false,error:e.message})); } }
  if(req.method==='POST' && url.pathname==='/api/import-archive') { try { const body=await readJson(req); const project=importArchiveBundle(body.source || body, body.existing || null); return send(res,200,mime['.json'],JSON.stringify(project)); } catch(e) { return send(res,errorStatus(e,400),mime['.json'],JSON.stringify({ok:false,error:e.message})); } }
  if(req.method==='POST' && url.pathname==='/api/validate') { try { const result=validateProject(await readJson(req)); return send(res,result.ok?200:422,mime['.json'],JSON.stringify(result)); } catch(e) { return send(res,errorStatus(e,400),mime['.json'],JSON.stringify({ok:false,error:e.message})); } }
  if(req.method==='POST' && url.pathname==='/api/resolve') { try { const body=await readJson(req); const project=resolveConflict(body.project,body.itemId,body.decision,body.expectedRevision); return send(res,200,mime['.json'],JSON.stringify(project)); } catch(e) { return send(res,errorStatus(e,409),mime['.json'],JSON.stringify({ok:false,error:e.message})); } }
  if(req.method==='POST' && url.pathname==='/api/compose') { try { const body=await readJson(req); const result=await composeEdition(body.project || body,{profile:body.profile || 'portfolio',maxPages:body.maxPages,allowedTemplates:body.allowedTemplates,timeLimitMs:body.timeLimitMs,alternativeCount:body.alternativeCount}); return send(res,result.status==='INFEASIBLE'?422:200,mime['.json'],JSON.stringify(result)); } catch(e) { return send(res,errorStatus(e,422),mime['.json'],JSON.stringify({ok:false,error:e.message})); } }
  if(req.method==='POST' && url.pathname==='/api/export'){
    try { const body=await readJson(req); const result=await writeExports(body.project || body,outputs,{profile:body.profile || 'portfolio',compose:body.compose,maxPages:body.maxPages,allowedTemplates:body.allowedTemplates,timeLimitMs:body.timeLimitMs,alternativeCount:body.alternativeCount,compositionOverride:body.compositionOverride,selectedAlternative:body.selectedAlternative}); const files=result.files.map(file=>path.basename(file)); return send(res,200,mime['.json'],JSON.stringify({ok:true,plan:result.plan,composition:result.composition,files,urls:files.map(file=>`/outputs/${encodeURIComponent(file)}`)})); }
    catch(e) { return send(res,errorStatus(e,422),mime['.json'],JSON.stringify({ok:false,error:e.message})); }
  }
  let pathname; try { pathname = decodeURIComponent(url.pathname); } catch { return send(res,400,'text/plain','Bad request'); } let p=pathname==='/'?'/index.html':pathname; const file=path.resolve(root, `.${p}`); if(file !== root && !file.startsWith(`${root}${path.sep}`)) return send(res,403,'text/plain','Forbidden');
  try{return send(res,200,mime[path.extname(file)]||'text/plain',await fs.readFile(file))}catch{return send(res,404,'text/plain','Not found')}
}
http.createServer(handler).listen(port,()=>console.log(`IRIS listo en http://localhost:${port}`));
