// Compare retained pre-pass near models with installed candidates, sequentially.
// Both arms use identical current distant cells, camera scripts and venue metadata.
import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
import assert from 'node:assert/strict';
const pairs=[['wells','wellsFargoTower'],['park-towers','parkTowers'],['residence-inn','residenceInnHughes']];
for(const [name,key] of pairs.filter(p=>!process.argv[2]||p[0]===process.argv[2]))for(const arm of ['baseline','candidate']){
 let source=fs.readFileSync('tools/probe-eval.mjs','utf8').replaceAll("'./lib/bitmagic-cli.mjs'","'./tools/lib/bitmagic-cli.mjs'");
 if(arm==='baseline'){
  source=source.replace('  await page.goto(',`  const assetHits=new Set();
  for(const key of ${JSON.stringify(pairs.map(p=>p[1]))})await page.route('**/*'+key+'-exterior.glb*',route=>{assetHits.add(key);return route.fulfill({body:fs.readFileSync('.bitmagic/city-exterior-backups/hughes-center-amenities/'+key+'-exterior.glb'),contentType:'model/gltf-binary'});});
  await page.goto(`);
  source=source.replace('  fs.writeFileSync(`${outDir}/results.json`',`  if(!assetHits.has(${JSON.stringify(key)}))throw new Error('Baseline asset not intercepted');
  fs.writeFileSync(outDir+'/baseline-intercepts.json',JSON.stringify([...assetHits]));
  fs.writeFileSync(\`\${outDir}/results.json\``);
 }
 const result=spawnSync(process.execPath,['--input-type=module','-','tools/city-exteriors/probe-'+name+'-amenities.js','--out','build/city-exteriors/'+name+'-hughes-ab-'+arm],{input:source,stdio:['pipe','inherit','inherit']});
 assert.equal(result.status,0,name+' '+arm);
}
