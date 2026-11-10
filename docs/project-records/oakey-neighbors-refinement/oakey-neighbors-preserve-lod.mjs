import fs from 'node:fs';
import assert from 'node:assert/strict';
import {readBlocks,encodeBlocks,writeLodCells} from '/Users/janisun/Development/GitFork/vegas-2601-westwood/tools/city-cells/lod-files.mjs';
const key=b=>JSON.stringify([b.part,b.key]), old=new Map(), report=[];
for(const f of fs.readdirSync('/tmp/oakey-neighbors-base-cells').filter(f=>f.endsWith('.bin')))for(const b of readBlocks(fs.readFileSync('/tmp/oakey-neighbors-base-cells/'+f)))old.set(key(b),b);
const blocks=readBlocks(fs.readFileSync('build/baked/city-lod.bin')).map(b=>{
 const prev=old.get(key(b));if(!prev){assert.ok(['peppermintHippo','oakeyService','courtyard525'].includes(b.key),'Unexpected new block '+key(b));report.push({part:b.part,key:b.key,added:true});return b;}
 if(prev.bytes.equals(b.bytes))return b;
 const restore=/goldCoastExterior|wyndhamDesertBlue/.test(b.key);
 assert.ok(restore||['peppermintHippo','oakeyService','courtyard525'].includes(b.key),'Unexpected changed block '+key(b));
 report.push({part:b.part,key:b.key,before:prev.bytes.length,after:b.bytes.length,restored:restore});return restore?prev:b;
});
fs.writeFileSync('build/baked/city-lod.bin',encodeBlocks(blocks));
writeLodCells('build/baked/city-lod.bin','build/baked/cells','OpenStreetMap / geographic Strip','.bitmagic/bake/raw');
fs.writeFileSync('docs/project-records/oakey-neighbors-refinement/lod-preservation.json',JSON.stringify(report,null,2)+'\n');console.log(report);
