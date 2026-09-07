'use strict';

// Rebuild local PDF derivatives from the consolidated Markdown sources.
// Python and Playwright must already be installed. This script installs nothing.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { spawnSync } = require('node:child_process');
const { chromium } = require(process.env.SUBMISSION_PLAYWRIGHT_PATH || 'playwright');

const root = path.resolve(__dirname, '../../..');
const packageDir = path.join(root, 'output/postulacion_dimensiones_del_orden_2027');
const python = process.env.SUBMISSION_PYTHON || 'python';
const renderer = path.join(__dirname, 'render_markdown_pdf.py');
const documents = [
  ['06_treatment_rewrite.md', 'submission_treatment', 'Dimensiones del Orden'],
  ['02_experimental_method.md', 'submission_experimental_method', 'Metodologia experimental'],
  ['16_budget_form_reconciled_draft.md', 'submission_budget_reconciled', 'Presupuesto de trabajo'],
  ['04_budget_audit.md', 'submission_budget_audit', 'Presupuesto: antecedente historico'],
];
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');

async function main() {
  const browser = await chromium.launch({ headless: true });
  const manifest = [];
  try {
    const page = await browser.newPage();
    for (const [sourceName, stem, title] of documents) {
      const source = path.join(packageDir, sourceName);
      const sourceHash = hash(source);
      const html = path.join(packageDir, stem + '.html');
      const pdf = path.join(packageDir, stem + '.pdf');
      const generated = spawnSync(python, [renderer, source, html, '--title', title], { encoding: 'utf8' });
      if (generated.error || generated.status !== 0) {
        throw new Error('HTML generation failed: ' + sourceName + '\n' + (generated.error || generated.stderr));
      }
      await page.setContent(fs.readFileSync(html, 'utf8'), { waitUntil: 'load' });
      await page.pdf({ path: pdf, format: 'A4', printBackground: true, preferCSSPageSize: true });
      if (hash(source) !== sourceHash) throw new Error('Source changed during rendering: ' + sourceName);
      manifest.push({ source: sourceName, source_sha256: sourceHash, pdf: stem + '.pdf', pdf_sha256: hash(pdf) });
      process.stdout.write('RENDERED ' + stem + '.pdf\n');
    }
    fs.writeFileSync(path.join(packageDir, 'render_manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  } finally {
    await browser.close();
  }
}

main().catch(error => { process.stderr.write(String(error) + '\n'); process.exitCode = 1; });
