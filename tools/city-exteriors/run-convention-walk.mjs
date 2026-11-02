// Keep each continuous forward/reverse circuit below probe-eval's ten-minute watchdog.
import fs from 'node:fs';import {spawnSync} from 'node:child_process';import assert from 'node:assert/strict';
const source=fs.readFileSync('tools/city-exteriors/walk-convention-refinement.js','utf8'),start=source.indexOf('const meta='),end=source.indexOf('const waitReady=');
const {routes}=JSON.parse(source.slice(start+11,end).trim().replace(/;$/,''));
const root='build/city-exteriors/convention-walk-scripts';fs.mkdirSync(root,{recursive:true});const results=[];
for(let i=0;i<routes.length;i++){
 const file=`${root}/${i}.js`,out=`build/city-exteriors/convention-walk-${i}`;
 fs.writeFileSync(file,source.slice(0,start)+`const meta=${JSON.stringify({routes:[routes[i]]})};\n`+source.slice(end));
 const process=spawnSync('node',['tools/probe-eval.mjs',file,'--out',out],{stdio:'inherit'});assert.equal(process.status,0);
 const result=JSON.parse(fs.readFileSync(`${out}/results.json`));assert.equal(result.passed,true,routes[i].name);results.push(result);
}
fs.writeFileSync('docs/project-records/convention-area-refinement/walk.json',JSON.stringify({passed:true,circuits:results},null,2)+'\n');
