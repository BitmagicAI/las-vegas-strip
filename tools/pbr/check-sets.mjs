// Lists which scanned material (src/work/PbrDetailSets.ts) every exterior runtime material gets.
// node --import ./tools/ts-register.mjs tools/pbr/check-sets.mjs
import fs from 'node:fs';import path from 'node:path';
import {detailSetFor,PBR_SETS} from '../../src/work/PbrDetailSets.ts';
const skip=/interior|lobby|\/hotels\/|\/interiors\/|vehicles|foliage|character|uthana/i,by=new Map();
function walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);if(e.isDirectory())walk(p);else if(p.endsWith('.glb')&&!skip.test(p)){
    const b=fs.readFileSync(p),L=b.readUInt32LE(12),j=JSON.parse(b.subarray(20,20+L).toString());
    for(const m of j.materials??[]){const s=detailSetFor(m.name??''),k=s<0?'(none)':PBR_SETS[s];if(!by.has(k))by.set(k,new Set());by.get(k).add(m.name);}}}}
walk('build/optimized');
for(const [k,v] of [...by].sort())console.log(`${k} (${v.size}): ${[...v].sort().join(' | ')}\n`);
