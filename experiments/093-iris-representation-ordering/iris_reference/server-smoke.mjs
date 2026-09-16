import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import net from 'node:net';

const port = await new Promise((resolve, reject) => { const probe = net.createServer(); probe.once('error', reject); probe.listen(0, '127.0.0.1', () => { const address = probe.address(); probe.close(() => resolve(address.port)); }); });
const base = `http://127.0.0.1:${port}`;
const child = spawn(process.execPath, ['server.mjs'], { env: { ...process.env, IRIS_PORT: String(port) }, stdio: 'ignore' });
async function waitForServer() {
  for (let attempt = 0; attempt < 50; attempt++) {
    try { const response = await fetch(`${base}/`); if (response.ok) return; } catch {}
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error('El servidor no inició dentro del tiempo esperado.');
}
try {
  await waitForServer();
  const page = await fetch(`${base}/`);
  assert.equal(page.status, 200);
  assert.match(page.headers.get('content-type') || '', /text\/html/);
  const project = await fs.readFile('demo-project.json', 'utf8');
  const exportResponse = await fetch(`${base}/api/export`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ project: JSON.parse(project), profile: 'portfolio' }) });
  assert.equal(exportResponse.status, 200);
  const exported = await exportResponse.json();
  assert.equal(exported.ok, true);
  assert.equal(exported.files.length, 4);
  assert.equal(exported.urls.length, 4);
  const output = await fetch(`${base}${exported.urls[0]}`);
  assert.equal(output.status, 200);
  const oversized = await fetch(`${base}/api/import`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: 'x'.repeat(10 * 1024 * 1024 + 1) });
  assert.equal(oversized.status, 413);
  console.log('IRIS server smoke passed: static page, export URLs, output retrieval and payload limit.');
} finally {
  child.kill();
}
