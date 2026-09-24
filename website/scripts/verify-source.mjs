import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';
const manifest = JSON.parse(readFileSync(new URL('../threeui-source.json', import.meta.url)));
for (const file of manifest.files) {
 const bytes = readFileSync(new URL('../'+file.path, import.meta.url));
 assert.equal(createHash('sha256').update(bytes).digest('hex'), file.sha256, file.path+' must remain exact');
}
const data = JSON.parse(readFileSync(new URL('../src/data/study.json', import.meta.url)));
assert.equal(data.detection.length,42); assert.equal(data.xai.length,28);
assert.equal(data.figures.length,41); assert.equal(data.llm.length,24);
for (const rows of Object.values(data.audit)) assert.equal(rows.length,483);
assert.equal(data.detection.reduce((n,r)=>n+r.n_seeds,0),126);
console.log('Verified all four exact ThreeUI source hashes and website evidence inventory.');

for (const [path,hash] of Object.entries(data.provenance.inputs)) {
 const bytes=readFileSync(new URL('../../'+path,import.meta.url));
 assert.equal(createHash('sha256').update(bytes).digest('hex'),hash,'Research input changed: '+path);
}
console.log('Frozen research input hashes match the website dataset.');

for (const figure of data.figures) {
 const exported=readFileSync(new URL('../public/'+figure.path,import.meta.url));
 const original=readFileSync(new URL('../../'+figure.source,import.meta.url));
 assert.equal(createHash('sha256').update(exported).digest('hex'),createHash('sha256').update(original).digest('hex'),'Figure copy mismatch: '+figure.number);
}
const pdf=readFileSync(new URL('../public/thesis.pdf',import.meta.url));
const report=readFileSync(new URL('../../output/pdf/thesis_xai_ids_preserved.pdf',import.meta.url));
assert.equal(createHash('sha256').update(pdf).digest('hex'),createHash('sha256').update(report).digest('hex'),'PDF copy mismatch');
const fontManifest=JSON.parse(readFileSync(new URL('../font-sources.json',import.meta.url)));
for (const font of fontManifest.files) assert.equal(createHash('sha256').update(readFileSync(new URL('../'+font.file,import.meta.url))).digest('hex'),font.sha256,font.file);
console.log('All 41 original figure copies, report PDF and self-hosted font hashes match.');
