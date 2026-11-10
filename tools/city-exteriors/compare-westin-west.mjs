// Sequential same-session comparison, without modifying installed assets or other apps.
// Baseline replays retained pre-pass GLBs and venue metadata; baked distant cells stay identical in both arms.
import fs from 'node:fs';import {spawnSync} from 'node:child_process';import assert from 'node:assert/strict';
for(const key of ['westin'])for(const arm of ['baseline','candidate']){
 let source=fs.readFileSync('tools/probe-eval.mjs','utf8').replaceAll("'./lib/bitmagic-cli.mjs'","'./tools/lib/bitmagic-cli.mjs'");
 if(arm==='baseline'){
 source=source.replace('  await page.goto(',`  let assetHits=0,metadataHits=0;
  for(const key of ['westin','platinum'])await page.route('**/*'+key+'-exterior.glb*',route=>{assetHits++;return route.fulfill({body:fs.readFileSync('.bitmagic/city-exterior-backups/westin-platinum-amenities/'+key+'-exterior.glb'),contentType:'model/gltf-binary'});});
  await page.route('**/strip-landmarks/venues.bin*',route=>{metadataHits++;return route.fulfill({body:fs.readFileSync('.bitmagic/city-exterior-backups/westin-platinum-amenities/venues-before.bin'),contentType:'application/octet-stream'});});
  await page.goto(`);
 source=source.replace('  fs.writeFileSync(`${outDir}/results.json`',"  if(!assetHits||!metadataHits)throw new Error('Baseline not applied');\n  fs.writeFileSync(`${outDir}/results.json`");
 }
 const r=spawnSync(process.execPath,['--input-type=module','-','tools/city-exteriors/diagnose-westin-west.js','--out','build/city-exteriors/'+key+'-west-ablation-'+arm],{input:source,stdio:['pipe','inherit','inherit']});assert.equal(r.status,0);
}
