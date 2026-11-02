// Replay retained pre-pass Platinum asset/metadata in the browser only; never swap live files.
import fs from 'node:fs';import {spawnSync} from 'node:child_process';import assert from 'node:assert/strict';
const baseline=process.argv.includes('--baseline');
let source=fs.readFileSync('tools/probe-eval.mjs','utf8').replaceAll("'./lib/bitmagic-cli.mjs'","'./tools/lib/bitmagic-cli.mjs'");
if(baseline){
 source=source.replace('  await page.goto(',`  let baselineModelHits=0,baselineMetadataHits=0;
  await page.route('**/*platinum-exterior.glb*',route=>{baselineModelHits++;return route.fulfill({body:fs.readFileSync('.bitmagic/city-exterior-backups/westin-platinum-amenities/platinum-exterior.glb'),contentType:'model/gltf-binary'});});
  await page.route('**/strip-landmarks/venues.bin*',route=>{baselineMetadataHits++;return route.fulfill({body:fs.readFileSync('.bitmagic/city-exterior-backups/westin-platinum-amenities/venues-before.bin'),contentType:'application/octet-stream'});});
  await page.goto(`);
 source=source.replace('  fs.writeFileSync(`${outDir}/results.json`',"  if(!baselineModelHits||!baselineMetadataHits)throw new Error('Baseline overrides not used');\n  fs.writeFileSync(`${outDir}/results.json`");
}
const out='build/city-exteriors/platinum-pool-interior-'+(baseline?'baseline':'preview');
const r=spawnSync(process.execPath,['--input-type=module','-','tools/city-exteriors/probe-platinum-pool-interior.js','--out',out],{input:source,stdio:['pipe','inherit','inherit']});assert.equal(r.status,0);
